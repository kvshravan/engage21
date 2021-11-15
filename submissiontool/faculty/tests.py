from django.test import TestCase

# Create your tests here.
class URLTests(TestCase):
    def test_faculty_home(self):
        response = self.client.get('/faculty',{},True)
        self.assertEqual(response.status_code, 301)
