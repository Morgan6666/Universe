from django.test import TestCase, Client
from universeSocial.user import  User
from universeSocial.chat.models import DialogsModel, MessageModel


class ViewTests(TestCase):
    def setUp(self):
        self.client1 = Client()
        self.client2 = Client()
        self.user1 = User.objects.create_user(username = 'user1', email = 'test@example.com', password = 'top_secret')
        self.user2 = User.objects.create_user(username='user2', email='test2@example.com', password='top_secret2')
        self.client1.force_login(self.user1)
        self.client2.force_login(self.user2)





