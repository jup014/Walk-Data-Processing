from django.db import models

# Create your models here.
class Aggregated1(models.Model):
    index_day = models.IntegerField()
    index_method = models.IntegerField()
    key_n_days = models.IntegerField()
    key_window_size = models.IntegerField()
    key_threshold1 = models.FloatField()
    key_threshold2 = models.FloatField()
    TP = models.IntegerField()
    TN = models.IntegerField()
    FP = models.IntegerField()
    FN = models.IntegerField()
    
    class Meta:
        indexes = [
            models.Index(fields=['index_day', 'index_method', 'key_n_days', 'key_window_size', 'key_threshold1', 'key_threshold2',])
        ]
    
# class Aggregated2(models.Model):
#     index_method = models.IntegerField()
#     key_n_days = models.IntegerField()
#     key_window_size = models.IntegerField()
#     key_threshold1 = models.FloatField()
#     key_threshold2 = models.FloatField()
#     TP = models.IntegerField()
#     TN = models.IntegerField()
#     FP = models.IntegerField()
#     FN = models.IntegerField()
    
#     class Meta:
#         indexes = [
#             models.Index(fields=['index_method', 'key_n_days', 'key_window_size', 'key_threshold1', 'key_threshold2',])
#         ]