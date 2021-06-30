import math
import copy
import sys
import pprint
import csv
import psutil
import os

from django.db.models import Sum, Avg, Window, F, RowRange, Value

from analysis.models import Aggregated1

from task.models import TaskLog

import gc

class T:
    def getList(key, iterable):
        return list(map(lambda x: getattr(x, key), iterable))
    
    def get_dict_two_by_two_table(actual, predicted, threshold):
        dict_return = {
            "TP": 0,
            "TN": 0,
            "FP": 0,
            "FN": 0
        }
        for i in range(len(actual)):
            if actual[i] == 1:
                if predicted[i] > threshold:
                    dict_return['TP'] += 1
                else:
                    dict_return['FN'] += 1
            else:
                if predicted[i] > threshold:
                    dict_return['FP'] += 1
                else:
                    dict_return['TN'] += 1
        return dict_return
                    
    
    def get_window_average(list_obj, i, window_size):
        index_start = i - window_size
        index_start = T.ifelse(index_start<0, 0, index_start)
        index_end = i + window_size
        index_end = T.ifelse(index_end>=1440, 1439, index_end)
        
        sum = 0
        
        for index_minute in range(index_start, index_end+1):
            sum += list_obj[index_minute]
        
        return sum / (window_size * 2 + 1)
    
    def get_minute_index(time):
        return time.hour * 60 + time.minute

    def ifelse(x, this, that):
        if x:
            return this
        else:
            return that
    
    def export_csv_obj_list(filename, csv_obj_list):
        with open(filename, "w") as f:
            csvwriter = csv.DictWriter(f, sorted(csv_obj_list[0].keys()))
            csvwriter.writeheader()
            csvwriter.writerows(csv_obj_list)
    
    def gc():
        process = psutil.Process(os.getpid())
        before_b = math.floor(process.memory_info().rss / 1000000)  # in MB
        before = gc.get_count()
        gc.collect()
        process = psutil.Process(os.getpid())
        after_b = math.floor(process.memory_info().rss / 1000000) # in MB
        after = gc.get_count()
        TaskLog.log("{}/{}MB -> {}/{}MB".format(before, before_b, after, after_b), silent=True)
        
    
    def bulk_create_flush(class_name, obj_list):
        class_name.objects.bulk_create(obj_list)
        TaskLog.log("{} bulk create list is flushed: {} items".format(class_name, len(obj_list)), silent=True)
        del obj_list[:]
        T.gc()

    def bulk_create_enque(class_name, obj, obj_list, commit_count=100000):
        if len(obj_list) >= commit_count:
            T.bulk_create_flush(class_name, obj_list)
        else:
            obj_list.append(obj)

