from django import forms
from django.contrib.auth.models import User

class TextFileForm(forms.Form):
    file_name = forms.CharField(max_length=255, label='File Name')
    file_content = forms.CharField(widget=forms.Textarea, label='File Content')

class InvitationForm(forms.Form):
    invited_user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label='Invite User',
        help_text='Select a user to invite to edit the document.'
    )
