from django.db import models

class Task(models.Model):
    # pkey = models.AutoField(primary_key=True)
    function_name = models.CharField(max_length=255)
    params = models.TextField(blank=True)
    status = models.IntegerField(default=0)
    # 0 : submitted (not executed yet)
    # 1 : fetched (not executed yet)
    # 2 : being executed
    # 3 : completed successfully
    # 4 : finished unsuccessfully
    when_created = models.DateTimeField(auto_now_add=True)
    depends = models.ManyToManyField('self', symmetrical=False, blank=True)
    
    @property
    def func(self):
        params = self.function_name.split('.')
        
        functionname = params[-1]
        modulename = ".".join(params[0:-1])
        
        import importlib
        moduleobj = importlib.import_module(name=modulename)
        return getattr(moduleobj, functionname)

class TaskLog(models.Model):
    when_created = models.DateTimeField(auto_now_add=True)
    msg = models.TextField(blank=True)
    
    def log(msg):
        obj = TaskLog.objects.create(msg=msg)
        print(obj)
        
    def __str__(self):
        return "{}: {}".format(self.when_created, self.msg)