from django.core.management.base import BaseCommand
from shelter.models import Shelter, Product


class Command(BaseCommand):
    help = "테스트용 보호소/사료 데이터를 정리합니다. (test, test2 보호소와 fpdla 사료 삭제)"

    def handle(self, *args, **options):
        shelter_names = ["test", "test2"]
        # 이름에 'fpdla'가 포함된 사료를 모두 삭제
        product_qs = Product.objects.filter(name__icontains="fpdla")

        deleted_shelters, _ = Shelter.objects.filter(name__in=shelter_names).delete()
        deleted_products, _ = product_qs.delete()

        self.stdout.write(self.style.SUCCESS(
            f"삭제된 보호소 레코드 수: {deleted_shelters}, 삭제된 사료 레코드 수: {deleted_products}"
        ))

