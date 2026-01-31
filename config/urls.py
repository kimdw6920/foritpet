from django.contrib import admin
from django.urls import path, include
from main import views as main_views # 추가

urlpatterns = [
    path('', main_views.home, name='home'), # 추가: 루트 주소
    path('admin/', admin.site.urls),
    path('shelter/', include('shelter.urls')), # shelter 앱의 URL 포함
]