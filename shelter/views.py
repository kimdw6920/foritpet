from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Shelter, Product, Donation


def shelter_list(request):
    """전국 보호소 리스트 (지역별 정렬)"""
    shelters = Shelter.objects.all().order_by('region', 'name')
    return render(request, 'shelter_list.html', {'shelters': shelters})


def shelter_detail_info(request, pk):
    """보호소 기본정보"""
    shelter = get_object_or_404(Shelter, pk=pk)
    return render(request, 'shelter/shelter_info.html', {'shelter': shelter})


def shelter_donate(request, pk):
    """사료 후원 페이지 - 플랫폼에서 사료 구매"""
    shelter = get_object_or_404(Shelter, pk=pk)
    products = list(Product.objects.all())
    if shelter.target_product and shelter.target_product in products:
        products.remove(shelter.target_product)
        products.insert(0, shelter.target_product)
    return render(request, 'shelter/shelter_donate.html', {
        'shelter': shelter,
        'products': products,
    })


def shelter_donate_do(request, pk):
    """사료 후원 처리 (로그인 필요)"""
    if not request.user.is_authenticated:
        messages.warning(request, '로그인 후 후원할 수 있습니다.')
        return redirect('shelter_donate', pk=pk)
    shelter = get_object_or_404(Shelter, pk=pk)
    product_id = request.POST.get('product_id')
    amount = request.POST.get('amount', '1')
    try:
        amount = max(1, int(amount))
    except ValueError:
        amount = 1
    product = get_object_or_404(Product, pk=product_id)
    Donation.objects.create(user=request.user, shelter=shelter, product=product, amount=amount)
    messages.success(request, f'{product.name} {amount}개가 {shelter.name}에 후원 등록되었습니다.')
    return redirect('shelter_donations', pk=pk)


def shelter_donations(request, pk):
    """보호소 후원 내역 (해당 보호소로의 후원 목록)"""
    shelter = get_object_or_404(Shelter, pk=pk)
    donations = Donation.objects.filter(shelter=shelter).select_related('user', 'product').order_by('-created_at')[:50]
    return render(request, 'shelter/shelter_donations.html', {
        'shelter': shelter,
        'donations': donations,
    })