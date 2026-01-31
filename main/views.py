from django.shortcuts import render
from shelter.models import Shelter

def home(request):
    # 모든 보호소 정보를 가져와서 홈 화면에 전달
    shelters = Shelter.objects.all()
    return render(request, 'main/home.html', {'shelters': shelters})