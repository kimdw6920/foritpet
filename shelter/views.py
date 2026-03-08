import json
import requests
from django.conf import settings
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Shelter, Product, Donation, ChatMessage


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
    """포트원 REST API 액세스 토큰 발급 (서버 결제 검증용). 현재는 결제 검증을 사용하지 않으므로 호출되지 않습니다."""
    key = getattr(settings, 'PORTONE_REST_API_KEY', '') or ''
    secret = getattr(settings, 'PORTONE_REST_API_SECRET', '') or ''
    if not key or not secret:
        return None
    try:
        r = requests.post(
            'https://api.iamport.kr/users/getToken',
            json={'imp_key': key, 'imp_secret': secret},
            timeout=10,
        )
        data = r.json()
        if r.status_code != 200 or data.get('code') != 0:
            return None
        return data.get('response', {}).get('access_token')
    except Exception:
        return None


def _verify_portone_payment(imp_uid):
    """imp_uid로 결제 단건 조회 후 paid 여부 및 금액 반환. (성공 시 (True, amount, merchant_uid), 실패 시 (False, 0, None))"""
    token = _get_portone_access_token()
    if not token:
        return False, 0, None
    try:
        r = requests.get(
            f'https://api.iamport.kr/payments/{imp_uid}',
            headers={'Authorization': token},
            timeout=10,
        )
        data = r.json()
        if r.status_code != 200 or data.get('code') != 0:
            return False, 0, None
        res = data.get('response', {})
        if res.get('status') != 'paid':
            return False, 0, None
        return True, res.get('amount', 0), res.get('merchant_uid')
    except Exception:
        return False, 0, None


@login_required
def donate_process(request, pk):
    """결제 완료 콜백: (임시) 결제 검증 없이 후원 내역만 저장"""
    shelter = get_object_or_404(Shelter, pk=pk)
    imp_uid = (request.GET.get('imp_uid') or '').strip()
    items_param = (request.GET.get('items') or '').strip()
    created_any = False
    if items_param:
        # 새 방식: items=productIdXqty,productIdXqty,...
        parts = [p for p in items_param.split(',') if p]
        if not parts:
            messages.error(request, '후원 정보가 올바르지 않습니다.')
            return redirect('shelter_donate', pk=pk)
        # imp_uid가 넘어온 경우 중복 전체 방지
        if imp_uid and Donation.objects.filter(imp_uid=imp_uid).exists():
            messages.info(request, '이미 처리된 후원입니다.')
            return redirect('shelter_donations', pk=pk)
        for part in parts:
            try:
                pid_str, qty_str = part.split('x', 1)
                pid = int(pid_str)
                qty = max(1, min(100, int(qty_str)))
            except (ValueError, TypeError):
                continue
            product = get_object_or_404(Product, pk=pid)
            Donation.objects.create(
                user=request.user,
                shelter=shelter,
                product=product,
                amount=qty,
                imp_uid=imp_uid,
                merchant_uid='',
            )
            created_any = True
        if not created_any:
            messages.error(request, '후원 정보가 올바르지 않습니다.')
            return redirect('shelter_donate', pk=pk)
        messages.success(request, '선택하신 사료 후원이 등록되었습니다.')
        return redirect('shelter_donations', pk=pk)

    # 기존 단일 상품 방식 (fallback)
    product_id = request.GET.get('product_id')
    amount_str = request.GET.get('amount', '1')
    if not product_id:
        messages.error(request, '후원 정보가 올바르지 않습니다.')
        return redirect('shelter_donate', pk=pk)
    try:
        amount = max(1, min(100, int(amount_str)))
    except (TypeError, ValueError):
        amount = 1
    product = get_object_or_404(Product, pk=product_id)
    # imp_uid가 넘어온 경우 중복 저장 방지
    if imp_uid and Donation.objects.filter(imp_uid=imp_uid).exists():
        messages.info(request, '이미 처리된 후원입니다.')
        return redirect('shelter_donations', pk=pk)
    Donation.objects.create(
        user=request.user,
        shelter=shelter,
        product=product,
        amount=amount,
        imp_uid=imp_uid,
        merchant_uid='',
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


def shelter_chat(request, pk):
    """보호소 실시간 채팅 페이지"""
    shelter = get_object_or_404(Shelter, pk=pk)
    messages_qs = ChatMessage.objects.filter(shelter=shelter).select_related('user').order_by('-created_at')[:50]
    messages_qs = reversed(list(messages_qs))
    return render(request, 'shelter/shelter_chat.html', {
        'shelter': shelter,
        'chat_messages': messages_qs,
    })


def shelter_chat_messages(request, pk):
    """최근 채팅 메시지를 JSON으로 반환 (간단 폴링용)"""
    shelter = get_object_or_404(Shelter, pk=pk)
    messages_qs = ChatMessage.objects.filter(shelter=shelter).select_related('user').order_by('-created_at')[:50]
    data = [
        {
            'user': m.user.username,
            'content': m.content,
            'created_at': m.created_at.strftime('%H:%M'),
        }
        for m in reversed(list(messages_qs))
    ]
    return JsonResponse({'messages': data})


@login_required
def shelter_chat_send(request, pk):
    """채팅 메시지 전송 (AJAX 또는 일반 POST)"""
    if request.method != 'POST':
        return HttpResponseBadRequest('Invalid method')
    shelter = get_object_or_404(Shelter, pk=pk)
    content = (request.POST.get('content') or '').strip()
    if not content:
        return HttpResponseBadRequest('Empty message')
    ChatMessage.objects.create(shelter=shelter, user=request.user, content=content)
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'ok': True})
    return redirect('shelter_chat', pk=pk)