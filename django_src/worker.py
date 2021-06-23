import os
import django
os.environ['DJANGO_SETTINGS_MODULE'] = 'walk_data_processing.settings'
django.setup()


import pprint
import time
from data.models import RawSteps
from task.services import TaskFetcherService
from task.models import TaskLog

service = TaskFetcherService()

TaskLog.log('worker initiated')

no_further_job_print = False

from task.tasks import minute_padding

# # one-time
# for i in range(1, 100):
#     task = service.get_next_task()
#     if task:
#         task.func(task.params)

# loop
while True:
    task = service.get_next_task()

    if task:
        no_further_job_print = False
        task.status = 2
        task.save()
        task.func(task.params)
        task.status = 3
        task.save()
    else:
        if not no_further_job_print:
            TaskLog.log("No further job")
            no_further_job_print = True
        time.sleep(5)