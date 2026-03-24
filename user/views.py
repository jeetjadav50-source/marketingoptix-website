from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q, Prefetch
from datetime import datetime
from .models import (
    State, City, Category, Service, User, Project, 
    ProjectService, Quotation, Review, UserImage, 
    SavedProject, Message, Notification, UserLanguage
)

def home(request):
    search_query = request.GET.get('q', '')
    service_id = request.GET.get('service', '')
    
    projects = Project.objects.select_related('userid').prefetch_related(
        Prefetch('projectservice_set', queryset=ProjectService.objects.select_related('serviceid'), to_attr='prefetched_services')
    ).all()
    
    if search_query:
        projects = projects.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
        
    if service_id:
        projects = projects.filter(projectservice__serviceid_id=service_id)

    for p in projects:
        p.services = p.prefetched_services
    
    all_services = Service.objects.all()
    
    saved_ids = []
    if request.session.get("uid"):
        saved_ids = SavedProject.objects.filter(userid_id=request.session.get("uid")).values_list('projectid_id', flat=True)

    stats = {
        'total_projects': Project.objects.count(),
        'active_marketers': User.objects.filter(role='marketer').count(),
        'completed_projects': Project.objects.filter(status=3).count(),
        'total_users': User.objects.count()
    }

    context = {
        'projects': projects,
        'all_services': all_services,
        'search_query': search_query,
        'selected_service': int(service_id) if service_id else None,
        'saved_ids': saved_ids,
        'stats': stats
    }
    return render(request, 'home.html', context)

def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        profilepic = request.FILES.get("profilepic")
        gender = request.POST.get("gender")
        dob = request.POST.get("dob")
        pwd = request.POST.get("pwd")
        cpwd = request.POST.get("cpwd")
        role = request.POST.get("role", "client")

        if pwd != cpwd:
            return redirect('signup')
        
        if User.objects.filter(username=username).exists():
            return redirect('signup')
        
        u = User(
            username=username,
            email=email,
            profilepic=profilepic,
            gender=gender,
            dob=dob,        
            password=pwd,
            role=role
        )
        u.save()
        return redirect('login')
    return render(request, 'signup.html')

def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        pwd = request.POST.get("pwd")
        u = User.objects.filter(username=username, password=pwd).first()
        if u is None:
            data = {"error": "Invalid username or password"}
            return render(request, "login.html", data)
        else:
            request.session["uid"] = u.userid
            request.session["username"] = u.username
            request.session["role"] = u.role
            return redirect('home')
    return render(request, "login.html")

def logout(request):
    request.session.flush()
    return redirect('login')

def addproject(request):
    if not request.session.get("uid"):
        return redirect('login')
        
    if request.method == "POST":
        uid = request.session.get("uid")
        title = request.POST.get("title")
        description = request.POST.get("description")
        budget = request.POST.get("budget")
        mode = request.POST.get("mode")
        
        p = Project(
            userid_id=uid,
            title=title,
            description=description,
            budget=budget,
            mode=mode
        )
        p.save()
        
        service_ids = request.POST.getlist("services")
        for sid in service_ids:
            ps = ProjectService(projectid=p, serviceid_id=sid)
            ps.save()
            
        return redirect('home')
        
    context = {
        "services_list": Service.objects.all()
    }
    return render(request, "addproject.html", context)

def project_details(request, pid):
    p = Project.objects.select_related('userid').get(projectid=pid)
    p_services = ProjectService.objects.filter(projectid=p).select_related('serviceid')
    
    poster_reviews = Review.objects.filter(Q(client_user=p.userid) | Q(marketer_user=p.userid))
    avg_rating = 0
    if poster_reviews.exists():
        total_rating = sum([r.rating for r in poster_reviews])
        avg_rating = total_rating / poster_reviews.count()
        
    quotations_list = Quotation.objects.filter(projectid=p).select_related('userid')

    has_existing_quotation = False
    if request.session.get("uid"):
        has_existing_quotation = Quotation.objects.filter(userid_id=request.session.get("uid"), projectid=p).exists()

    if request.POST.get("submit_quotation"):
        if not request.session.get("uid"):
            return redirect('login')
            
        uid = request.session.get("uid")
        
        if uid == p.userid_id:
            messages.error(request, "You cannot bid on your own project.")
        elif Quotation.objects.filter(userid_id=uid, projectid=p).exists():
            messages.error(request, "You have already submitted a quotation for this project.")
        else:
            budget = request.POST.get("budget")
            description = request.POST.get("description")
            pdf = request.FILES.get("pdf")
            
            q = Quotation(userid_id=uid, projectid=p, budget=budget, description=description, pdf=pdf)
            q.save()
            
            Notification(
                userid=p.userid,
                content=f"New quotation received for project: {p.title}",
                link=f"/project-details/{p.projectid}/"
            ).save()
            
            messages.success(request, "Quotation submitted successfully!")
            has_existing_quotation = True

    accepted_q = quotations_list.filter(status='accepted').first()
    review_exists = Review.objects.filter(projectid=p).exists()
    
    is_saved = False
    if request.session.get("uid"):
        is_saved = SavedProject.objects.filter(userid_id=request.session.get("uid"), projectid=p).exists()
    
    context = {
        'p': p,
        'quotations': quotations_list,
        'services': p_services, 
        'avg_rating': round(avg_rating, 1),
        'rating_stars': range(int(avg_rating)),
        'empty_stars': range(5 - int(avg_rating)),
        'poster': p.userid,
        'accepted_q': accepted_q,
        'review_exists': review_exists,
        'is_saved': is_saved,
        'has_existing_quotation': has_existing_quotation
    }
    return render(request, "project_details.html", context)

