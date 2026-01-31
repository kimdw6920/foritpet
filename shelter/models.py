from django.db import models
from django.conf import settings

# 1. 보호소 기본 정보
class Shelter(models.Model):
    name = models.CharField(max_length=100, verbose_name="보호소명")
    address = models.CharField(max_length=255, verbose_name="주소")
    phone = models.CharField(max_length=20, verbose_name="연락처")
    description = models.TextField(verbose_name="보호소 소개")
    image = models.ImageField(upload_to='shelters/', null=True, blank=True)
    # 친구분 스마트스토어 연동용 (사료 후원 버튼 클릭 시 이동할 URL)
    feed_support_url = models.URLField(verbose_name="사료후원 링크", blank=True)

    def __str__(self):
        return self.name

# 2. 봉사활동 일정 관리
class VolunteerSchedule(models.Model):
    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE, related_name='schedules')
    date = models.DateField(verbose_name="봉사 날짜")
    max_participants = models.IntegerField(default=5, verbose_name="모집 인원")
    current_participants = models.IntegerField(default=0, verbose_name="현재 신청 인원")

# 3. 봉사 신청 내역
class VolunteerApplication(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    schedule = models.ForeignKey(VolunteerSchedule, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='대기', choices=[('대기', '대기'), ('승인', '승인'), ('취소', '취소')])
    applied_at = models.DateTimeField(auto_now_add=True)

class UserProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    point = models.IntegerField(default=0, verbose_name="보유 포인트")

    def __str__(self):
        return f"{self.user.username}의 프로필"