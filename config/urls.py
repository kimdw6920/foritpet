from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from main import views as main_views

urlpatterns = [
    path('', main_views.home, name='home'),
    path('admin/', admin.site.urls),
    path('shelter/', include('shelter.urls')),
    path('community/', include('board.urls')),
    path('mypage/', main_views.mypage, name='mypage'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)