from django.conf.urls import url
from .views import FrontPageMainView

urlpatterns = [
    url('', FrontPageMainView.as_view(), name='frontpage-main')
]
