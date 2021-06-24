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
    
class BinaryWalked(models.Model):
    local_datetime = models.DateTimeField()
    user_id = models.IntegerField()
    did_walked = models.IntegerField()
    local_date = models.DateField(null=True, blank=True)
    local_time = models.TimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['local_datetime', 'user_id',]),
            models.Index(fields=['user_id','local_datetime'])
        ]

class AverageWalked(models.Model):
    local_datetime = models.DateTimeField()
    user_id = models.IntegerField()
    mean_did_walked = models.FloatField()
    local_date = models.DateField(null=True, blank=True)
    local_time = models.TimeField(null=True, blank=True)
    window_size = models.IntegerField()
