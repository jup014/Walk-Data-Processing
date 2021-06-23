from django.db import models

# Create your models here.
class RawSteps(models.Model):
    local_datetime = models.DateTimeField()
    user_id = models.IntegerField()
    steps = models.IntegerField()
    
    @property
    def local_date(self):
        return self.local_datetime.date()
    
    @property
    def local_time(self):
        return self.local_datetime.time()