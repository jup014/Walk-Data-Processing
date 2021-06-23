from django.conf.urls import url
from .views import DashboardMainView
from .views import DashboardGenericView

urlpatterns = [
    url('generic/', DashboardGenericView.as_view(), name='dashboard-generic'),
    url('', DashboardMainView.as_view(), name='dashboard-main')    
]
