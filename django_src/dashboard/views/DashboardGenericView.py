from django.views.generic import TemplateView
from django.template.response import TemplateResponse

from django.http import Http404
from django.http import HttpResponseRedirect
from django.http import UnreadablePostError
from django.db import IntegrityError


from dashboard.services import CSVFileUploadService
from dashboard.services import TaskExecutionService, TaskExecutionService2

class DashboardGenericView(TemplateView):
    template_name = 'dashboard/DashboardGenericView.html'
    def post(self, request, *args, **kwargs):
        msg_list = []
        
        def D(msg):
            msg_list.append(msg)
            
        context = self.get_context_data(**kwargs)
        
        context['result'] = None

        import pprint
                
        
        if request.user and request.user.is_superuser:
            command = request.POST['command']

            if command == 'csv_file_upload':
                if request.FILES['csv_file_upload']:
                    csv_file = request.FILES.get('csv_file_upload')

                    service = CSVFileUploadService()
                    
                    context["result"] = service.load_csv(csv_file)
                else:
                    raise RuntimeError("File is not uploaded")
            elif command == 'execute_task':
                service = TaskExecutionService()
                
                context["result"] = service.execute()
            elif command == 'reset':
                service = TaskExecutionService()
                
                context["result"] = service.reset()
            elif command == 'load_data':
                service = TaskExecutionService()
                
                context["result"] = service.load_data()
            elif command == 'aggregate':
                service = TaskExecutionService()
                
                context["result"] = service.aggr()
            elif command == 'prepare2':
                service = TaskExecutionService2()
                context["result"] = service.prepare()
            elif command == "analysis_2ndPhase":
                service = TaskExecutionService2()
                context["result"] = service.analysis_2ndPhase()
            elif command == "view_progress":
                service = TaskExecutionService2()
                context["result"] = service.view_progress()
            else:
                context["result"] = "\n".join(msg_list)        

        return TemplateResponse(request, self.template_name, context)
                    
