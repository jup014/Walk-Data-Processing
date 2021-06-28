from celery import shared_task

from django.db.models import Sum, Avg, Window, F, RowRange, Value

from task.models import TaskLog

from data.models import RawSteps
from data.models import Padded_Steps
from data.models import BinaryWalked
from data.models import AverageWalked
from data.models import BinaryWalked2

from data.models import ThreeHour

from analysis.tools import T

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
            
            T.bulk_create_enque(Padded_Steps, 
                              Padded_Steps(
                                  local_datetime=local_datetime,
                                  user_id=user_id,
                                  steps=padded_list[i],
                                  local_date=local_date,
                                  local_time=local_datetime.time()
                                  ),
                              padded_steps_list
                              )
            
    T.bulk_create_flush(Padded_Steps, padded_steps_list)
    
    binarize.apply_async(
        kwargs={
            "user_id": user_id
        }
    )
    
    
    
class UserDay:
    def __init__(self, user_id, local_date):
        self.user_id = user_id
        self.local_date = datetime.strptime(local_date, "%Y-%m-%dT%H:%M:%S")
        self.list_step = [0] * 1440
        self.db_queue = []
        
        self.__crit_step = None
        self.__crit_window_size = None
        self.__crit_threshold1 = None
        
        self.is_configured = False
        
    def configure(self, 
                  step=None, 
                  window_size=None,
                  threshold1=None):
        step = T.ifelse(step is None, 
                        self.__crit_step, 
                        step)
        window_size = T.ifelse(window_size is None, 
                               self.__crit_window_size, 
                               window_size)
        threshold1 = T.ifelse(threshold1 is None, 
                              self.__crit_threshold1, 
                              threshold1)
        
        if self.is_configured:
            if self.__crit_step != step:
                del self.binary1
                del self.average1
                del self.binary2
                del self.three_hour
                (
                    self.__crit_step, 
                    self.__crit_window_size, 
                    self.__crit_threshold1
                ) = (
                    step,
                    window_size,
                    threshold1
                )
                    
                self.__binarize()
            elif self.__crit_window_size != window_size:
                del self.average1
                del self.binary2
                del self.three_hour
                (
                    self.__crit_window_size, 
                    self.__crit_threshold1
                ) = (
                    window_size,
                    threshold1
                )
                self.__average()
            elif self.__crit_threshold1 != threshold1:
                del self.binary2
                del self.three_hour
                (
                    self.__crit_threshold1
                ) = (
                    threshold1
                )
                self.__binarize2()
            else:
                pass    # no crit has been changed, do nothing
        else:
            (
                self.__crit_step, 
                self.__crit_window_size, 
                self.__crit_threshold1
            ) = (
                step,
                window_size,
                threshold1
            )
                
            self.__binarize()
        self.is_configured = True
    
    def force_recalc(self):
        if self.is_configured:
            try:
                self.binary1
            except AttributeError:
                pass
            else:
                del self.binary1
            
            try:
                self.average1
            except AttributeError:
                pass
            else:
                del self.average1
            
            try:
                self.binary2
            except AttributeError:
                pass
            else:
                del self.binary2
            
            try:
                self.three_hour
            except AttributeError:
                pass
            else:
                del self.three_hour
            
            self.__binarize()
        else:
            raise RuntimeError(
                "Not configured yet. Please run configure(...) first.")
        
    def __binarize(self):
        try:
            self.binary1
        except AttributeError:
            pass
        else:
            del self.binary1
        
        self.binary1 = list(map(
            lambda x: T.ifelse(x > self.__crit_step, 1, 0), 
            self.list_step))
        
        self.__average()
        
    def __average(self):
        try:
            self.average1
        except AttributeError:
            pass
        else:
            del self.average1
        
        self.average1 = [0] * 1440
        
        for i in range(0, 1440):
            self.average1[i] = T.get_window_average(self.binary1, i, self.__crit_window_size)
        
        self.__binarize2()
    
    def __binarize2(self):
        try:
            self.binary2
        except AttributeError:
            pass
        else:
            del self.binary2
            
        self.binary2 = list(map(
            lambda x: x > self.__crit_threshold1, 
            self.average1))
        
        self.__aggregate()
    
    def __aggregate(self):
        try:
            self.three_hour
        except:
            pass
        else:
            del self.three_hour
        
        self.three_hour = [0] * 8
        for index_three_hour in range(0, 8):
            self.three_hour[index_three_hour] = T.ifelse(
                sum(self.binary2[(index_three_hour * 180):((index_three_hour + 1) * 180)]) > 0,
                1, 0
            )
        
    def add(self, time, steps):
        index_minute = T.get_minute_index(time)
        self.list_step[index_minute] += steps
    
    def save(self):
        if not self.is_configured:
            self.configure(
                step=60,
                window_size=3,
                threshold1=0.6
            )
        
        list_three_hour = self.get_db_obj_list()
        for obj_three_hour in list_three_hour:
            T.bulk_create_enque(ThreeHour, obj_three_hour, self.db_queue, commit_count=10000)
    
    def flush(self):
        T.bulk_create_flush(ThreeHour, self.db_queue)
    
    def get_db_obj_list(self):
        if self.is_configured:
            list_return = []
            
            for index_three_hour in range(0, 8):
                list_return.append(ThreeHour(
                    user_id=self.user_id,
                    local_date=self.local_date,
                    step = self.__crit_step,
                    window_size = self.__crit_window_size,
                    threshold1 = self.__crit_threshold1,
                    index_three_hour = index_three_hour,
                    did_walked = self.three_hour[index_three_hour]
                ))
            return list_return
        else:
            raise RuntimeError("This object is not configured.")
        
