from celery import shared_task

from django.db import IntegrityError, transaction

from data.models import RawSteps, Padded_Steps, BinaryWalked, \
    AverageWalked, BinaryWalked2, ThreeHour, Predicted_Actual, \
        TaskInfo
        
from analysis.models import Aggregated1

from task.models import TaskLog

from task.tasks import aggregate2, load_data, minute_padding2, enqueue_task, enqueue_task_2ndPhase

from task.tasks import T

from datetime import datetime
import pytz
import pprint
import json

@shared_task
def bulk_delete():
    TaskInfo.objects.all().delete()
    Predicted_Actual.objects.all().delete()
    ThreeHour.objects.all().delete()
    Aggregated1.objects.all().delete()
    BinaryWalked2.objects.all().delete()
    Padded_Steps.objects.all().delete()
    BinaryWalked.objects.all().delete()
    AverageWalked.objects.all().delete()
    TaskLog.objects.all().delete()
        
class TaskExecutionService:
    def reset(self):
        bulk_delete.apply_async(kwargs={})
        return "Database is cleared."
    
    def load_data(self):
        user_list = RawSteps.objects.distinct('user_id')
        
        is_testing = False
        index = 0
        for user_obj in user_list:        
            load_data.apply_async(
                kwargs={
                    'user_id': user_obj.user_id
                }
            )
            if is_testing == True and index > 3:
                break
            index += 1
        
        return "submitted"
    
    def aggr(self):
        aggregate2.apply_async(
            kwargs={}
        )
        
        
class TaskExecutionService2:
    def prepare(self):
        enqueue_task.apply_async(kwargs={})
    
    def analysis_2ndPhase(self):
        enqueue_task_2ndPhase.apply_async(kwargs={})
    
    def view_progress(self):
        total_tasks = TaskInfo.objects.all().count()
        fetched_tasks = TaskInfo.objects.filter(when_fetched__isnull=False).count()
        finished_tasks = TaskInfo.objects.filter(when_fetched__isnull=False, when_finished__isnull=False).count()
        
        
        
        if (total_tasks > 0):
            now = datetime.now()
            first_job_fetched = TaskInfo.objects.first().when_fetched
        
            if finished_tasks > 0:
                avr_time = (now.astimezone(pytz.utc)-first_job_fetched.astimezone(pytz.utc))/finished_tasks
                unfinished_tasks = total_tasks - finished_tasks
                eta = avr_time * unfinished_tasks + now
            else:
                eta = None
                
            return {
                'total_tasks': total_tasks,
                'fetched_tasks': fetched_tasks,
                'finished_tasks': finished_tasks,
                'fetched_pct': T.ifelse(total_tasks>0, round((fetched_tasks*100)/total_tasks, 2), None),
                'finished pct': T.ifelse(total_tasks>0, round(finished_tasks*100/total_tasks, 2), None),
                'eta': eta
            }
        else:
            return {
                'total_tasks': total_tasks,
                'fetched_tasks': fetched_tasks,
                'finished_tasks': finished_tasks
            }