from django.conf.urls import url
from .views import DashboardMainView

urlpatterns = [
    url('', DashboardMainView.as_view(), name='dashboard-main')
]
