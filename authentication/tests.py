from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class AuthenticationTest(TestCase):
    databases = {'default'}
    def setUp(self):
        self.login_url = reverse('login')
        self.signup_url = reverse('signup')
        self.logout_url = reverse('logout')
        self.home_url = reverse('home')

        self.user= {
            'username': 'testuser',
            'email': 'test@gmail.com',
            'pass1': 'testpassword',
            'pass2': 'testpassword'
        }
        self.user_short_password = {
            'username': 'testuser',
            'email': 'test@gmail.com',
            'pass1': 'test',
            'pass2': 'test'
        }
        self.user_unmatching_password = {
            'username': 'testuser',
            'email': 'test@gmail.com',
            'pass1': 'testpassword',
            'pass2': 'testpassword2'
        }
        return super().setUp()
                                             
    def test_signup_with_valid_data(self):
        response = self.client.post(self.signup_url, self.user, format='text/html')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().username, 'testuser')
        self.assertEqual(User.objects.first().email, 'test@gmail.com')
        
    def test_signup_with_short_password(self):
        response = self.client.post(self.signup_url, self.user_short_password, format='text/html')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.count(), 0)
        self.assertRedirects(response, self.signup_url)
        


    def test_signup_with_unmatching_password(self):
        response = self.client.post(self.signup_url, self.user_unmatching_password, format='text/html')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.count(), 0)
        self.assertRedirects(response, self.signup_url)

    def test_login_with_valid_data(self):
        self.client.post(self.signup_url, self.user, format='text/html')
        response = self.client.post(self.login_url, {'email': 'test@gmail.com', 'password': 'testpassword'}, format='text/html')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first().username, 'testuser')
        self.assertEqual(User.objects.first().email, 'test@gmail.com')


    def test_login_with_invalid_data(self):
        self.client.post(self.signup_url, self.user, format='text/html')
        response = self.client.post(self.login_url, {'email': 'wrong@email.com', 'password': 'wrongpassword'}, format='text/html')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)

    def test_logout(self):
        self.client.post(self.signup_url, self.user, format='text/html')
        self.client.post(self.login_url, {'email': 'test@gmail.com', 'password': 'testpassword'}, format='text/html')
        response = self.client.get(self.logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)

    