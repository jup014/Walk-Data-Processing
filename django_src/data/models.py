from django.db import models

class Task(models.Model):
    pkey = models.AutoField(primary_key=True)
    function_name = models.CharField(max_length=255)
    params = models.TextField(blank=True)
    status = models.IntegerField()
    when_created = models.DateTimeField(auto_now_add=True)
    depends = models.ManyToManyField('self', symmetrical=False)

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
    
class Padded_Steps(RawSteps):
    pass

