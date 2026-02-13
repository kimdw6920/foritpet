from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from shelter.models import Shelter, Donation


def home(request):
    """메인 홈 - 도움이 필요한 보호소 소개"""
    shelters = Shelter.objects.all().order_by('region', 'name')[:6]
    return render(request, 'home.html', {'shelters': shelters})


@login_required(login_url='/admin/login/')
def mypage(request):
    """내 정보 - 후원 기록, 커뮤니티 활동 등"""
    donations = Donation.objects.filter(user=request.user).select_related(
        'shelter', 'product'
    ).order_by('-created_at')[:30]
    total_donations_all = Donation.objects.filter(user=request.user)
    total_items = sum(d.amount for d in total_donations_all)
    return render(request, 'mypage.html', {
        'donations': donations,
        'total_items': total_items,
    })