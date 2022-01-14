from django.test import TestCase, Client
from django.urls import reverse, resolve
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from user.models import  User
from chat.models import DialogsModel, MessageModel
from chat.serializers import serialize_message_model, serialize_file_model, serialize_dialog_models
import json
from .factories import DialogsModelFactory, MessageModelFactory, UserFactory, faker



class ViewTests(TestCase):
    def setUp(self):
        self.client1 = Client()
        self.client2 = Client()
        self.user1 = User.objects.create_user(username = 'user1', email = 'test@example.com', password = 'top_secret')
        self.user2 = User.objects.create_user(username='user2', email='test2@example.com', password='top_secret2')
        self.client1.force_login(self.user1)
        self.client2.force_login(self.user2)





