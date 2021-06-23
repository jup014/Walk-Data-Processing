from django.db import models

class RawSteps(models.Model):
    local_datetime = models.DateTimeField()
    user_id = models.IntegerField()
    steps = models.IntegerField()
    local_date = models.DateField(null=True, blank=True)
    local_time = models.TimeField(null=True, blank=True)
    
class Padded_Steps(models.Model):
    local_datetime = models.DateTimeField()
    user_id = models.IntegerField()
    steps = models.IntegerField()
    local_date = models.DateField(null=True, blank=True)
    local_time = models.TimeField(null=True, blank=True)