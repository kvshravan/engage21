from django.shortcuts import render, redirect
from django.http import HttpResponse
from submissiontool.config import firebase, firebaseConfig
from django.views.decorators.cache import never_cache
from django.conf import settings
from django.core.files.storage import default_storage
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
        except Exception as e:
            message = "Invalid Credentials"
            print(e)

    return render(request, 'faculty/home.html', {"message": message})


@never_cache
def logout(request):
    auth.logout(request)
    return redirect(home)


@never_cache
def dashboard(request):
    if "uid" not in request.session:
        return redirect(home)
    db = firebase.database()
    name = db.child("faculty").child(request.session['uid']).get()
    assignmentsData = db.child("assignments").order_by_child(
        "facultyid").equal_to(request.session['uid']).get()
    sectionData = {}
    for key in assignmentsData.val():
        detailDict = assignmentsData.val()[key]
        sectionKey = detailDict['sectionid']
        if sectionKey not in sectionData:
            sectionData[sectionKey] = []
        sectionData[sectionKey].append(detailDict)
    return render(request, 'faculty/dashboard.html',
                  {'name': name.val(),
                   'assignmentData': sectionData})


@never_cache
def createAssignment(request):
    if "uid" not in request.session:
        return redirect(home)
    message = None
    db = firebase.database()
    name = db.child("faculty").child(request.session['uid']).get()
    if request.method == "POST":
        db = firebase.database()
        try:
            data = {"course_id": request.POST.get("course_id"),
                    "asname": request.POST.get("asname"),
                    "deadline": request.POST.get("deadline"),
                    "facultyid": request.session['uid'],
                    "sectionid": request.POST.get("sectionid")
                    }
            ref = db.child("assignments").push(data)
            print(ref)
            uploaded_file = request.FILES['assignment']
            file_name = default_storage.save(ref['name']+'.pdf', uploaded_file)
            # print(file_name)
            storage = firebase.storage()
            path_on_cloud = ref['name']+'.pdf'
            path_local = settings.MEDIA_ROOT+'/'+file_name
            # print(path_local)
            storage.child(path_on_cloud).put(path_local)
            return redirect(dashboard)
        except Exception as e:
            print(e)
            message = "Error in uploading"

    return render(request, 'faculty/create.html', {"name": name.val(), "message": message})
