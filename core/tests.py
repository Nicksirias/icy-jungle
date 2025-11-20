# make sure you have an env file locally before running (DO NOT COMMIT THE env. FILE!!!)

from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch

class AuthEventTests(TestCase):
	def setUp(self):
		self.client = Client()
		self.signin_url = reverse('signin')
		self.logout_url = reverse('logout')
		self.host_event_url = reverse('host_event')
		self.home_url = reverse('home')

	@patch('core.views._sb')
	def test_signup_success(self, mock_sb):
		# Mock Supabase sign_up response
		class MockSession:
			access_token = 'token'
			refresh_token = 'refresh'
		class MockUser:
			id = 'user_id'
			email = 'test@example.com'
		mock_sb.return_value.auth.sign_up.return_value = type('MockRes', (), {
			'session': MockSession(),
			'user': MockUser()
		})
		response = self.client.post(self.signin_url, {
			'action': 'signup',
			'email': 'test@example.com',
			'password': 'password123',
			'password_confirm': 'password123',
		})
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, self.home_url)

	@patch('core.views._sb')
	def test_signin_success(self, mock_sb):
		# Mock Supabase sign_in_with_password response
		class MockSession:
			access_token = 'token'
			refresh_token = 'refresh'
		class MockUser:
			id = 'user_id'
			email = 'test@example.com'
		mock_sb.return_value.auth.sign_in_with_password.return_value = type('MockRes', (), {
			'session': MockSession(),
			'user': MockUser()
		})
		response = self.client.post(self.signin_url, {
			'action': 'signin',
			'email': 'test@example.com',
			'password': 'password123',
		})
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, self.home_url)

	def test_logout_clears_session(self):
		session = self.client.session
		session['sb_access_token'] = 'token'
		session['sb_user_id'] = 'user_id'
		session.save()
		response = self.client.post(self.logout_url)
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, self.signin_url)
		session = self.client.session
		self.assertNotIn('sb_access_token', session)
		self.assertNotIn('sb_user_id', session)

	@patch('core.views._sb')
	def test_host_event_requires_auth(self, mock_sb):
		# Should redirect to signin if not authenticated
		response = self.client.get(self.host_event_url)
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, self.signin_url)

	@patch('core.views._sb')
	def test_host_event_success(self, mock_sb):
		# Simulate authenticated session right before POST
		event_data = {
			'title': 'Board Game Night',
			'description': 'Fun games!',
			'event_date': '2025-12-01T19:00',
			'location': 'Central Park',
		}
		from django.contrib.sessions.middleware import SessionMiddleware
		from django.test.client import RequestFactory
		factory = RequestFactory()
		request = factory.get(self.host_event_url)
		middleware = SessionMiddleware(lambda req: None)
		middleware.process_request(request)
		request.session['sb_user_email'] = 'test@example.com'
		request.session['sb_user_id'] = 'user_id'
		request.session['sb_access_token'] = 'token'
		request.session.save()
		session_key = request.session.session_key
		self.client.cookies['sessionid'] = session_key
		print('Session before POST (host_event):', dict(request.session.items()))
		mock_sb.return_value.table.return_value.insert.return_value.execute.return_value = None
		response = self.client.post(self.host_event_url, event_data, follow=True)
		# Debug: print session keys after request
		print('Session after POST (host_event):', dict(self.client.session.items()))
		# Check that the final redirect is to home
		self.assertEqual(response.redirect_chain[-1][0], self.home_url)

	@patch('core.views._sb')
	def test_rsvp_toggle_requires_auth(self, mock_sb):
		url = reverse('rsvp_toggle', args=['event_id'])
		response = self.client.post(url)
		self.assertEqual(response.status_code, 302)
		self.assertEqual(response.url, self.signin_url)

	@patch('core.views._sb')
	def test_rsvp_toggle_success(self, mock_sb):
		# Simulate authenticated session right before POST
		from django.contrib.sessions.middleware import SessionMiddleware
		from django.test.client import RequestFactory
		url = reverse('rsvp_toggle', args=['event_id'])
		factory = RequestFactory()
		request = factory.get(url)
		middleware = SessionMiddleware(lambda req: None)
		middleware.process_request(request)
		request.session['sb_user_email'] = 'test@example.com'
		request.session['sb_user_id'] = 'user_id'
		request.session['sb_access_token'] = 'token'
		request.session.save()
		session_key = request.session.session_key
		self.client.cookies['sessionid'] = session_key
		print('Session before POST (rsvp_toggle):', dict(request.session.items()))
		# Mock RSVP logic
		mock_sb.return_value.table.return_value.select.return_value.eq.return_value.eq.return_value.execute.return_value.data = []
		mock_sb.return_value.table.return_value.insert.return_value.execute.return_value = None
		mock_sb.return_value.table.return_value.delete.return_value.eq.return_value.eq.return_value.execute.return_value = None
		url = reverse('rsvp_toggle', args=['event_id'])
		response = self.client.post(url, follow=True)
		# Debug: print session keys after request
		print('Session after POST (rsvp_toggle):', dict(self.client.session.items()))
		# Check that the final redirect is to home
		self.assertEqual(response.redirect_chain[-1][0], self.home_url)
