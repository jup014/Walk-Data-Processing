from task.models import TaskLog

def minute_padding(args):
    TaskLog.log("minute_padding: {}".format(args))