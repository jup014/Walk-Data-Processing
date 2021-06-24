from django.db import models

class TaskLog(models.Model):
    when_created = models.DateTimeField(auto_now_add=True)
    msg = models.TextField(blank=True)
    
    def log(msg, silent=False):
        obj = TaskLog.objects.create(msg=msg)
        if not silent:
            print(obj)
        
    def __str__(self):
        return "{}: {}".format(self.when_created, self.msg)