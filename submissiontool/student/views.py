from django.shortcuts import render, redirect
from django.http import HttpResponse
from submissiontool.config import firebase, firebaseConfig
from django.views.decorators.cache import never_cache
from django.contrib import auth
from django.core.files.storage import default_storage
from django.conf import settings
from datetime import datetime
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

    return render(request, 'student/home.html', {"message": message})


@never_cache
def signUp(request):
    if "uid" in request.session:
        return redirect(dashboard)
    message = None
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('secretkey')
        fauth = firebase.auth()
        try:
            user = fauth.create_user_with_email_and_password(email, password)
            session_id = user['localId']
            print(request)
            request.session['uid'] = str(session_id)
            db = firebase.database()
            data = {'rollno': request.POST.get('rollno'),
                    'name': request.POST.get('name'),
                    'section_id': request.POST.get('section_id')
                    }
            ref = db.child("students").child(request.session['uid']).set(data)
            print(ref)
            return redirect(dashboard)
        except:
            message = "Error signing Up"

    return render(request, 'student/signUp.html', {"message": message})


@never_cache
def logout(request):
    auth.logout(request)
    return redirect(home)


@never_cache
def dashboard(request):
    if "uid" not in request.session:
        return redirect(home)
    contextDict = None
    try:
        db = firebase.database()
        data = db.child("students").child(request.session['uid']).get()
        assignmentObj = db.child("assignments").order_by_child(
            "sectionid").equal_to(data.val()['section_id']).get()
        print(assignmentObj.val())
        contextDict = {'date': datetime.today().strftime('%Y-%m-%d'),
                       'name': data.val(),
                       'assignmentData': assignmentObj.val()}
    except Exception as e:
        print('error')

    return render(request, 'student/dashboard.html', contextDict)


def view_assignment(request, slug=None):
    try:
        storage = firebase.storage()
        link = storage.child(slug).child(
            slug+'.pdf').get_url(request.session["uid"])
        print(link)
        return redirect(link)
    except Exception as e:
        print(e)
        print('Failed')

    return render(dashboard)


def submit_assignment(request, slug=None):
    db = firebase.database()
    data = db.child("students").child(request.session['uid']).get()
    print(data.val())
    assignment = db.child("assignments").child(slug).get()
    print(assignment.val())
    if request.method == "POST":
        uploaded_file = request.FILES['assignment']
        try:
            file_name = default_storage.save(
                slug+data.val()['rollno']+'.pdf', uploaded_file)
            # print(file_name)
            storage = firebase.storage()
            path_on_cloud = slug+'/submissions/'+request.session['uid']+'.pdf'
            path_local = settings.MEDIA_ROOT+'/'+file_name
            # print(path_local)
            storage.child(path_on_cloud).put(path_local)
            db.child("assignments").child(slug).child("submissions").child(
                request.session['uid']).set(data.val())
        except Exception as e:
            print('error')
        return redirect(dashboard)

    return render(request, 'student/submit.html', {'student': data.val(), 'asObj': assignment.val()})
