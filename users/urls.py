from django.urls import path
from .views import student_info

urlpatterns = [
    path("carrier/student/detail/", student_info.as_view()) #sample_api
]
