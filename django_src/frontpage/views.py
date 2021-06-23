from django.shortcuts import render
from django.views.generic import TemplateView


# Create your views here.
class FrontPageMainView(TemplateView):
    template_name = 'frontpage/FrontPageMainView.html'