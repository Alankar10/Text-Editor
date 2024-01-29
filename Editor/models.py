from django.db import models
from django.contrib.auth.models import User

class Document(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_documents')
    editors = models.ManyToManyField(User, related_name='editable_documents', blank=True)
    viewers = models.ManyToManyField(User, related_name='viewable_documents', blank=True)
