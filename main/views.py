import json
from datetime import datetime, timedelta

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseNotFound, HttpResponseBadRequest, HttpResponseRedirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core import serializers
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist

from main.forms import SubjectForm, UserForm
from main.models import Subject, Card

ONE_DAY_POINTS = 10
ONE_WEEK_POINTS = 5
ONE_MONTH_POINTS = 2

# Helper methods and classes

class PageMessage:
    def __init__(self, text, colour=None, css_class=None):
        if colour is None:
            colour = "red"
        self.text = text
        self.colour = colour
        if not css_class is None:
            self.css_class = css_class;

def render_error(request, template, error_text):
    return render(request, template, { "message": PageMessage(text=error_text) })
    
def render_success(request, template, success_text, extras=None):
    dict = { "message": PageMessage(text=success_text, colour="green") }
    if extras is not None:
        dict.update(extras)
    return render(request, template, dict)
    
def add_card(user, title, subject, points, date):
    return Card.objects.get_or_create(title=title,
                                      subject=Subject.objects.get(name=subject),
                                      points=points,
                                      date=date,
                                      user=user)

def delete_all_cards(user):
    Card.objects.filter(user=user).delete()
                                      
def create_all_cards(user, commence, midsem_break):
    for subject in Subject.objects.all().filter(user=user):
        week_date = commence
        lecture_number = 1
        skipped_break = False
        
        # 12 weeks of semester
        for i in range(0, 12):
            # Time delays for each round of cards
            time_delays_points = (
                (timedelta(days=1), ONE_DAY_POINTS),
                (timedelta(weeks=1), ONE_WEEK_POINTS),
                (timedelta(weeks=4), ONE_MONTH_POINTS)
            )
            # Create the actual card
            for lecture_day in subject.days:
                for delay_points in time_delays_points:
                    add_card(user,
                             subject.name + " Lecture " + str(lecture_number),
                             subject.name,
                             delay_points[1],
                             week_date + delay_points[0] + timedelta(days=int(lecture_day)))
                lecture_number += 1
                
            week_date += timedelta(weeks=1)
            
            if week_date >= midsem_break and skipped_break == False:
                week_date += timedelta(weeks=1)
                skipped_break = True

def get_next_cards(user):
    cards = Card.objects.all().filter(user=user).order_by("date")
    if cards:
        next_cards = list()
        first_date = cards[0].date
        for card in cards:
            if card.date != first_date:
                break;
            next_cards.append(card)
    return next_cards

# Views
    
@ensure_csrf_cookie
def index(request, message=None):
    # Get a message if there is one
    dict = { }
    if request.user.is_authenticated():
        dict = { "subjects": Subject.objects.all().filter(user=request.user) }
    if message is not None:
        dict.update({ "message": message })
        
    return render(request, "index.html", dict)
    
@login_required
def new_subject(request):
    if request.method == "POST":
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save(commit=False)
            subject.user = request.user
            # TODO: Check uniqueness manually
            
            subject.save()
            
            return index(request, PageMessage(text="Successfully created subject!", colour="green"))
    else:
        form = SubjectForm()
    return render(request, "new-subject.html", { 'form': form })
    
@login_required
def create_cards(request):
    if request.method == "POST":
        commence = request.POST["commence"] or None
        midsem_break = request.POST["break"] or None
        if commence is None or midsem_break is None:
            return render_error(request, "create-cards.html", "Fields missing!")
        
        # Parse dates
        commence = datetime.strptime(commence, "%Y-%m-%d")
        midsem_break = datetime.strptime(midsem_break, "%Y-%m-%d")
        
        if not midsem_break > commence:
            return render_error(request, "create-cards.html", "Break date must be after commencement date!")
        
        # Perform database manipulation
        delete_all_cards(request.user)
        create_all_cards(request.user, commence, midsem_break)
        return index(request, PageMessage(text="Successfully created cards!", colour="green"))
        
    return render(request, "create-cards.html")
    
@login_required
def delete_subject(request):
    subject = request.GET.get("name") or None
    if not subject is None:
        if request.method == "POST":
            delete = request.POST["confirm"] or None
            if not delete is None and delete == "yes":
                print Card.objects.filter(subject=Subject.objects.get(name=subject).pk).delete()
                Subject.objects.get(name=subject).delete()
        else:                
            return render(request, "delete-subject.html", { "subject": subject })
    return index(request)

def register(request):
    if request.user.is_authenticated():
        return index(request)
    if request.method == "POST":
        user_form = UserForm(data=request.POST);
        
        if user_form.is_valid():
            user = user_form.save()
            username = user.username
            password = user.password
            user.set_password(password)
            user.save()
            
            user = authenticate(username=username, password=password)
            login(request, user)
            
            return index(request, PageMessage(text="Successfully registered!", colour="green"))
    else:
        user_form = UserForm()
        
    return render(request, "register.html", { "user_form":      user_form })
                                              
def user_login(request):
    if request.user.is_authenticated():
        return index(request)
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        user = authenticate(username=username, password=password)
        message = None
        if user:
            if user.is_active:
                login(request, user)
                message = PageMessage(text="Welcome " + username + "!", colour="green")
            else:
                message = PageMessage(text="Your account has been disabled.")
        else:
            message = PageMessage(text="Your login details were incorrect")
        return index(request, message)
    return render(request, "login.html")

@login_required
def user_logout(request):
    logout(request)
    return index(request, PageMessage(text="You have successfully logged out!", colour="green"))
    
# RESTful API views
    
def rest_clear_card(request):
    data = json.loads(request.body) or None
    if data is None:
        return HttpResponseBadRequest()
    try:
        id = data.get("id")
        card = Card.objects.get(pk=id, user=request.user) or None
        card.delete()
    except:
        return HttpResponseNotFound()
        
    return HttpResponse()
    
def rest_get_cards(request):
    try:
        cards = get_next_cards(request.user)
    except ObjectDoesNotExist:
        return HttpResponseNotFound()
        
    time_distance = (cards[0].date - datetime.now().date()).days
    data = serializers.serialize('json', cards)
    # unfortunately Django doesn't make this as nice as it could be
    # here I just encode the time left to do the card in the JSON string
    # before returning it
    final_data = "[{" + '"time_distance": ' + str(time_distance) + ", " + data[2:]
    return HttpResponse(final_data)
    
REST_CARD_ACTIONS = {
    "GET": rest_get_cards,
    "DELETE": rest_clear_card,
}

def rest_card(request):
    if not request.user.is_authenticated():
        return HttpResponseNotFound()
    return REST_CARD_ACTIONS.get(request.method)(request)