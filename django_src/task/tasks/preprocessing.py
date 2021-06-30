from celery import shared_task

from django.db.models import Sum, Avg, Window, F, RowRange, Value, query

from task.models import TaskLog

from data.models import RawSteps
from data.models import ThreeHour
from data.models import Predicted_Actual
from data.models import TaskInfo

from analysis.tools import T

from datetime import datetime, timedelta
import pytz
import json
import pprint
import math

        
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
def enqueue_task_2ndPhase():
    user_list = ThreeHour.objects.distinct('user_id')
        
    is_testing = False
    index = 0
    for user_obj in user_list:        
        
        analysis_2ndPhase.apply_async(
            kwargs={
                "user_id": user_obj.user_id
            }
        )
        if is_testing == True and index > 3:
            break
        index += 1


class UserDay_2ndPhase:
    class NotEnoughInputException(Exception):
        pass
    
    def __init__(self, user_id, local_date, step, window_size, threshold1):
        self.user_id = user_id
        # self.local_date = datetime.strptime(local_date, "%Y-%m-%dT%H:%M:%S")
        self.local_date = local_date
        self.step = step
        self.window_size = window_size
        self.threshold1 = threshold1
        
        self.list_three_hour = []
        
        self.__crit_method = None
        self.__crit_n_days = None
        self.__crit_list_threshold2 = None
        
        self.is_configured = False

        first_day = ThreeHour.objects.filter(user_id=self.user_id).order_by("local_date").first().local_date
        
        local_date_time_tuple = self.local_date.timetuple()
        first_day_time_tuple = first_day.timetuple()
        def get_days_since_0_0(timetuple):
            return timetuple.tm_year * 365 + timetuple.tm_yday
        
        self.index_day = get_days_since_0_0(local_date_time_tuple) - get_days_since_0_0(first_day_time_tuple)
        
        obj_query = ThreeHour.objects.filter(
            user_id=user_id, 
            local_date=self.local_date,
            step=step,
            window_size=window_size, 
            threshold1=threshold1).order_by("index_three_hour")
        
        # pprint.pprint(list(map(lambda x: x, obj_query)))
        self.list_three_hour = list(map(lambda x: x.did_walked, obj_query))
        
        # print("self.list_three_hour: {}".format(self.list_three_hour))
        
    def __str__(self):
        return "user={}, step={}, ws={}, th1={}, method={}, n_days={}, th2={}".format(
            self.user_id, self.step, self.window_size, self.threshold1,
            self.__crit_method, self.__crit_n_days, self.__crit_list_threshold2)
    
    def configure(self, method=None, n_days=None, list_threshold2=None):
        method = T.ifelse(method is None, self.__crit_method, method)
        n_days = T.ifelse(n_days is None, self.__crit_n_days, n_days)
        list_threshold2 = T.ifelse(list_threshold2 is None, self.__crit_list_threshold2, list_threshold2)
        
        if self.is_configured:
            pass
        else:
            (
                self.__crit_method,
                self.__crit_n_days,
                self.__crit_list_threshold2
            ) = (
                method,
                n_days,
                list_threshold2
            )
            
            try:
                self.__fetch()
            except UserDay_2ndPhase.NotEnoughInputException as e:
                # TaskLog.log("exception: {}".format(e), silent=True)
                pass
    
    def __fetch(self):
        previous_days = []
        
        # print(self.__crit_method)
        # print(self.__crit_n_days)
        if self.__crit_method == 0 or self.__crit_method == 2: # day-by-day or day-of-week
            if self.__crit_method == 0: # day-by-day
                date_gap = timedelta(days=1)
            else:
                date_gap = timedelta(days=7)
            for i in range(1, self.__crit_n_days + 1):
                previous_days.append(self.local_date - (date_gap * i))
        elif self.__crit_method == 1:   # weekend / weekday
            current_day = self.local_date - timedelta(days=1)
            is_weekend = self.local_date.weekday() in (5,6)
            while True:
                current_is_weekend = current_day.weekday() in (5,6)
                if current_is_weekend == is_weekend:
                    previous_days.append(current_day)
                current_day = current_day - timedelta(days=1)
                if len(previous_days) >= self.__crit_n_days:
                    break
        
        # print(previous_days)
        query_days = ThreeHour.objects.filter(
            user_id=self.user_id,
            local_date__in=previous_days,
            step=self.step,
            window_size=self.window_size,
            threshold1=self.threshold1
        ).order_by("local_date", "index_three_hour")
        # print("query_days: {}".format(query_days))
        input_n = query_days.distinct("local_date").count()
        # print("input_n: {}".format(input_n))
        if input_n != self.__crit_n_days:
            raise UserDay_2ndPhase.NotEnoughInputException("not enough input dates: input_n={}, {}".format(input_n, self))
        self.average = list(map(lambda x: x["avr"], 
                                query_days.values("index_three_hour").annotate(avr=Avg('did_walked')).order_by("index_three_hour")))
        # print(self.average)
        
    def save(self, db_queue):
        try:
            list_average = self.average
            for threshold2 in self.__crit_list_threshold2:
                # print("actual: {}".format(self.list_three_hour))
                # print("predicted: {}".format(self.average))
                dict_two_by_two_table = T.get_dict_two_by_two_table(
                    actual=self.list_three_hour,
                    predicted=list_average,
                    threshold=threshold2
                )
                T.bulk_create_enque(Predicted_Actual, 
                                    Predicted_Actual(
                                        user_id=self.user_id,
                                        index_day=self.index_day,
                                        step=self.step, 
                                        window_size=self.window_size, 
                                        threshold1=self.threshold1,
                                        method=self.__crit_method,
                                        n_days=self.__crit_n_days,
                                        threshold2=threshold2,
                                        TP=dict_two_by_two_table['TP'],
                                        TN=dict_two_by_two_table["TN"],
                                        FP=dict_two_by_two_table["FP"],
                                        FN=dict_two_by_two_table["FN"]
                                    ),
                                    db_queue
                                    )
        except AttributeError:
            pass
        
    def flush(db_queue):
        T.bulk_create_flush(Predicted_Actual, db_queue)
    

                

    
