from django import forms
from django.db import models
from apps.events.models import Event
from apps.users.models import ERPProfile
import select2.fields


class AddEventForm(forms.ModelForm):
    coords = select2.fields.MultipleChoiceField(choices=ERPProfile.objects.as_choices(),overlay="Choose a coord...")
    class Meta:
        model = Event
        fields=('name','is_visible','short_description','event_type','category','has_tdp','team_size_min','team_size_max','registration_starts','registration_ends','google_group','email','coords',)
