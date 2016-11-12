import json
from datetime import datetime, timedelta

from django.shortcuts import render, HttpResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core import serializers

from main.forms import SubjectForm
from main.models import Subject, Card

ONE_DAY_POINTS = 10
ONE_WEEK_POINTS = 5
ONE_MONTH_POINTS = 2

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
    
def add_card(title, subject, points, date):
    return Card.objects.get_or_create(title=title,
                                      subject=Subject.objects.get(name=subject),
                                      points=points,
                                      date=date)

def delete_all_cards():
    Card.objects.all().delete()
                                      
def create_all_cards(commence, midsem_break):
    for subject in Subject.objects.all():
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
                    add_card(subject.name + " Lecture " + str(lecture_number), subject.name, delay_points[1],
                             week_date + delay_points[0]
                             + timedelta(days=int(lecture_day)))
                lecture_number += 1
                
            week_date += timedelta(weeks=1)
            
            if week_date >= midsem_break and skipped_break == False:
                week_date += timedelta(weeks=1)
                skipped_break = True

def get_next_cards():
    cards = Card.objects.all().order_by("date")
    if cards:
        next_cards = list()
        first_date = cards[0].date
        for card in cards:
            if card.date != first_date:
                break;
            next_cards.append(card)
    return next_cards
    
                
@ensure_csrf_cookie
def index(request, message=None):
    # Get a message if there is one
    dict = { "subjects": Subject.objects.all() }
    if message is not None:
        dict.update({ "message": message })
    
    next_cards = get_next_cards()
    dict.update({ "cards": next_cards,
                  "time_distance": (next_cards[0].date - datetime.now().date()).days })
    return render(request, "index.html", dict)
    
def new_subject(request):
    if request.method == "POST":
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return index(request, PageMessage(text="Successfully created subject!", colour="green"))
        else:
            print form.errors
    else:
        form = SubjectForm()
    return render(request, "new-subject.html", { 'form': form })
    
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
        delete_all_cards()
        create_all_cards(commence, midsem_break)
        return index(request, PageMessage(text="Successfully created cards!", colour="green"))
        
    return render(request, "create-cards.html")
    
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

def rest_clear_card(request):
    data = json.loads(request.body)
    if not data is None:
        id = data.get("id")
        card = Card.objects.get(pk=id) or None
        if not card is None:
            card.delete()

    return HttpResponse()
    
def rest_get_cards(request):
    cards = get_next_cards()
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
    return REST_CARD_ACTIONS.get(request.method)(request)
