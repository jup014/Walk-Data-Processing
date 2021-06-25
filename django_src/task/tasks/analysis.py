from celery import shared_task

from django.db.models import Sum, Avg, Window, F, RowRange, Value

from task.models import TaskLog

from data.models import RawSteps
from data.models import Padded_Steps
from data.models import BinaryWalked
from data.models import AverageWalked
from data.models import BinaryWalked2

from analysis.tools import T, WalkingDataAnalysis
from analysis.models import Aggregated1

from datetime import datetime, timedelta
import pytz
import json
import pprint
import math


@shared_task
def load_data(user_id):
    TaskLog.log("load_data: {}".format(user_id))
    
    tool = WalkingDataAnalysis(debug=False)
    
    tool.load_data(
        RawSteps.objects.filter(
            user_id=user_id
        )
    )

@shared_task
def aggregate2():
    aggr1 = Aggregated1.objects.values(
        'index_day',
        'index_method',
        'key_n_days',
        'key_window_size',
        'key_threshold1',
        'key_threshold2',
    ).annotate(
        TP=Sum('TP')
    ).annotate(
        TN=Sum('TN')
    ).annotate(
        FP=Sum('FP')
    ).annotate(
        FN=Sum('FN')
    )
    
    aggr2 = Aggregated1.objects.values(
        'index_method',
        'key_n_days',
        'key_window_size',
        'key_threshold1',
        'key_threshold2',
    ).annotate(
        TP=Sum('TP')
    ).annotate(
        TN=Sum('TN')
    ).annotate(
        FP=Sum('FP')
    ).annotate(
        FN=Sum('FN')
    )
    
    T.export_csv_obj_list("aggr1.csv", aggr1)
    T.export_csv_obj_list("aggr2.csv", aggr2)
    