from data.models import RawSteps
import pprint

class TaskExecutionService:
    def execute(self):
        user_list = RawSteps.objects.distinct('user_id', "local_date")
        
        user_id_list = []
        
        pprint.pprint(user_list)
        for user_obj in user_list:
            pprint.pprint(user_obj.__dict__)
            user_id_list.append("user_id: {}, local_date: {}".format(user_obj.user_id, user_obj.local_date))
        
        return "\n".join(user_id_list)
        # return "printed"