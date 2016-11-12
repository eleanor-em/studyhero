from django import forms
from main.models import Subject

class SubjectForm(forms.ModelForm):
    name = forms.CharField(max_length=50, help_text="Subject name:")
    colour = forms.ChoiceField(choices=Subject.COLOURS, help_text="Colour:")
    days = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=Subject.DAYS, help_text="Days with lectures:")
    
    class Meta:
        model = Subject
        fields = ('name', 'colour', 'days')