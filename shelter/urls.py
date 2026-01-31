from django.urls import path
from . import views

urlpatterns = [
    # 1. 보호소 상세 페이지
    # 접속 주소 예시: http://127.0.0.1:8000/shelter/1/
    path('<int:shelter_id>/', views.shelter_detail, name='shelter_detail'),
    
    # 2. 봉사 신청 처리 로직
    # 접속 주소 예시: http://127.0.0.1:8000/shelter/apply/1/
    # (HTML 폼에서 버튼을 누를 때 호출되는 주소입니다)
    path('apply/<int:schedule_id>/', views.apply_volunteer, name='apply_volunteer'),
]