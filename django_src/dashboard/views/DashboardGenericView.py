from django.views.generic import TemplateView
from django.template.response import TemplateResponse

from django.http import Http404
from django.http import HttpResponseRedirect
from django.http import UnreadablePostError
from django.db import IntegrityError

import random
import csv
import os

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
                
                    filename = "temp_file_{}.csv".format(random.randint(1000000, 9999999))
                    
                    with open(filename, "wb") as f:
                        if csv_file.multiple_chunks():
                            for chunk in csv_file.chunks():
                                f.write(chunk)
                        else:
                            f.write(csv_file.read())
                    
                    with open(filename, "r") as f:
                        datareader = csv.reader(f)
                        
                        line_index = 0
                        
                        for row in datareader:
                            if line_index == 0:
                                header = row
                                print(header)
                            else:
                                # TODO: insert data
                                pass
                                
                            line_index += 1
                    
                    D("{} lines are read.".format(line_index))
                    D("header: {}".format(header))
                    
                    os.remove(filename)

        context["result"] = "\n".join(msg_list)
        return TemplateResponse(request, self.template_name, context)