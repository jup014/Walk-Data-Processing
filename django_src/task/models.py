from django.db import models

class Task(models.Model):
    pkey = models.AutoField(primary_key=True)
    function_name = models.CharField(max_length=255)
    params = models.TextField(blank=True)
    status = models.IntegerField(default=0)
    when_created = models.DateTimeField(auto_now_add=True)
    depends = models.ManyToManyField('self', symmetrical=False)
