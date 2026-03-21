from django.db import models
from django.contrib.auth.models import User

# 1. 사료 상품 (수익 모델)
class Product(models.Model):
    name = models.CharField(max_length=100, verbose_name="사료명")
    price = models.IntegerField(verbose_name="가격")
    image = models.ImageField(upload_to='products/', verbose_name="사료이미지")
    description = models.TextField(verbose_name="사료설명")
     # 포장 무게 (kg 단위, 전체 후원 kg 계산에 사용)
    weight_kg = models.FloatField(default=1.0, verbose_name="포장 무게(kg)")

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
    # 배송(창고 → 보호소) 조회용
    tracking_number = models.CharField(max_length=64, blank=True, verbose_name="송장번호")
    tracking_carrier = models.CharField(max_length=64, blank=True, verbose_name="택배사")
    shipped_at = models.DateTimeField(null=True, blank=True, verbose_name="발송일시")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.shelter.name} ({self.product.name})"

    def get_tracking_url(self):
        """택배사별 배송 조회 URL. 없으면 None."""
        if not self.tracking_number or not self.tracking_carrier:
            return None
        num = self.tracking_number.strip()
        carrier = (self.tracking_carrier or "").strip()
        # 택배사 이름으로 URL 패턴 매칭
        if "cj" in carrier.lower() or "대한통운" in carrier or "CJ" in carrier:
            return f"https://www.cjlogistics.com/ko/tool/parcel/tracking?wlbn={num}"
        if "한진" in carrier or "hanjin" in carrier.lower():
            return f"https://www.hanjin.co.kr/kor/CMS/DeliveryMgr.do?mCode=MN038&schLang=KR&wblnum={num}"
        if "롯데" in carrier or "lotte" in carrier.lower():
            return f"https://www.lotteglogis.com/home/reservation/tracking/index?InvNo={num}"
        if "우체국" in carrier or "epost" in carrier.lower() or "우편" in carrier:
            return f"https://service.epost.go.kr/trace.RetrieveEmsTrace.postal?sid1={num}"
        if "로젠" in carrier or "logen" in carrier.lower():
            return f"https://www.logen.co.kr/delivery/delivery_01.asp?param_inv_no={num}"
        if "cu" in carrier.lower() or "편의점" in carrier:
            return f"https://www.cupost.co.kr/postbox/cu/tracking.do?inv_no={num}"
        # 기본: 네이버 배송조회 (여러 택배사 지원)
        return f"https://search.shopping.naver.com/search/all?query={num}"


class ChatMessage(models.Model):
    """보호소별 실시간 채팅 메시지"""
    shelter = models.ForeignKey(Shelter, on_delete=models.CASCADE, related_name='chat_messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.shelter.name} - {self.user.username}: {self.content[:20]}"