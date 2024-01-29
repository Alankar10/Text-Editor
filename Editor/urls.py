from django.urls import path
from . import views
from django.contrib.auth import views as auth_view

urlpatterns = [
	path('', views.home, name='home'),
	path('signup',views.signup, name="signup"),
    path('signin',views.signin, name="signin"),
    path('signout',views.signout, name="signout"),
    path('password_reset/', auth_view.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_view.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_view.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_view.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('accounts/login/',views.signin, name="accounts/login/"),
    path('create_text_file/', views.create_text_file, name='create_text_file'),
    path('view_text_files/', views.view_text_files, name='view_text_files'),
    path('view_text_file/<str:filename>/', views.view_text_file, name='view_text_file'),
    path('edit_text_file/<str:filename>/', views.edit_text_file, name='edit_text_file'),
    path('save_text_file/<str:filename>/', views.save_text_file, name='save_text_file'),
    path('delete_text_file/<str:filename>/', views.delete_text_file, name='delete_text_file'),
    path('document/<int:document_id>/', views.view_document, name='view_document'),
    path('document/<int:document_id>/invite/', views.invite_user, name='invite_user'),
]