def my_projects(request):
    if not request.session.get("uid"):
        return redirect('login')
    
    uid = request.session.get("uid")
    projects_list = Project.objects.filter(userid_id=uid).order_by('-createdDT')
    
    total = projects_list.count()
    active = projects_list.filter(status=2).count()
    completed = projects_list.filter(status=3).count()
    
    for p in projects_list:
        p.quotation_count = Quotation.objects.filter(projectid=p).count()
        
    context = {
        'projects': projects_list,
        'total_count': total,
        'active_count': active,
        'completed_count': completed
    }
    return render(request, "my_projects.html", context)

def my_quotations(request):
    if not request.session.get("uid"):
        return redirect('login')
        
    uid = request.session.get("uid")
    quotations_list = Quotation.objects.filter(userid_id=uid).select_related('projectid', 'projectid__userid').order_by('-quotationid')
    
    total = quotations_list.count()
    accepted = quotations_list.filter(status='accepted').count()
    pending = quotations_list.filter(status='pending').count()
    
    context = {
        'quotations': quotations_list,
        'total_count': total,
        'accepted_count': accepted,
        'pending_count': pending
    }
    return render(request, "my_quotations.html", context)

def profile_view(request, uid):
    u = User.objects.select_related('cityid').get(userid=uid)
    received_reviews = Review.objects.filter(Q(marketer_user=u) | Q(client_user=u))
    
    avg_rating = 0
    if received_reviews.exists():
        avg_rating = sum([r.rating for r in received_reviews]) / received_reviews.count()
    
    portfolio = UserImage.objects.filter(userid=u).order_by('-userimageid')
    languages = UserLanguage.objects.filter(userid=u)
        
    context = {
        'target_user': u,
        'reviews': received_reviews.order_by('-reviewdate'),
        'avg_rating': round(avg_rating, 1),
        'rating_stars': range(int(avg_rating)),
        'empty_stars': range(5 - int(avg_rating)),
        'portfolio': portfolio,
        'languages': languages
    }
    return render(request, "profile.html", context)

def accept_quotation(request, qid):
    # This existing function is kept for any internal logic, but the user flows through checkout
    if not request.session.get("uid"):
        return redirect('login')
        
    uid = request.session.get("uid")
    q = Quotation.objects.select_related('projectid').get(quotationid=qid)
    
    if q.projectid.userid_id != uid:
        return redirect('home')
        
    q.status = 'accepted'
    q.save()
    
    p = q.projectid
    p.status = 2 
    p.save()
    
    Notification(
        userid=q.userid,
        content=f"Congratulations! Your quotation for '{p.title}' has been accepted.",
        link=f"/project-details/{p.projectid}/"
    ).save()
    
    Quotation.objects.filter(projectid=p).exclude(quotationid=qid).update(status='rejected')
    
    return redirect('project_details', pid=p.projectid)

def checkout(request, qid):
    if not request.session.get("uid"):
        return redirect('login')
        
    uid = request.session.get("uid")
    q = Quotation.objects.select_related('projectid', 'userid').get(quotationid=qid)
    p = q.projectid
    
    if p.userid_id != uid:
        messages.error(request, "Unauthorized access to checkout.")
        return redirect('home')
        
    # Calculate amounts
    budget = q.budget
    platform_fee = budget * 0.05  # 5% platform fee
    gst = platform_fee * 0.18     # 18% GST on platform fee
    total_amount = budget + platform_fee + gst
    
    context = {
        'q': q,
        'p': p,
        'marketer': q.userid,
        'budget': budget,
        'platform_fee': platform_fee,
        'gst': gst,
        'total_amount': total_amount
    }
    return render(request, "checkout.html", context)

