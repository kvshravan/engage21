from django.shortcuts import render,redirect
from django.http import HttpResponse
from submissiontool.config import firebase,firebaseConfig
from django.views.decorators.cache import never_cache
from django.conf import settings
from django.core.files.storage import default_storage
import pyrebase
from django.contrib import auth
# Create your views here.   
@never_cache
def home(request):
    if "uid" in request.session:
        return redirect(dashboard)
    message = None
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('secretkey')
        fauth = firebase.auth()
        try:
            user = fauth.sign_in_with_email_and_password(email, password)
            session_id = user['localId']
            print(request)
            request.session['uid'] = str(session_id)
            return redirect(dashboard)
        except:
            message = "Invalid Credentials"

    return render(request,'faculty/home.html',{"message":message})

def logout(request):
    auth.logout(request)
    return  redirect(home)

def dashboard(request):
    return render(request,'faculty/dashboard.html')

def createAssignment(request):
    if "uid" not in request.session:
        return redirect(home)
    if request.method == "POST":
        db = firebase.database()
        ref = db.child("assignments").child(request.POST.get("section_id")).push("")
        print(ref)
        db.child("faculty").child(request.POST.get("section_id")).child(ref["name"]).set("")
        uploaded_file = request.FILES['assignment']
        file_name = default_storage.save(ref['name']+'.pdf',uploaded_file)
        print(file_name)
        storage = firebase.storage()
        path_on_cloud = ref['name']+'.pdf'
        path_local = settings.MEDIA_ROOT+'/'+file_name
        print(path_local)
        storage.child(path_on_cloud).put(path_local)
    return render(request, 'faculty/create.html')