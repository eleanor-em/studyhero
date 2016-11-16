from __future__ import unicode_literals
import ast, calendar

from django.db import models
from django.contrib.auth.models import User

class ListField(models.TextField):
    # __metaclass__ = models.SubfieldBase
    description = "Stores a python list"

    def __init__(self, *args, **kwargs):
        super(ListField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if not value:
            value = []

        if isinstance(value, list):
            return value

        return ast.literal_eval(value)
        
    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value;

        return ast.literal_eval(value)

    def get_prep_value(self, value):
        if value is None:
            return value

        return unicode(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_db_prep_value(value)

class Subject(models.Model):
    RED = "0"
    YELLOW = "1"
    GREEN = "2"
    BLUE = "3"
    
    COLOURS = (
        (RED, "Red"),
        (YELLOW, "Yellow"),
        (GREEN, "Green"),
        (BLUE, "Blue"),
    )
    DAYS = [(str(i), calendar.day_name[i]) for i in range(0, 5)]

    name = models.CharField(max_length=50)
    colour = models.CharField(max_length=6, choices=COLOURS)
    days = ListField()
    user = models.ForeignKey(User)
    
    def __unicode__(self):
        return self.name
        
    class Meta:
        unique_together = (
            ("user", "colour"),
            ("user", "name"),
        )

class Card(models.Model):
    title = models.CharField(max_length=128)
    subject = models.ForeignKey(Subject)
    points = models.IntegerField(default=1)
    date = models.DateField()
    user = models.ForeignKey(User)
    colour = models.CharField(max_length=6, choices=Subject.COLOURS)
    
    def __unicode__(self):
        return self.title + " " + str(self.date)
        
class StudyUser(models.Model):
    user = models.OneToOneField(User)
    points = models.IntegerField(default=0)
    multiplier = models.IntegerField(default=1)
    last_updated = models.DateField()
    
    def __unicode__(self):
        return self.user.username