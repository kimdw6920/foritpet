from django.core.management.base import BaseCommand
from shelter.models import Product, Shelter


class Command(BaseCommand):
    help = "Demo용 사료 상품과 보호소 데이터를 생성합니다."

    def handle(self, *args, **options):
        products_data = [
            {"name": "포잇 어덜트 사료 10kg", "price": 45000, "description": "성견용 균형 잡힌 영양 사료.", "weight_kg": 10.0},
            {"name": "포잇 퍼피 사료 5kg", "price": 32000, "description": "성장기 강아지를 위한 고단백 사료.", "weight_kg": 5.0},
            {"name": "포잇 시니어 사료 7kg", "price": 38000, "description": "노령견 관절 건강을 위한 사료.", "weight_kg": 7.0},
        ]

        products = []
        for data in products_data:
            product, _ = Product.objects.get_or_create(
                name=data["name"],
                defaults={
                    "price": data["price"],
                    "description": data["description"],
                    "image": "",
                    "weight_kg": data["weight_kg"],
                },
            )
            products.append(product)

        shelters_data = [
            {
                "name": "서울 포잇 보호소",
                "region": "서울",
                "address": "서울시 마포구 어딘가 123",
                "phone": "02-123-4567",
                "description": "도심 속에서 구조된 아이들이 지내는 작은 보호소입니다.",
            },
            {
                "name": "경기 포잇 보호소",
                "region": "경기",
                "address": "경기도 성남시 포잇로 45",
                "phone": "031-987-6543",
                "description": "경기 남부 지역 유기견을 주로 보호하고 있습니다.",
            },
            {
                "name": "부산 포잇 보호소",
                "region": "부산",
                "address": "부산시 해운대구 바닷가길 7",
                "phone": "051-555-7777",
                "description": "바다 근처에 위치한 넓은 운동장이 자랑인 보호소입니다.",
            },
        ]

        for idx, data in enumerate(shelters_data):
            shelter, created = Shelter.objects.get_or_create(
                name=data["name"],
                defaults={
                    "region": data["region"],
                    "address": data["address"],
                    "phone": data["phone"],
                    "description": data["description"],
                    "image": "",
                    "target_product": products[idx % len(products)] if products else None,
                },
            )

        self.stdout.write(self.style.SUCCESS("Demo용 사료/보호소 데이터 생성이 완료되었습니다."))

