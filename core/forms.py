from django import forms
from .models import CalendarEvent


class CalendarEventForm(forms.ModelForm):
    class Meta:
        model = CalendarEvent
        fields = ['event_type', 'title', 'description',
                  'start_at', 'end_at', 'company', 'employee']