class WalkingDataAnalysis:
    def __init__(self, debug=True):
        self.debug = debug
        self.raw_data = {}
        self.pad_criteria = 60
        self.max_window_size = 10
        self.threshold1_denominator = 10
        self.methods = ["day by day", "weekday/weekend", "day of a week"]
        self.max_n_days = 7
        self.threshold2_denominator = 10
    
    def load_data(self, queryset):
        TaskLog.log("Beginning the loading and padding: {}".format(sys.getsizeof(self)), silent=True)
        for obj in queryset.all():
            index_minute = T.get_minute_index(obj.local_time)
            if not (obj.local_date in self.raw_data):
                self.raw_data[obj.local_date] = [0] * 1440
            self.raw_data[obj.local_date][index_minute] += obj.steps
            
        self.__binarize()
        T.gc()
        self.__average_window()
        T.gc()
        self.__binarize2()
        T.gc()
        self.__cluster_three_hours()
        T.gc()
        self.__prepare_params()
        T.gc()
        self.__apply_params()
        T.gc()
        self.__aggregate()
        T.gc()
        self.__db_save()
        T.gc()
    
    def __binarize(self):
        TaskLog.log("Beginning the binarizing: {}".format(sys.getsizeof(self)), silent=True)
        self.binary1 = {}
        
        for key_date in self.raw_data:
            self.binary1[key_date] = list(self.raw_data[key_date])
            for index_minute in range(0, 1440):
                self.binary1[key_date][index_minute] = T.ifelse(self.binary1[key_date][index_minute] > self.pad_criteria, 1, 0)
        
        if not self.debug:
            del self.raw_data
        
    def __average_window(self):
        TaskLog.log("Beginning the averaging: {}".format(sys.getsizeof(self)), silent=True)
        self.average_window = {}
        
        for window_size in range(0, self.max_window_size + 1):
            self.average_window[window_size] = copy.deepcopy(self.binary1)
        
        for window_size in range(1, self.max_window_size + 1):
            for offset_minute in range(window_size, self.max_window_size + 1):
                for index_minute in range(0, 1440):
                    before_index_minute = index_minute - offset_minute
                    after_index_minute = index_minute + offset_minute
                    
                    for key_date in self.average_window[window_size]:
                        if before_index_minute >= 0:
                            self.average_window[window_size][key_date][index_minute] += self.binary1[key_date][before_index_minute]
                        
                        if after_index_minute < 1440:
                            self.average_window[window_size][key_date][index_minute] += self.binary1[key_date][after_index_minute]
        
        for key_window_size, dict_window_size in self.average_window.items():
            for key_date in dict_window_size:
                for index_minute in range(0, 1440):
                    self.average_window[key_window_size][key_date][index_minute] /= (1+2*key_window_size)
        
        if not self.debug:
            del self.binary1            

    
    def __binarize2(self):
        TaskLog.log("Beginning the binarizing 2: {}".format(sys.getsizeof(self)), silent=True)
        self.binary2 = {}
        
        for threshold1_raw in range(1, self.threshold1_denominator + 1):
            key_threshold1 = threshold1_raw / self.threshold1_denominator
            
            self.binary2[key_threshold1] = copy.deepcopy(self.average_window)
        
        for key_threshold1, dict_threshold1 in self.binary2.items():
            for key_window_size, dict_window_size in dict_threshold1.items():
                for key_date, list_date in dict_window_size.items():
                    for index_minute in range(0, 1440):
                        self.binary2[key_threshold1][key_window_size][key_date][index_minute] = T.ifelse(
                            list_date[index_minute] > key_threshold1,
                            1, 0
                        )

        if not self.debug:
            del self.average_window
    
    def __cluster_three_hours(self):
        TaskLog.log("Beginning the clustering to three hours: {}".format(sys.getsizeof(self)), silent=True)
        self.three_hour = {}
        
        for key_threshold1, dict_threshold1 in self.binary2.items():
            self.three_hour[key_threshold1] = {}
            
            for key_window_size, dict_window_size in dict_threshold1.items():
                self.three_hour[key_threshold1][key_window_size] = {}
                
                for key_date, list_date in dict_window_size.items():
                    self.three_hour[key_threshold1][key_window_size][key_date] = [0] * 8
                    
                    for index_three_hour in range(0, 1440, 180):
                        sum = 0
                        for offset_minute in range(0, 180):
                            sum += list_date[index_three_hour + offset_minute]
                        self.three_hour[key_threshold1][key_window_size][key_date][math.floor(index_three_hour / 180)] = T.ifelse(sum > 0, 1, 0)
        
        if not self.debug:
            del self.binary2
        
    
    def __prepare_params(self):
        TaskLog.log("Beginning the preparing params: {}".format(sys.getsizeof(self)), silent=True)
        
        self.params = []
        
        _, dict_first_threshold1 = next(iter(self.three_hour.items()))
        _, dict_first_window_size = next(iter(dict_first_threshold1.items()))
        key_first_date = next(iter(dict_first_window_size))
        
        dict_date_info = {}
        dict_info_date = {}
        
        for key_date in dict_first_window_size:
            index_day = (key_date - key_first_date).days
            weekday_N = key_date.weekday()
            is_weekend = (weekday_N in (5, 6))
            list_info = [
                1,
                is_weekend,
                weekday_N
                ]
            
            dict_date_info[key_date] = {
                "index_day": index_day,
                "info": list_info
            }
            
            for index_method, _ in enumerate(self.methods):
                value_info = list_info[index_method]
                
                if not(index_method in dict_info_date):
                    dict_info_date[index_method] = {}
                if not (value_info in dict_info_date[index_method]):
                    dict_info_date[index_method][value_info] = []
                
                dict_info_date[index_method][value_info].append(key_date)
            
        for index_method, _ in enumerate(self.methods):
            for key_date in dict_first_window_size:
                value_date_info = dict_date_info[key_date]["info"][index_method]
                
                list_date_same_info = dict_info_date[index_method][value_date_info]
                
                index_date_same_info = list_date_same_info.index(key_date)
                
                for key_n_days in range(1, self.max_n_days + 1):
                    if key_n_days <= index_date_same_info:
                        self.params.append(
                            {
                                "key_date": key_date,
                                "index_day": dict_date_info[key_date]["index_day"],
                                "index_method": index_method,
                                "key_n_days": key_n_days
                            }
                        )
        self.dict_date_info = dict_date_info
        self.dict_info_date = dict_info_date
        
        # print("self.dict_date_info:")
        # pprint.pprint(self.dict_date_info)
        
        # print("self.dict_info_date:")
        # pprint.pprint(self.dict_info_date)
        
        # T.export_csv_obj_list("params.csv", self.params)
        
        
    
    def __apply_params(self):
        TaskLog.log("Beginning the applying params: {}".format(sys.getsizeof(self)), silent=True)
        self.list_result = []
        
        for value_param in self.params:
            key_date = value_param["key_date"]
            index_day = value_param["index_day"]
            index_method = value_param["index_method"]
            key_n_days = value_param["key_n_days"]
            
            value_date_info = self.dict_date_info[key_date]["info"][index_method]
            list_date_same_info = self.dict_info_date[index_method][value_date_info]
                
            index_date_same_info = list_date_same_info.index(key_date)
            
            # three hour reference:
            #  self.three_hour[key_threshold1][key_window_size][key_date][math.floor(index_three_hour / 180)] = T.if_x_then_this_else_that(sum > 0, 1, 0)
            
            for key_threshold1, dict_threshold1 in self.three_hour.items():
                for key_window_size, dict_window_size in dict_threshold1.items():
                    for index_three_hour, _ in enumerate(dict_window_size[key_date]):
                        sum = 0
                        
                        index_date_same_info_start = index_date_same_info - key_n_days
                        
                        for index_date_same_info_current in range(index_date_same_info_start, index_date_same_info):
                            key_date_current = list_date_same_info[index_date_same_info_current]
                            sum += dict_window_size[key_date_current][index_three_hour]
                        

                        
                        for raw_threshold2 in range(1, self.threshold2_denominator + 1):
                            threshold2 = raw_threshold2 / self.threshold2_denominator
                            
                            dict_result = {}
                            for k, v in value_param.items():
                                dict_result[k] = v
                        
                            dict_result["key_threshold1"] = key_threshold1
                            dict_result["key_window_size"] = key_window_size
                            dict_result["index_three_hour"] = index_three_hour
                            
                            dict_result["key_threshold2"] = threshold2
                            
                            dict_result["predicted"] = T.ifelse(
                                (sum / key_n_days) > threshold2,
                                1, 0
                            )
                            dict_result["actual"] = dict_window_size[key_date][index_three_hour]
                            
                            self.list_result.append(dict_result)
                            
        # T.export_csv_obj_list("results.csv", self.list_result)
        
        del self.params
    
        
    
    def __aggregate(self):
        TaskLog.log("Beginning the aggregating results: {}".format(sys.getsizeof(self)), silent=True)
        self.aggregated_result_1 = {}
        self.list_aggregated_result_1 = []
        
        for dict_result in self.list_result:
            index_day = dict_result["index_day"]
            index_method = dict_result["index_method"]
            key_n_days = dict_result["key_n_days"]
            key_window_size = dict_result["key_window_size"]
            key_threshold1 = dict_result["key_threshold1"]
            key_threshold2 = dict_result["key_threshold2"]
            
            dict_two_by_two_table = {
                "TP": 0,
                "TN": 0,
                "FP": 0,
                "FN": 0
            }
            
            if not (index_day in self.aggregated_result_1):
                self.aggregated_result_1[index_day] = {}
            
            if not (index_method in self.aggregated_result_1[index_day]):
                self.aggregated_result_1[index_day][index_method] = {}
            
            if not (key_n_days in self.aggregated_result_1[index_day][index_method]):
                self.aggregated_result_1[index_day][index_method][key_n_days] = {}

            if not (key_window_size in self.aggregated_result_1[index_day][index_method][key_n_days]):
                self.aggregated_result_1[index_day][index_method][key_n_days][key_window_size] = {}

            if not (key_threshold1 in self.aggregated_result_1[index_day][index_method][key_n_days][key_window_size]):
                self.aggregated_result_1[index_day][index_method][key_n_days][key_window_size][key_threshold1] = {}
                
            if not (key_threshold2 in self.aggregated_result_1[index_day][index_method][key_n_days][key_window_size][key_threshold1]):
                self.aggregated_result_1[index_day][index_method][key_n_days][key_window_size][key_threshold1][key_threshold2] = copy.deepcopy(dict_two_by_two_table)
                

            if dict_result["actual"] == 1 and dict_result["predicted"] == 1:
                self.aggregated_result_1[index_day][index_method][key_n_days][key_window_size][key_threshold1][key_threshold2]["TP"] += 1
            elif dict_result["actual"] == 1 and dict_result["predicted"] == 0:
                self.aggregated_result_1[index_day][index_method][key_n_days][key_window_size][key_threshold1][key_threshold2]["FN"] += 1
            elif dict_result["actual"] == 0 and dict_result["predicted"] == 0:
                self.aggregated_result_1[index_day][index_method][key_n_days][key_window_size][key_threshold1][key_threshold2]["TN"] += 1
            elif dict_result["actual"] == 0 and dict_result["predicted"] == 1:
                self.aggregated_result_1[index_day][index_method][key_n_days][key_window_size][key_threshold1][key_threshold2]["FP"] += 1
                
        for index_day, dict_day in self.aggregated_result_1.items():
            for index_method, dict_method in dict_day.items():
                for key_n_days, dict_n_days in dict_method.items():
                    for key_window_size, dict_window_size in dict_n_days.items():
                        for key_threshold1, dict_threshold1 in dict_window_size.items():
                            for key_threshold2, dict_threshold2 in dict_threshold1.items():
                                self.list_aggregated_result_1.append(
                                    {
                                        "index_day": index_day,
                                        "index_method": index_method,
                                        "key_n_days": key_n_days,
                                        "key_window_size": key_window_size,
                                        "key_threshold1": key_threshold1,
                                        "key_threshold2": key_threshold2,
                                        "TP": dict_threshold2["TP"],
                                        "FP": dict_threshold2["FP"],
                                        "TN": dict_threshold2["TN"],
                                        "FN": dict_threshold2["FN"]
                                    }
                                )
                                
        del self.aggregated_result_1
    
    def __db_save(self):
        TaskLog.log("Beginning the db saving: {}".format(sys.getsizeof(self)), silent=True)
        aggr1 = []
        for item_aggr1 in self.list_aggregated_result_1:
            T.bulk_create_enque(
                Aggregated1, 
                Aggregated1(
                    index_day = item_aggr1["index_day"],
                    index_method = item_aggr1["index_method"],
                    key_n_days = item_aggr1["key_n_days"],
                    key_window_size = item_aggr1["key_window_size"],
                    key_threshold1 = item_aggr1["key_threshold1"],
                    key_threshold2 = item_aggr1["key_threshold2"],
                    TP = item_aggr1["TP"],
                    TN = item_aggr1["TN"],
                    FP = item_aggr1["FP"],
                    FN = item_aggr1["FN"]    
                ),
                aggr1, 
                commit_count=10000
            )
        T.bulk_create_flush(Aggregated1, aggr1)
        
