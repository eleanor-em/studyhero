from datetime import datetime

from django.shortcuts import render

from main.forms import SubjectForm
from main.models import Subject, Card

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
    
def render_success(request, template, success_text):
    return render(request, template, { "message": PageMessage(text=success_text, colour="green") })
    
def add_card(title, subject, points, date):
    return Card.objects.get_or_create(title=title, subject=subject, points=points, date=date)

def create_cards(commence, midsem_break):
    for subject in Subject.objects:
        lectures_per_week = subject.days.length
        print lectures_per_week
    return None

def index(request):
    return render(request, "index.html", { })
    
def new_subject(request):
    if request.method == "POST":
        form = SubjectForm(request.POST)
        if form.is_valid():
            form.save(commit=True)
            return render_success(request, "index.html", "Successfully created subject!")
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
        error = create_cards(commence, midsem_break)
        if error is None:
            return render_success(request, "index.html", "Successfully created cards!");
        return render_error(request, "create-cards.html", error)
        
    return render(request, "create-cards.html")