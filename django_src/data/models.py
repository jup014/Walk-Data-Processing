from django.db import models
import pprint

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

    def __str__(self):
        return "{} - user_id={}, n={}, m={}".format(self.local_datetime, self.user_id, self.window_size, self.mean_did_walked)
    
class BinaryWalked2(models.Model):
    local_datetime = models.DateTimeField()
    user_id = models.IntegerField()
    did_walked = models.IntegerField()
    local_date = models.DateField(null=True, blank=True)
    local_time = models.TimeField(null=True, blank=True)
    window_size = models.IntegerField()
    threshold1 = models.FloatField()

    def __str__(self):
        return "{} - user_id={}, n={}, m={}".format(self.local_datetime, self.user_id, self.window_size, self.did_walked)
    




class ThreeHour(models.Model):
    user_id = models.IntegerField()
    local_date = models.DateField()
    step = models.IntegerField()
    window_size = models.IntegerField()
    threshold1 = models.FloatField()
    index_three_hour = models.IntegerField()
    did_walked = models.IntegerField()
    
    def __str__(self):
        return "user_id={}, local_date={}, step={}, window_size={}, threshold1={}, index_three_hour={}, did_walked={}". \
            format(self.user_id, self.local_date, self.step, self.window_size, self.threshold1, self.index_three_hour, self.did_walked)
    
    class Meta:
        indexes = [
            models.Index(fields=['user_id', 'local_date', 'step', 'window_size', 'threshold1'])
        ]

class Predicted_Actual(models.Model):
    user_id = models.IntegerField()
    index_day = models.IntegerField()
    step = models.IntegerField()
    window_size = models.IntegerField()
    threshold1 = models.FloatField()
    method = models.IntegerField()
    n_days = models.IntegerField()
    threshold2 = models.FloatField()
    TP = models.IntegerField()
    TN = models.IntegerField()
    FP = models.IntegerField()
    FN = models.IntegerField()
    
    
    def __str__(self):
        # return pprint.pformat(list(map(lambda x: getattr(self, x), 
        #                                self.__dict__.keys())))
        return pprint.pformat(self.__dict__)


class TaskInfo(models.Model):
    when_created = models.DateTimeField(auto_now_add=True)
    when_fetched = models.DateTimeField(null=True, blank=True)
    when_finished = models.DateTimeField(null=True, blank=True)
    sig_str = models.TextField(null=True, blank=True)