from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.generics import GenericAPIView
# Create your views here.

class student_info(GenericAPIView):

    def get(self, request):
        if not request.user.is_authenticated:
            return HttpResponse("Login first")
        
        user = request.user
        profile = user.user_login_profile
        carrier = profile.carrier
        student = carrier.student

        return HttpResponse(str(student))