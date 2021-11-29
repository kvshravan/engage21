from django.shortcuts import render, redirect
from submissiontool.config import firebase
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
            request.session['uid'] = str(session_id)
            request.session['idToken'] = str(user['idToken'])
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
            request.session['uid'] = str(session_id)
            db = firebase.database()
            data = {'rollno': request.POST.get('rollno'),
                    'name': request.POST.get('name'),
                    'section_id': str(request.POST.get('section_id')).upper()
                    }
            ref = db.child("students").child(request.session['uid']).set(data)
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
        if assignmentObj.val():
            for key, assignment in assignmentObj.val().items():
                marks = db.child("assignments").child("submissions").child(
                    key).child(request.session['uid']).child("marks").get()
                if marks.val() is not None:
                    assignment['status'] = 1
                    assignment['marks'] = marks.val()
                else:
                    assignment['status'] = 0
                    assignment['marks'] = '-'
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
        return redirect(link)
    except Exception as e:
        print('error')

    return render(dashboard)


def submit_assignment(request, slug=None):
    db = firebase.database()
    data = db.child("students").child(request.session['uid']).get()
    assignment = db.child("assignments").child(slug).get()
    if request.method == "POST":
        uploaded_file = request.FILES['assignment']
        try:
            file_name = default_storage.save(
                slug+data.val()['rollno']+'.pdf', uploaded_file)
            storage = firebase.storage()
            path_on_cloud = slug+'/submissions/'+request.session['uid']+'.pdf'
            path_local = settings.MEDIA_ROOT+'/'+file_name
            storage.child(path_on_cloud).put(path_local)
            val = data.val()
            val['marks'] = '-'
            db.child("assignments").child("submissions").child(slug).child(
                request.session['uid']).set(val)
        except Exception as e:
            print('error')
        return redirect(dashboard)

    return render(request, 'student/submit.html', {'student': data.val(), 'asObj': assignment.val()})


@never_cache
def reset_password(request):
    if "idToken" not in request.session:
        return redirect(home)
    db = firebase.database()
    name = db.child("students").child(request.session['uid']).get()
    fauth = firebase.auth()
    info = fauth.get_account_info(request.session['idToken'])
    try:
        fauth.send_password_reset_email(info['users'][0]['email'])
    except Exception as e:
        print('error')
    return render(request, 'student/reset.html', {'name': name.val()})
