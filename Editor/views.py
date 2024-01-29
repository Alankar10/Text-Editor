import os
from datetime import datetime
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from djangoProject3 import settings
from .form import TextFileForm, InvitationForm
from .models import Document

def home(request):
    return render(request, 'home.html', {'home': home})

def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if User.objects.filter(username=username):
            messages.error(request, "Username Already Exist")
            return redirect("signup")

        if len(username) > 10:
            messages.error(request, "Username must under 10 characters")
            return redirect("signup")

        if not username.isalnum():
            messages.error(request, "Usernames can contain letters (a-z), numbers (0-9) only")
            return redirect("signup")

        if User.objects.filter(email=email):
            messages.error(request, "Email Already Registered")
            return redirect("signup")

        if len(password1) < 8 or not any(c.isalpha() for c in password1) or not any(
                c.isdigit() for c in password1) or not any(not c.isalnum() for c in password1):
            messages.error(request,"Password should contain a combination of at least 8 characters, including letters (a-z), numbers (0-9) and special symbols.")
            return redirect("signup")

        if password1 != password2:
            messages.error(request, "Passwords didn't match")
            return redirect("signup")

        myuser = User.objects.create_user(username, email, password1)
        myuser.first_name = fname
        myuser.last_name = lname

        myuser.save()

        messages.success(request, "Your account has been successfully created.")

        subject = "Welcome to Editor!!"
        message = "Hello " + myuser.first_name + "!!\n" + "Welcome to Editor\n Thank you for visiting our website."
        from_email = settings.EMAIL_HOST_USER
        to_list = [myuser.email]
        send_mail(subject, message, from_email, to_list, fail_silently=True)

        return redirect('signin')

    return render(request, "signup.html")

def signin(request):
    if request.method == "POST":
        username = request.POST['username']
        password1 = request.POST['password1']

        user = authenticate(username=username, password=password1)

        if user is not None:
            login(request, user)
            fname = user.first_name
            return render(request, "home.html", {'fname': fname})

        else:
            messages.error(request, "Wrong Username or Passward")
            return redirect('home')

    return render(request, "signin.html")

def signout(request):
    logout(request)
    messages.success(request, "Logged Out Successfully")
    return redirect('home')

def create_text_file(request):
    if request.method == 'POST':
        form = TextFileForm(request.POST)
        if form.is_valid():
            file_name = form.cleaned_data['file_name']
            form_content = form.cleaned_data['file_content']

            # Ensure the file name is unique
            if file_name_exists(file_name):
                messages.error(request, f"The file name '{file_name}' is already taken. Please choose a different name.")
                return render(request, 'create_text_file.html', {'form': form})

            # Generate a unique filename based on the current timestamp
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            filename = f"{file_name}.txt"

            # Create the text file
            with open(filename, "w") as file:
                file.write(form_content)

            return redirect('view_text_files')  # Redirect to the list of text files
    else:
        form = TextFileForm()

    return render(request, 'create_text_file.html', {'form': form})

def file_name_exists(file_name):
    # Check if the file name already exists in the current directory
    return any(f.startswith(file_name) and f.endswith('.txt') for f in os.listdir('.'))

def view_text_files(request):
    file_name = request.GET.get('file_name')

    files = get_text_files_list(file_name)

    return render(request, 'view_text_files.html', {'files': files, 'file_name': file_name})

def view_text_file(request, filename):
    try:
        with open(filename, "r") as file:
            file_content = file.read()

        file_name = filename.split('.')[0]

        return render(request, 'view_text_file.html',
                      {'file_content': file_content, 'file_name': file_name, 'filename': filename})
    except FileNotFoundError:
        return HttpResponse("Text file not found.")

def edit_text_file(request, filename):
    try:
        with open(filename, "r") as file:
            file_content = file.read()
            return render(request, 'edit_text_file.html', {'file_content': file_content, 'filename': filename})
    except FileNotFoundError:
        return HttpResponse("Text file not found.")

def save_text_file(request):
    if request.method == 'POST':
        file_name = request.POST.get('file_name')
        form_content = request.POST.get('file_content')

        # Save the text file
        with open(file_name, "w") as file:
            file.write(form_content)

        # Notify connected clients about the changes
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'text_files',
            {
                'type': 'file.changed',
                'message': 'File changed',
            }
        )

        return redirect('view_text_files')
    else:
        # Handle the GET request as needed
        pass

def delete_text_file(request, filename):
    try:
        os.remove(filename)
        return redirect('view_text_files')
    except FileNotFoundError:
        return HttpResponse("Text file not found.")

def get_text_files_list(file_name=None):
    return [f for f in os.listdir('.') if f.endswith('.txt')]

def view_document(request, document_id):
    document = get_object_or_404(Document, id=document_id)

    # Check if the user has access to view/edit the document
    if request.user == document.created_by or request.user in document.editors.all() or request.user in document.viewers.all():
        return render(request, 'view_document.html', {'document': document})
    else:
        return render(request, 'access_denied.html')

def invite_user(request, document_id):
    document = get_object_or_404(Document, id=document_id)

    # Check if the user has permission to invite users
    if request.user == document.created_by:
        if request.method == 'POST':
            form = InvitationForm(request.POST)
            if form.is_valid():
                invited_user = form.cleaned_data['invited_user']
                document.editors.add(invited_user)
                return redirect('view_document', document_id=document.id)
        else:
            form = InvitationForm()

        return render(request, 'invite_user.html', {'form': form, 'document': document})
    else:
        return render(request, 'access_denied.html')