from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('mening-profilim/', views.mening_profilim, name='mening_profilim'),
    path('reytinglar/', views.reytinglar, name='reytinglar'),
    path('xodimlar/', views.xodimlar, name='xodimlar'),
    path('xodim/<int:pk>/', views.xodim_detail, name='xodim_detail'),
    path('xodim-qoshish/', views.xodim_qoshish, name='xodim_qoshish'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('bonus-qoshish/', views.bonus_qoshish, name='bonus_qoshish'),
    path('rasm-ochirish/', views.rasm_ochirish, name='rasm_ochirish'),
    path('jarima-qoshish/', views.jarima_qoshish, name='jarima_qoshish'),
    path('sabablar-boshqaruvi/', views.sabablar_boshqaruvi, name='sabablar_boshqaruvi'),
]