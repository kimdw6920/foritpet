from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
# 아래 줄이 빠져서 NameError가 났던 것입니다!
from .models import Shelter, VolunteerSchedule, VolunteerApplication, UserProfile

# 1. 보호소 상세 페이지 뷰
def shelter_detail(request, shelter_id):
    shelter = get_object_or_404(Shelter, id=shelter_id)
    return render(request, 'shelter/shelter_detail.html', {'shelter': shelter})

# 2. 봉사 신청 로직
def apply_volunteer(request, schedule_id):
    if request.method == 'POST':
        # 여기서도 Shelter와 관련된 모델들을 사용합니다.
        schedule = get_object_or_404(VolunteerSchedule, id=schedule_id)
        
        if schedule.current_participants >= schedule.max_participants:
            return JsonResponse({'message': '이미 정원이 초과되었습니다.'}, status=400)
        
        VolunteerApplication.objects.create(
            user=request.user,
            schedule=schedule
        )
        
        schedule.current_participants += 1
        schedule.save()
        
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.point += 500
        profile.save()
        
        return JsonResponse({'message': '신청이 완료되었습니다! 500P가 적립되었습니다.'})