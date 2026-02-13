import requests
from django.conf import settings
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
    """사료 후원 페이지 - 플랫폼에서 사료 구매 (카카오페이 연동)"""
    shelter = get_object_or_404(Shelter, pk=pk)
    products = list(Product.objects.all())
    if shelter.target_product and shelter.target_product in products:
        products.remove(shelter.target_product)
        products.insert(0, shelter.target_product)
    return render(request, 'shelter/shelter_donate.html', {
        'shelter': shelter,
        'products': products,
        'PORTONE_IMP_CODE': getattr(settings, 'PORTONE_IMP_CODE', 'imp88875057'),
    })


def shelter_donate_do(request, pk):
    """사료 후원 처리 (로그인 필요, POST만 허용)"""
    if request.method != 'POST':
        return redirect('shelter_donate', pk=pk)
    if not request.user.is_authenticated:
        messages.warning(request, '로그인 후 후원할 수 있습니다.')
        from django.urls import reverse
        return redirect(reverse('login') + '?next=' + reverse('shelter_donate', kwargs={'pk': pk}))
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


def _get_portone_access_token():
    """포트원 REST API 액세스 토큰 발급 (서버 결제 검증용)"""
    key = getattr(settings, 'PORTONE_REST_API_KEY', '') or ''
    secret = getattr(settings, 'PORTONE_REST_API_SECRET', '') or ''
    if not key or not secret:
        return None
    r = requests.post(
        'https://api.iamport.kr/users/getToken',
        json={'imp_key': key, 'imp_secret': secret},
        timeout=10,
    )
    if r.status_code != 200:
        return None
    data = r.json()
    if data.get('code') != 0:
        return None
    return data.get('response', {}).get('access_token')


def _verify_portone_payment(imp_uid):
    """imp_uid로 결제 단건 조회 후 paid 여부 및 금액 반환. (성공 시 (True, amount, merchant_uid), 실패 시 (False, 0, None))"""
    token = _get_portone_access_token()
    if not token:
        return False, 0, None
    r = requests.get(
        f'https://api.iamport.kr/payments/{imp_uid}',
        headers={'Authorization': token},
        timeout=10,
    )
    if r.status_code != 200:
        return False, 0, None
    data = r.json()
    if data.get('code') != 0:
        return False, 0, None
    res = data.get('response', {})
    if res.get('status') != 'paid':
        return False, 0, None
    return True, res.get('amount', 0), res.get('merchant_uid')


@login_required
def donate_process(request, pk):
    """결제 완료 콜백: imp_uid 검증 후 후원 내역 저장 (보안: 서버에서 반드시 검증)"""
    shelter = get_object_or_404(Shelter, pk=pk)
    imp_uid = (request.GET.get('imp_uid') or '').strip()
    product_id = request.GET.get('product_id')
    amount_str = request.GET.get('amount', '1')
    if not imp_uid or not product_id:
        messages.error(request, '결제 정보가 올바르지 않습니다.')
        return redirect('shelter_donate', pk=pk)
    try:
        amount = max(1, min(100, int(amount_str)))
    except (TypeError, ValueError):
        amount = 1
    product = get_object_or_404(Product, pk=product_id)
    expected_amount = product.price * amount
    if expected_amount <= 0:
        messages.error(request, '결제 금액이 올바르지 않습니다.')
        return redirect('shelter_donate', pk=pk)
    if Donation.objects.filter(imp_uid=imp_uid).exists():
        messages.info(request, '이미 처리된 결제입니다.')
        return redirect('shelter_donations', pk=pk)
    ok, paid_amount, merchant_uid = _verify_portone_payment(imp_uid)
    if not ok:
        messages.error(request, '결제 검증에 실패했습니다. 결제가 완료되었다면 고객센터로 문의해 주세요.')
        return redirect('shelter_donate', pk=pk)
    if paid_amount != expected_amount:
        messages.error(request, f'결제 금액이 일치하지 않습니다. (결제: {paid_amount}원, 예상: {expected_amount}원)')
        return redirect('shelter_donate', pk=pk)
    Donation.objects.create(
        user=request.user,
        shelter=shelter,
        product=product,
        amount=amount,
        imp_uid=imp_uid,
        merchant_uid=merchant_uid or '',
    )
    messages.success(request, f'{product.name} {amount}개가 {shelter.name}에 후원 등록되었습니다.')
    return redirect('shelter_donations', pk=pk)


def shelter_donations(request, pk):
    """보호소 후원 내역 - 로그인 시 해당 사용자만의 후원 목록, 미로그인 시 로그인 유도"""
    shelter = get_object_or_404(Shelter, pk=pk)
    if not request.user.is_authenticated:
        return render(request, 'shelter/shelter_donations_login_required.html', {
            'shelter': shelter,
        })
    donations = (
        Donation.objects.filter(shelter=shelter, user=request.user)
        .select_related('product')
        .order_by('-created_at')[:50]
    )
    return render(request, 'shelter/shelter_donations.html', {
        'shelter': shelter,
        'donations': donations,
    })