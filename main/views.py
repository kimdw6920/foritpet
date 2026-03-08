from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.mail import send_mail
from django.db.models import Sum
from django.shortcuts import render, redirect
from shelter.models import Shelter, Donation


def home(request):
    """메인 홈 - 도움이 필요한 보호소 소개"""
    shelters = Shelter.objects.all().order_by('region', 'name')[:6]
    # 전체 후원 내역을 사료 포장 무게(kg) 기준으로 합산
    donations = Donation.objects.select_related('product')
    total_kg = 0.0
    for d in donations:
        weight = getattr(d.product, 'weight_kg', 1.0) or 1.0
        total_kg += d.amount * weight
    return render(request, 'home.html', {'shelters': shelters, 'total_kg': total_kg})


@login_required
def mypage(request):
    """내 정보 - 후원 기록, 커뮤니티 활동 등"""
    donations = Donation.objects.filter(user=request.user).select_related(
        'shelter', 'product'
    ).order_by('-created_at')[:30]
    # 사용자가 후원한 전체 사료 무게(kg) 합산
    total_donations_all = Donation.objects.filter(user=request.user).select_related('product')
    total_kg = 0.0
    for d in total_donations_all:
        weight = getattr(d.product, 'weight_kg', 1.0) or 1.0
        total_kg += d.amount * weight
    return render(request, 'mypage.html', {
        'donations': donations,
        'total_kg': total_kg,
    })


User = get_user_model()


class SignUpForm(UserCreationForm):
    email = forms.EmailField(label='이메일', required=True)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email')


def signup(request):
    """회원 가입 (아이디 + 이메일 + 비밀번호)"""
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '회원가입이 완료되었습니다.')
            return redirect('home')
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


def find_username(request):
    """
    아이디 찾기: 이메일을 입력하면 해당 이메일로 연결된 아이디를 메일로 안내.
    보안상 존재 여부와 상관없이 동일한 안내 메시지를 보여준다.
    """
    if request.method == 'POST':
        email = (request.POST.get('email') or '').strip()
        if email:
            users = User.objects.filter(email=email)
            if users.exists():
                usernames = ', '.join(u.username for u in users)
                subject = '포잇펫 아이디 안내'
                message = f'입력하신 이메일({email})로 등록된 아이디: {usernames}'
                from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@foritpet.local')
                try:
                    send_mail(subject, message, from_email, [email], fail_silently=True)
                except Exception:
                    pass
        messages.info(request, '입력하신 이메일로 아이디 안내를 발송했습니다. (등록된 이메일이 아닐 경우 메일이 가지 않을 수 있습니다.)')
        return redirect('login')
    return render(request, 'find_username.html')