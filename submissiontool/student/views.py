from django.shortcuts import render
from django.http import HttpResponse
from submissiontool.config import firebase,firebaseConfig
from django.views.decorators.cache import never_cache
import pyrebase
# Create your views here.
@never_cache
def home(request):
    if "uid" in request.session:
        return render(request, 'student/dashboard.html')
    message = None
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('secretkey')
        auth = firebase.auth()
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session_id = user['localId']
            print(request)
            request.session['uid'] = str(session_id)
            return render(request, 'student/dashboard.html')
        except:
            message = "Invalid Credentials"

    return render(request,'student/home.html',{"message":message})
