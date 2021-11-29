from django.shortcuts import render, redirect
from submissiontool.config import firebase
from django.views.decorators.cache import never_cache
from django.conf import settings
from django.core.files.storage import default_storage
from django.contrib import auth
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
        except Exception as e:
            message = "Invalid Credentials"

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
    try:
        for key in assignmentsData.val():
            detailDict = assignmentsData.val()[key]
            detailDict['assign_id'] = key
            sectionKey = detailDict['sectionid']
            if sectionKey not in sectionData:
                sectionData[sectionKey] = []
            sectionData[sectionKey].append(detailDict)
    except Exception as e:
        message = "Error"
    return render(request, 'faculty/dashboard.html',
                  {'name': name.val(),
                   'assignmentData': sectionData})


@never_cache
def createAssignment(request):
    if "uid" not in request.session:
        return redirect(home)
    message = None
    workLoad = None
    db = firebase.database()
    name = db.child("faculty").child(request.session['uid']).get()
    if request.method == "POST" and "upload" in request.POST:
        db = firebase.database()
        try:
            data = {"course_id": request.POST.get("course_id"),
                    "asname": request.POST.get("asname"),
                    "deadline": request.POST.get("deadline"),
                    "facultyid": request.session['uid'],
                    "sectionid": str(request.POST.get("sectionid")).upper()
                    }
            ref = db.child("assignments").push(data)
            uploaded_file = request.FILES['assignment']
            file_name = default_storage.save(ref['name']+'.pdf', uploaded_file)
            storage = firebase.storage()
            path_on_cloud = ref['name']+'/'+ref['name']+'.pdf'
            path_local = settings.MEDIA_ROOT+'/'+file_name
            storage.child(path_on_cloud).put(path_local)
            return redirect(dashboard)
        except Exception as e:
            message = "Error in uploading"
    if request.method == "POST" and 'workload' in request.POST:
        assignmentsData = db.child("assignments").order_by_child(
            "sectionid").equal_to(request.POST.get("sectionid")).get()
        noAssignments = 0
        date_format = '%Y-%m-%d'
        today = datetime.today().strftime(date_format)
        delta = datetime.strptime(request.POST.get(
            "deadline"), date_format) - datetime.strptime(today, date_format)
        noDays = delta.days
        value = assignmentsData.val()
        if len(value) > 0:
            for key, item in value.items():
                if item['deadline'] >= today and item['deadline'] <= request.POST.get("deadline"):
                    noAssignments += 1
        load = ((noAssignments+1)/(noDays))
        workLoad = {"noDays": noDays, "noAssignments": noAssignments,
                    "deadline": request.POST.get("deadline"),
                    "load": 2*load,
                    "wload": load
                    }
    return render(request, 'faculty/create.html', {"workLoad": workLoad, "name": name.val(), "message": message})


@never_cache
def view_submissions(request, slug=None):
    if "uid" not in request.session:
        return redirect(home)
    db = firebase.database()
    name = db.child("faculty").child(request.session['uid']).get()
    assignmentsData = db.child("assignments").child("submissions").child(
        slug).get()
    asname = db.child("assignments").child(slug).child(
        "asname").get()
    return render(request, 'faculty/view.html',
                  {'name': name.val(),
                   'asid': slug,
                   'asname': asname.val(),
                   'assignmentData': assignmentsData.val()})


def generate_link(assignment_id, student_id, uid):
    link = None
    try:
        storage = firebase.storage()
        link = storage.child(assignment_id).child(
            "submissions").child(student_id+'.pdf').get_url(uid)
        return link
    except Exception as e:
        print('error')

    return link


@never_cache
def extend_deadline(request, slug=None):
    if "uid" not in request.session:
        return redirect(home)
    db = firebase.database()
    name = db.child("faculty").child(request.session['uid']).get()
    assignment = db.child("assignments").child(slug).get()
    if request.method == "POST":
        try:
            db.child("assignments").child(slug).update(
                {'deadline': request.POST.get("newdeadline")})
            return redirect(dashboard)
        except Exception as e:
            print('error')

    return render(request, 'faculty/extend.html', {'name': name.val(), 'asObj': assignment.val()})


@never_cache
def evaluate_submission(request, asid=None, sid=None):
    if "uid" not in request.session:
        return redirect(home)
    db = firebase.database()
    name = db.child("faculty").child(request.session['uid']).get()
    asname = db.child("assignments").child(asid).child(
        "asname").get()
    assignment = db.child("assignments").child(
        "submissions").child(asid).child(sid).get()
    val = assignment.val()
    val['link'] = generate_link(asid, sid, request.session['uid'])
    if request.method == "POST":
        try:
            db.child("assignments").child("submissions").child(asid).child(sid).update(
                {'marks': request.POST.get("newmarks")})
            return redirect('faculty-view', slug=asid)
        except Exception as e:
            print('error')

    return render(request, 'faculty/evaluate.html', {'name': name.val(), 'asname': asname.val(), 'asObj': val})


@never_cache
def admin(request):
    if "uid" in request.session:
        return redirect(dashboard)
    message = None
    if request.method == "POST":
        aemail = request.POST.get('aemail')
        apassword = request.POST.get('asecretkey')
        femail = request.POST.get('femail')
        fpassword = request.POST.get('fsecretkey')
        fname = request.POST.get('fname')
        fauth = firebase.auth()
        db = firebase.database()
        try:
            user = fauth.sign_in_with_email_and_password(aemail, apassword)
            fuser = fauth.create_user_with_email_and_password(
                femail, fpassword)
            session_id = fuser['localId']
            ref = db.child("faculty").child(session_id).set({'name': fname})
            return redirect(dashboard)
        except Exception as e:
            message = "Invalid Credentials"

    return render(request, 'faculty/admin.html', {"message": message})


@never_cache
def delete(request, aid):
    if "uid" not in request.session:
        return redirect(home)
    message = None
    db = firebase.database()
    name = db.child("faculty").child(request.session['uid']).get()
    asname = db.child("assignments").child(aid).child(
        "asname").get()
    if request.method == "POST":
        try:
            db.child("assignments").child(aid).remove()
            try:
                db.child("assignments").child(
                    "submissions").child(aid).remove()
            except Exception as e:
                message = None
            return redirect(dashboard)
        except Exception as e:
            message = "Error"
    return render(request, 'faculty/delete.html', {"message": message, 'name': name.val(), 'asname': asname.val()})


@never_cache
def reset_password(request):
    if "idToken" not in request.session:
        return redirect(home)
    db = firebase.database()
    name = db.child("faculty").child(request.session['uid']).get()
    fauth = firebase.auth()
    info = fauth.get_account_info(request.session['idToken'])
    try:
        fauth.send_password_reset_email(info['users'][0]['email'])
    except Exception as e:
        print('error')
    return render(request, 'faculty/reset.html', {'name': name.val()})
