from django.db import models
from django.contrib.auth.models import User

# 1. 사료 상품 (수익 모델)
class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name="사료명")
    price = models.IntegerField(verbose_name="가격")
    image = models.ImageField(upload_to='products/', verbose_name="사료이미지")
    description = models.TextField(verbose_name="사료설명")

    def __str__(self):
        return self.name

# 2. 보호소 정보 (전국 각지 리스트용 - 공공데이터 없어 직접 등록)
class Shelter(models.Model):
    REGION_CHOICES = [
        ('서울', '서울'), ('부산', '부산'), ('대구', '대구'), ('인천', '인천'), ('광주', '광주'),
        ('대전', '대전'), ('울산', '울산'), ('세종', '세종'), ('경기', '경기'), ('강원', '강원'),
        ('충북', '충북'), ('충남', '충남'), ('전북', '전북'), ('전남', '전남'), ('경북', '경북'),
        ('경남', '경남'), ('제주', '제주'),
    ]
    name = models.CharField(max_length=100, verbose_name="보호소명")
    region = models.CharField(max_length=20, choices=REGION_CHOICES, default='서울', verbose_name="지역")
    address = models.CharField(max_length=200, verbose_name="주소")
    phone = models.CharField(max_length=20, blank=True, verbose_name="연락처")
    description = models.TextField(verbose_name="보호소소개")
    image = models.ImageField(upload_to='shelters/', verbose_name="보호소이미지", blank=True, null=True)
    # 보호소에서 사용하는 추천 사료 (플랫폼에서 구매 가능)
    target_product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="필요사료")

    def __str__(self):
        return self.name

# 3. 후원 내역 (결제 연동 시 imp_uid로 중복 방지 및 감사)
class Donation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="후원자")
    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE, verbose_name="보호소")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="후원물품")
    amount = models.IntegerField(default=1, verbose_name="수량")
    imp_uid = models.CharField(max_length=64, blank=True, verbose_name="포트원 결제고유번호")
    merchant_uid = models.CharField(max_length=128, blank=True, verbose_name="주문번호")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="후원시간")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.shelter.name} ({self.product.name})"