@shared_task
def analysis_2ndPhase(user_id):
    TaskLog.log("analysis_2ndPhase: user_id={}".format(user_id), silent=True)
    
    steps = [60]
    window_sizes = range(0, 7)
    threshold1s = list(map(lambda x: x/10, range(1, 11)))
    
    for step in steps:
        for window_size in window_sizes:
            for threshold1 in threshold1s:
                obj_taskinfo = TaskInfo.objects.create(
                    sig_str=pprint.pformat({
                        "user_id": user_id, 
                        # "local_date": local_date,
                        "step": step, 
                        "window_size": window_size, 
                        "threshold1": threshold1
                    })
                )
                analysis_2ndPhase_sub.apply_async(
                    kwargs={
                        "user_id": user_id, 
                        # "local_date": local_date,
                        "step": step, 
                        "window_size": window_size, 
                        "threshold1": threshold1,
                        "taskinfo_id": obj_taskinfo.id
                    }
                )
    del steps
    del window_sizes
    del threshold1s

@shared_task
def analysis_2ndPhase_sub(user_id, step, window_size, threshold1, taskinfo_id):
    # print("analysis_2ndPhase_sub: user_id={}, local_date={}, step={}, ws={}, th1={}".format(user_id, local_date, step, window_size, threshold1))
    obj_taskinfo = TaskInfo.objects.get(id=taskinfo_id)
    obj_taskinfo.when_fetched = datetime.now().astimezone(pytz.utc)
    obj_taskinfo.save()
    
    list_local_dates = list(map(lambda x: x.local_date, RawSteps.objects.filter(user_id=user_id).distinct("local_date")))
    
    db_queue = []
    
    for local_date in list_local_dates:
        obj_user_day = UserDay_2ndPhase(user_id, local_date, step, window_size, threshold1)
                    
        for index_method in range(0, 3):
            for key_n_days in range(1, 10):
                # print("configure: method={}, n_days={}".format(index_method, key_n_days))
                obj_user_day.configure(index_method, key_n_days, 
                                    list(map(lambda x: x/10, range(1, 11))))
                # print("done configure: method={}, n_days={}".format(index_method, key_n_days))
                obj_user_day.save(db_queue)
        
        del obj_user_day
    
    UserDay_2ndPhase.flush(db_queue)
        
    obj_taskinfo.when_finished = datetime.now().astimezone(pytz.utc)
    obj_taskinfo.save()