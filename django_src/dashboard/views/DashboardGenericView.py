from django.views.generic import TemplateView
from django.template.response import TemplateResponse

from django.http import Http404
from django.http import HttpResponseRedirect
from django.http import UnreadablePostError
from django.db import IntegrityError


from dashboard.services import CSVFileUploadService

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
            else:
                context["result"] = "\n".join(msg_list)        

        return TemplateResponse(request, self.template_name, context)
                    