@shared_task
def enqueue_task():
    user_list = RawSteps.objects.distinct('user_id', 'local_date')
        
    is_testing = False
    index = 0
    for user_obj in user_list:        
        
        minute_padding2.apply_async(
            kwargs={
                "user_id": user_obj.user_id,
                "local_date": user_obj.local_datetime.date()
            }
        )
        if is_testing == True and index > 3:
            break
        index += 1

@shared_task
def enqueue_task2():
    user_list = ThreeHour.objects.distinct('user_id', 'local_date')
        
    is_testing = False
    index = 0
    for user_obj in user_list:        
        
        minute_padding2.apply_async(
            kwargs={
                "user_id": user_obj.user_id,
                "local_date": user_obj.local_datetime.date()
            }
        )
        if is_testing == True and index > 3:
            break
        index += 1
    
@shared_task
def minute_padding2(user_id, local_date):
    TaskLog.log("minute_padding2: user_id={}, local_date={}".format(user_id, local_date), silent=True)
    obj_user_day = UserDay(user_id, local_date)
    minute_list = RawSteps.objects.filter(
            user_id=user_id,
            local_date=datetime.strptime(local_date, "%Y-%m-%dT%H:%M:%S")
            ).values('local_time', 'steps')
            
    for a_minute in minute_list:
        obj_user_day.add(a_minute["local_time"], a_minute["steps"])
    del minute_list
        
    for window_size in range(0, 7):
        for threshold1_raw in range(1, 10):
            threshold1 = threshold1_raw/10
            obj_user_day.configure(step=60, window_size=window_size, threshold1=threshold1)
            obj_user_day.save()
    obj_user_day.flush()
    del obj_user_day
    
    
    
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
        T.bulk_create_enque(
            BinaryWalked,
            BinaryWalked(
                local_datetime=obj.local_datetime,
                user_id=obj.user_id,
                did_walked=if_x_then_this_else_that(obj.steps>60, 1, 0), 
                local_date=obj.local_date,
                local_time=obj.local_time
            ),
            insert_obj_list
        )
    
    T.bulk_create_flush(BinaryWalked, insert_obj_list)
    
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
    
    insert_obj_list = []
    
    for n_days in range(0, 10):
        TaskLog.log("  average_walk: user_id={}, n_days={}".format(user_id, n_days))
        
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
            T.bulk_create_enque(
                AverageWalked,
                AverageWalked(
                    local_datetime=new_obj.local_datetime,
                    user_id=new_obj.user_id,
                    mean_did_walked=new_obj.mean_did_walked,
                    local_date=new_obj.local_date,
                    local_time=new_obj.local_time,
                    window_size=new_obj.window_size
                ),
                insert_obj_list
            )
    
    T.bulk_create_flush(AverageWalked, insert_obj_list)
    
    binarize2.apply_async(
        kwargs={
            "user_id": user_id
        }
    )


@shared_task
def binarize2(user_id):
    obj_list = AverageWalked.objects.filter(
        user_id=user_id
    )
    
    def if_x_then_this_else_that(x, this, that):
        if x:
            return this
        else:
            return that
        
    insert_obj_list = []
    for threshold1 in range(1, 11):
        TaskLog.log("binarize2: user_id={}, threshold1={}".format(user_id, threshold1 * 0.1))
        for obj in obj_list:
            T.bulk_create_enque(BinaryWalked2,
                BinaryWalked2(
                    local_datetime=obj.local_datetime,
                    user_id=obj.user_id,
                    did_walked=if_x_then_this_else_that(obj.mean_did_walked>(threshold1*0.1), 1, 0), 
                    local_date=obj.local_date,
                    local_time=obj.local_time,
                    window_size=obj.window_size,
                    threshold1=(threshold1 * 0.1)
                ),
                insert_obj_list
            )
        
    T.bulk_create_flush(BinaryWalked2, insert_obj_list)
    