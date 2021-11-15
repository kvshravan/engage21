from django.test import TestCase

# Create your tests here.
class URLTests(TestCase):
    def test_student_home(self):
        response = self.client.get('/student',{},True)
        self.assertEqual(response.status_code, 200)
