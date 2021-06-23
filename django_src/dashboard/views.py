from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.
class DashboardMainView(TemplateView):
    template_name = 'dashboard/DashboardMainView.html'