from django.shortcuts import redirect, render
from authentication.models import Register
from profiles.forms import EditProfileForm

# Create your views here.


def profile (request):
   
    return render(request, 'profile/Profile.html')
   


def EditProfile(request):
   
    return render(request, 'profile/editProfile.html')
    