def process_payment(request, qid):
    if request.method == "POST":
        if not request.session.get("uid"):
            return redirect('login')
            
        uid = request.session.get("uid")
        q = Quotation.objects.select_related('projectid').get(quotationid=qid)
        
        if q.projectid.userid_id != uid:
            return redirect('home')
            
        # Re-use the accept quotation logic here since payment is "successful"
        q.status = 'accepted'
        q.save()
        
        p = q.projectid
        p.status = 2 
        p.save()
        
        Notification(
            userid=q.userid,
            content=f"Payment received! Your quotation for '{p.title}' has been accepted and the funds are in escrow.",
            link=f"/project-details/{p.projectid}/"
        ).save()
        
        Quotation.objects.filter(projectid=p).exclude(quotationid=qid).update(status='rejected')
        
        messages.success(request, f"Payment successful! ₹{request.POST.get('total_amount', q.budget)} added to platform escrow. Project '{p.title}' is now active.")
        return redirect('project_details', pid=p.projectid)
        
    return redirect('home')

def complete_project(request, pid):
    if not request.session.get("uid"):
        return redirect('login')
        
    uid = request.session.get("uid")
    p = Project.objects.get(projectid=pid)
    
    if p.userid_id != uid:
        return redirect('home')
        
    p.status = 3
    p.save()
    
    q = Quotation.objects.filter(projectid=p, status='accepted').first()
    if q:
        Notification(
            userid=q.userid,
            content=f"Project '{p.title}' has been marked as completed by the client.",
            link=f"/project-details/{p.projectid}/"
        ).save()
        
    return redirect('project_details', pid=p.projectid)

def submit_review(request):
    if not request.session.get("uid"):
        return redirect('login')
        
    if request.POST.get("submit_review"):
        pid = request.POST.get("projectid")
        rating = request.POST.get("rating")
        review_text = request.POST.get("review")
        
        p = Project.objects.select_related('userid').get(projectid=pid)
        q = Quotation.objects.filter(projectid=p, status='accepted').first()
        
        if not q:
            return redirect('home')

        if Review.objects.filter(client_user=p.userid, projectid=p).exists():
            messages.error(request, "You have already submitted a review for this project.")
            return redirect('project_details', pid=p.projectid)

        r = Review(
            marketer_user=q.userid,
            client_user=p.userid,
            projectid=p,
            review=review_text,
            rating=rating
        )
        r.save()
        
        return redirect('profile', uid=q.userid.userid)
        
    return redirect('home')

def toggle_save_project(request, pid):
    if not request.session.get("uid"):
        return redirect('login')
    
    uid = request.session.get("uid")
    p = Project.objects.get(projectid=pid)
    
    save_entry = SavedProject.objects.filter(userid_id=uid, projectid=p).first()
    
    if save_entry:
        save_entry.delete()
        messages.info(request, "Project removed from saved list.")
    else:
        SavedProject(userid_id=uid, projectid=p).save()
        messages.success(request, "Project saved successfully!")
        
    return redirect(request.META.get('HTTP_REFERER', 'home'))

def saved_projects(request):
    if not request.session.get("uid"):
        return redirect('login')
        
    uid = request.session.get("uid")
    saved_list = SavedProject.objects.filter(userid_id=uid).select_related('projectid', 'projectid__userid').order_by('-saveid')
    
    for s in saved_list:
        p = s.projectid
        p.services = ProjectService.objects.filter(projectid=p).select_related('serviceid')
        
    context = {'saved_projects': saved_list}
    return render(request, "saved_projects.html", context)

def upload_portfolio_image(request):
    if not request.session.get("uid"):
        return redirect('login')
        
    if request.method == "POST" and request.FILES.get("image"):
        uid = request.session.get("uid")
        img = request.FILES.get("image")
        
        UserImage(userid_id=uid, imageurl=img).save()
        messages.success(request, "Portfolio image uploaded!")
        
    return redirect('profile', uid=request.session.get("uid"))

def delete_portfolio_image(request, imgid):
    if not request.session.get("uid"):
        return redirect('login')
        
    uid = request.session.get("uid")
    img = UserImage.objects.get(userimageid=imgid)
    
    if img.userid_id == uid:
        img.delete()
        messages.success(request, "Image removed from portfolio.")
        
    return redirect('profile', uid=uid)


