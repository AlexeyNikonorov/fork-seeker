from __future__ import unicode_literals
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Event(models.Model):
    sport = models.CharField(max_length=200)
    team_home = models.CharField(max_length=200)
    team_away = models.CharField(max_length=200)
    bet_home = models.CharField(max_length=200)
    bet_draw = models.CharField(max_length=200)
    bet_away = models.CharField(max_length=200)
    
    def __str__(self):
        return '%s v %s' % (self.team_home, self.team_away)
