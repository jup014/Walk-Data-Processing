from celery import shared_task

from django.db.models import Sum, Avg, Window, F, RowRange, Value

from task.models import TaskLog

from data.models import RawSteps
from data.models import Padded_Steps
from data.models import BinaryWalked
from data.models import AverageWalked

from datetime import datetime, timedelta
import pytz
import json
import pprint
import math

@shared_task
def minute_padding(args):
    TaskLog.log("minute_padding: {}".format(args))
    
    # args_dict = json.loads(args)

    # user_id = args_dict['user_id']
    user_id = args['user_id']
    
    local_date_list = RawSteps.objects.filter(
        user_id=user_id
    ).distinct('local_date')
    
    padded_steps_list = []

    for a_local_date in local_date_list:
        local_date = a_local_date.local_date
        minute_list = RawSteps.objects.filter(
            user_id=user_id,
            local_date=local_date
        ).values(
            'user_id',
            'local_datetime',
            'local_date',
            'local_time'
        ).annotate(
            steps2=Sum('steps')
        )
        
        padded_list = [0] * 1440
        
        for a_minute in minute_list:
            local_time = a_minute["local_time"]
            list_index = local_time.hour * 60 + local_time.minute
            padded_list[list_index] += a_minute["steps2"]
        
        for i in range(0, 1440):
            local_datetime = datetime(
                year=local_date.year,
                month=local_date.month,
                day=local_date.day).astimezone(pytz.utc) + timedelta(hours=math.floor(i/60), minutes=(i%60))
            padded_steps_list.append(Padded_Steps(
                local_datetime=local_datetime,
                user_id=user_id,
                steps=padded_list[i],
                local_date=local_date,
                local_time=local_datetime.time()
            ))
        
    Padded_Steps.objects.bulk_create(padded_steps_list)
    
    binarize.apply_async(
        kwargs={
            "user_id": user_id
        }
    )
    
@shared_task
def binarize(user_id):
    TaskLog.log("binarize: user_id={}".format(user_id))
    
    obj_list = Padded_Steps.objects.filter(
        user_id=user_id
    )
    
    def if_x_then_this_else_that(x, this, that):
        if x:
            return this
        else:
            return that
        
    insert_obj_list = []
    for obj in obj_list:
        insert_obj_list.append(
            BinaryWalked(
                local_datetime=obj.local_datetime,
                user_id=obj.user_id,
                did_walked=if_x_then_this_else_that(obj.steps>60, 1, 0), 
                local_date=obj.local_date,
                local_time=obj.local_time
            )
        )
    
    BinaryWalked.objects.bulk_create(insert_obj_list)
    
    average_walk.apply_async(
        kwargs={
            "user_id": user_id
        }
    )

@shared_task
def average_walk(user_id):
    obj_list = BinaryWalked.objects.filter(
        user_id=user_id
    ).order_by("local_datetime")
    
    for n_days in range(0, 10):
        TaskLog.log("  average_walk: user_id={}, n_days={}".format(user_id, n_days))
        insert_obj_list = []
        
        new_obj_list = obj_list.annotate(
            window_size=Value(n_days)
        ).annotate(
            mean_did_walked=Window(
                expression=Avg('did_walked'),
                order_by=F("local_datetime").asc(),
                frame=RowRange(start=(-n_days),end=n_days)
            )
        )
        
        for new_obj in new_obj_list:
            insert_obj_list.append(
                AverageWalked(
                    local_datetime=new_obj.local_datetime,
                    user_id=new_obj.user_id,
                    mean_did_walked=new_obj.mean_did_walked,
                    local_date=new_obj.local_date,
                    local_time=new_obj.local_time,
                    window_size=new_obj.window_size
                )
            )
        
        AverageWalked.objects.bulk_create(insert_obj_list)
    
    