def get_user_threads(uid):
    sent_to = Message.objects.filter(sender_id=uid).values_list('receiver_id', flat=True)
    received_from = Message.objects.filter(receiver_id=uid).values_list('sender_id', flat=True)
    u_ids = set(list(sent_to) + list(received_from))

    threads = []
    for other_id in u_ids:
        try:
            other_user = User.objects.get(userid=other_id)
            latest = Message.objects.filter(
                Q(sender_id=uid, receiver_id=other_id) |
                Q(sender_id=other_id, receiver_id=uid)
            ).order_by('-timestamp').first()

            unread_count = Message.objects.filter(sender_id=other_id, receiver_id=uid, is_read=False).count()

            threads.append({
                'user': other_user,
                'latest_message': latest,
                'unread_count': unread_count
            })
        except User.DoesNotExist:
            continue

    threads.sort(key=lambda x: x['latest_message'].timestamp if x['latest_message'] else datetime.min, reverse=True)
    return threads

def inbox(request):
    if not request.session.get("uid"):
        return redirect('login')

    uid = request.session.get("uid")
    threads = get_user_threads(uid)

    context = {'threads': threads}
    return render(request, "inbox.html", context)


def chat_thread(request, other_uid):
    if not request.session.get("uid"):
        return redirect('login')

    my_uid = request.session.get("uid")
    other_user = User.objects.get(userid=other_uid)

    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            msg = Message(sender_id=my_uid, receiver_id=other_uid, content=content)
            msg.save()
            Notification(
                userid=other_user,
                content=f"You have a new message from {request.session.get('username')}.",
                link=f"/chat/{my_uid}/"
            ).save()
            return redirect('chat_thread', other_uid=other_uid)

    history = Message.objects.filter(
        Q(sender_id=my_uid, receiver_id=other_uid) |
        Q(sender_id=other_uid, receiver_id=my_uid)
    ).order_by('timestamp')

    Message.objects.filter(sender_id=other_uid, receiver_id=my_uid, is_read=False).update(is_read=True)

    context = {
        'other_user': other_user,
        'history': history,
        'threads': get_user_threads(my_uid)
    }
    return render(request, "chat_thread.html", context)


def notifications_list(request):
    if not request.session.get("uid"):
        return redirect('login')

    uid = request.session.get("uid")
    notifs = Notification.objects.filter(userid_id=uid).order_by('-timestamp')

    Notification.objects.filter(userid_id=uid, is_read=False).update(is_read=True)

    context = {'notifications': notifs}
    return render(request, "notifications.html", context)


def edit_profile(request):
    if not request.session.get("uid"):
        return redirect('login')

    uid = request.session.get("uid")
    u = User.objects.get(userid=uid)
    all_cities = City.objects.all()

    if request.method == "POST":
        u.username = request.POST.get("username")
        u.email = request.POST.get("email")
        u.bio = request.POST.get("bio")
        u.gender = request.POST.get("gender")
        u.displaycontact = request.POST.get("contact")
        u.website = request.POST.get("website")
        u.displayaddress = request.POST.get("address")
        
        cid = request.POST.get("city")
        if cid:
            u.cityid_id = cid
            
        if request.FILES.get("profilepic"):
            u.profilepic = request.FILES.get("profilepic")
            
        u.save()
        request.session['username'] = u.username
        messages.success(request, "Profile updated successfully!")
        return redirect('profile', uid=uid)

    context = {
        'u': u,
        'cities': all_cities
    }
    return render(request, "edit_profile.html", context)


def add_language(request):
    if not request.session.get("uid"):
        return redirect('login')
    
    if request.method == "POST":
        uid = request.session.get("uid")
        language = request.POST.get("language", "").strip()
        
        if language:
            if UserLanguage.objects.filter(userid_id=uid, language__iexact=language).exists():
                messages.error(request, "This language is already added.")
            else:
                UserLanguage(userid_id=uid, language=language).save()
                messages.success(request, f"{language} added to your profile!")
    
    return redirect('profile', uid=request.session.get("uid"))


def delete_language(request, lid):
    if not request.session.get("uid"):
        return redirect('login')
    
    uid = request.session.get("uid")
    lang = UserLanguage.objects.filter(userlanguageid=lid, userid_id=uid).first()
    
    if lang:
        lang.delete()
        messages.success(request, "Language removed from your profile.")
    
    return redirect('profile', uid=uid)


def about_us(request):
    return render(request, 'about_us.html')

def services(request):
    all_services = Service.objects.all()
    return render(request, 'services.html', {'services': all_services})

def blog(request):
    return render(request, 'blog.html')

def contact(request):
    return render(request, 'contact.html')

def help_support(request):
    return render(request, 'help_support.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')

def terms_service(request):
    return render(request, 'terms_service.html')

def faq(request):
    return render(request, 'faq.html')
