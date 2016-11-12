from __future__ import unicode_literals

from django.db import models
import ast, calendar

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
    RED = "#FFB5B9"
    ORANGE = "#FFE6BF"
    YELLOW = "#FFEDB5"
    GREEN = "#B5F2BA"
    BLUE = "#BFDAFF"
    INDIGO = "#DABFFF"
    VIOLET = "#FBBFFF"
    
    COLOURS = (
        (RED, "Red"),
        (ORANGE, "Orange"),
        (YELLOW, "Yellow"),
        (GREEN, "Green"),
        (BLUE, "Blue"),
        (INDIGO, "Indigo"),
        (VIOLET, "Violet")
    )
    DAYS = [(str(i), calendar.day_name[i]) for i in range(0, 5)]

    name = models.CharField(max_length=50, unique=True)
    colour = models.CharField(max_length=7, choices=COLOURS, unique=True)
    days = ListField()
    
    def __unicode__(self):
        return self.name

class Card(models.Model):
    title = models.CharField(max_length=128)
    subject = models.ForeignKey(Subject)
    points = models.IntegerField(default=1)
    date = models.DateField()
    
    def __unicode__(self):
        return self.title + " " + str(self.date)