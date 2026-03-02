from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Sum, Count
from django.contrib import messages
from datetime import datetime, timedelta
from django.utils import timezone
from .models import *
from .forms import *

from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Q

@login_required
def dashboard(request):
    """Asosiy dashboard - kunlik reyting bilan"""
    
    # Joriy xodim (agar oddiy foydalanuvchi bo'lsa)
    try:
        joriy_xodim = request.user.xodim
        
        # Bugungi statistika
        bugun = timezone.now().date()
        bugungi_bonus = BonusRecord.objects.filter(
            xodim=joriy_xodim, 
            sana__date=bugun
        ).aggregate(Sum('ball_miqdori'))['ball_miqdori__sum'] or 0
        
        bugungi_jarima = JarimaRecord.objects.filter(
            xodim=joriy_xodim, 
            sana__date=bugun
        ).aggregate(Sum('ball_miqdori'))['ball_miqdori__sum'] or 0
        
        joriy_xodim.bugungi_ball = bugungi_bonus
        joriy_xodim.bugungi_jarima = bugungi_jarima
        
    except:
        joriy_xodim = None
    
    # Bugungi sana
    bugun = timezone.now().date()
    
    # Kunlik harakatlar (bugungi bonus va jarimalar)
    kunlik_bonuslar = BonusRecord.objects.filter(
        sana__date=bugun
    ).select_related('xodim', 'sabab').order_by('-sana')
    
    kunlik_jarimalar = JarimaRecord.objects.filter(
        sana__date=bugun
    ).select_related('xodim', 'sabab').order_by('-sana')
    
    # Birlashtirish
    kunlik_harakatlar = []
    
    for bonus in kunlik_bonuslar:
        kunlik_harakatlar.append({
            'tur': 'bonus',
            'xodim': bonus.xodim,
            'ball': bonus.ball_miqdori,
            'pul': bonus.pul_miqdori,
            'sabab': bonus.sabab.nom if bonus.sabab else 'Bonus',
            'sana': bonus.sana,
            'lavozim': 'Xodim'
        })
    
    for jarima in kunlik_jarimalar:
        kunlik_harakatlar.append({
            'tur': 'jarima',
            'xodim': jarima.xodim,
            'ball': jarima.ball_miqdori,
            'pul': jarima.pul_miqdori,
            'sabab': jarima.sabab.nom if jarima.sabab else 'Jarima',
            'sana': jarima.sana,
            'lavozim': 'Xodim'
        })
    
    # Vaqt bo'yicha saralash (eng oxirgisi tepada)
    kunlik_harakatlar.sort(key=lambda x: x['sana'], reverse=True)
    kunlik_harakatlar_soni = len(kunlik_harakatlar)
    
    # Barcha xodimlar (umumiy reyting)
    xodimlar = Xodim.objects.all().order_by('-reyting_ball')
    xodimlar_soni = xodimlar.count()
    
    context = {
        'joriy_xodim': joriy_xodim,
        'bugun': bugun,
        'kunlik_harakatlar': kunlik_harakatlar,
        'kunlik_harakatlar_soni': kunlik_harakatlar_soni,
        'xodimlar': xodimlar,
        'xodimlar_soni': xodimlar_soni,
    }
    return render(request, 'main/dashboard.html', context)

@login_required
def mening_profilim(request):
    """Xodim o'z profilini ko'rishi"""
    try:
        xodim = request.user.xodim
    except:
        messages.error(request, 'Siz xodim sifatida ro\'yxatdan o\'tmagansiz!')
        return redirect('dashboard')
    
    # Xodimning barcha bonus va jarimalari
    bonuslar = BonusRecord.objects.filter(xodim=xodim).order_by('-sana')[:20]
    jarimalar = JarimaRecord.objects.filter(xodim=xodim).order_by('-sana')[:20]
    
    # Statistikalar - xatolarni tuzatish
    umumiy_bonus_ball = xodim.bonus_ball  # .jami qismini olib tashlang
    umumiy_bonus_pul = xodim.bonus_pul    # .jami qismini olib tashlang
    umumiy_jarima_ball = xodim.jarima_ball  # .jami qismini olib tashlang
    umumiy_jarima_pul = xodim.jarima_pul    # .jami qismini olib tashlang
    reyting_ball = xodim.reyting_ball
    reyting_pul = xodim.reyting_pul
    
    # Reytingdagi o'rni
    joylashuv = Xodim.objects.filter(reyting_ball__gt=reyting_ball).count() + 1
    
    context = {
        'xodim': xodim,
        'bonuslar': bonuslar,
        'jarimalar': jarimalar,
        'umumiy_bonus_ball': umumiy_bonus_ball,
        'umumiy_bonus_pul': umumiy_bonus_pul,
        'umumiy_jarima_ball': umumiy_jarima_ball,
        'umumiy_jarima_pul': umumiy_jarima_pul,
        'reyting_ball': reyting_ball,
        'reyting_pul': reyting_pul,
        'joylashuv': joylashuv,
        'jami_xodimlar': Xodim.objects.count(),
    }
    return render(request, 'main/mening_profilim.html', context)



@login_required
def reytinglar(request):
    """Barcha reytinglarni ko'rish"""
    davr = request.GET.get('davr', 'umumiy')
    
    if davr == 'kunlik':
        bugun = timezone.now().date()
        data = []
        for xodim in Xodim.objects.all():
            bonus = BonusRecord.objects.filter(xodim=xodim, sana__date=bugun).aggregate(
                ball=Sum('ball_miqdori'), pul=Sum('pul_miqdori')
            )
            jarima = JarimaRecord.objects.filter(xodim=xodim, sana__date=bugun).aggregate(
                ball=Sum('ball_miqdori'), pul=Sum('pul_miqdori')
            )
            data.append({
                'xodim': xodim,
                'bonus_ball': bonus['ball'] or 0,
                'bonus_pul': bonus['pul'] or 0,
                'jarima_ball': jarima['ball'] or 0,
                'jarima_pul': jarima['pul'] or 0,
            })
        data.sort(key=lambda x: (x['bonus_ball'] - x['jarima_ball']), reverse=True)
        
    elif davr == 'haftalik':
        hafta_boshi = timezone.now().date() - timedelta(days=timezone.now().date().weekday())
        data = []
        for xodim in Xodim.objects.all():
            bonus = BonusRecord.objects.filter(xodim=xodim, sana__date__gte=hafta_boshi).aggregate(
                ball=Sum('ball_miqdori'), pul=Sum('pul_miqdori')
            )
            jarima = JarimaRecord.objects.filter(xodim=xodim, sana__date__gte=hafta_boshi).aggregate(
                ball=Sum('ball_miqdori'), pul=Sum('pul_miqdori')
            )
            data.append({
                'xodim': xodim,
                'bonus_ball': bonus['ball'] or 0,
                'bonus_pul': bonus['pul'] or 0,
                'jarima_ball': jarima['ball'] or 0,
                'jarima_pul': jarima['pul'] or 0,
            })
        data.sort(key=lambda x: (x['bonus_ball'] - x['jarima_ball']), reverse=True)
        
    elif davr == 'oylik':
        oy_boshi = timezone.now().date().replace(day=1)
        data = []
        for xodim in Xodim.objects.all():
            bonus = BonusRecord.objects.filter(xodim=xodim, sana__date__gte=oy_boshi).aggregate(
                ball=Sum('ball_miqdori'), pul=Sum('pul_miqdori')
            )
            jarima = JarimaRecord.objects.filter(xodim=xodim, sana__date__gte=oy_boshi).aggregate(
                ball=Sum('ball_miqdori'), pul=Sum('pul_miqdori')
            )
            data.append({
                'xodim': xodim,
                'bonus_ball': bonus['ball'] or 0,
                'bonus_pul': bonus['pul'] or 0,
                'jarima_ball': jarima['ball'] or 0,
                'jarima_pul': jarima['pul'] or 0,
            })
        data.sort(key=lambda x: (x['bonus_ball'] - x['jarima_ball']), reverse=True)
        
    elif davr == 'yillik':
        yil_boshi = timezone.now().date().replace(month=1, day=1)
        data = []
        for xodim in Xodim.objects.all():
            bonus = BonusRecord.objects.filter(xodim=xodim, sana__date__gte=yil_boshi).aggregate(
                ball=Sum('ball_miqdori'), pul=Sum('pul_miqdori')
            )
            jarima = JarimaRecord.objects.filter(xodim=xodim, sana__date__gte=yil_boshi).aggregate(
                ball=Sum('ball_miqdori'), pul=Sum('pul_miqdori')
            )
            data.append({
                'xodim': xodim,
                'bonus_ball': bonus['ball'] or 0,
                'bonus_pul': bonus['pul'] or 0,
                'jarima_ball': jarima['ball'] or 0,
                'jarima_pul': jarima['pul'] or 0,
            })
        data.sort(key=lambda x: (x['bonus_ball'] - x['jarima_ball']), reverse=True)
        
    else:  # umumiy
        data = Xodim.objects.all().order_by('-reyting_ball')
    
    context = {
        'davr': davr,
        'data': data,
    }
    return render(request, 'main/reytinglar.html', context)

@staff_member_required
def xodim_qoshish(request):
    if request.method == 'POST':
        form = XodimForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Xodim muvaffaqiyatli qo\'shildi!')
            return redirect('xodimlar')
    else:
        form = XodimForm()
    return render(request, 'main/xodim_form.html', {'form': form, 'title': 'Xodim Qo\'shish'})

@login_required
def xodimlar(request):
    xodimlar = Xodim.objects.all().order_by('-reyting_ball')
    
    # Qidiruv
    qidiruv = request.GET.get('qidiruv', '')
    if qidiruv:
        xodimlar = xodimlar.filter(
            Q(ism__icontains=qidiruv) | 
            Q(familya__icontains=qidiruv) |
            Q(telefon__icontains=qidiruv)
        )
    
    # Sahifalash
    from django.core.paginator import Paginator
    paginator = Paginator(xodimlar, 10)
    page = request.GET.get('page', 1)
    xodimlar = paginator.get_page(page)
    
    return render(request, 'main/xodimlar.html', {'xodimlar': xodimlar})

@login_required
def xodim_detail(request, pk):
    """Bitta xodim haqida to'liq ma'lumot"""
    xodim = get_object_or_404(Xodim, pk=pk)
    bonuslar = BonusRecord.objects.filter(xodim=xodim).order_by('-sana')[:30]
    jarimalar = JarimaRecord.objects.filter(xodim=xodim).order_by('-sana')[:30]
    
    context = {
        'xodim': xodim,
        'bonuslar': bonuslar,
        'jarimalar': jarimalar,
    }
    return render(request, 'main/xodim_detail.html', context)

@staff_member_required
def bonus_qoshish(request):
    if request.method == 'POST':
        form = BonusRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.created_by = request.user
            record.save()
            messages.success(request, 'Bonus muvaffaqiyatli qo\'shildi!')
            return redirect('dashboard')
    else:
        form = BonusRecordForm()
    
    sabablar = BonusSabab.objects.filter(active=True)
    return render(request, 'main/bonus_form.html', {
        'form': form,
        'sabablar': sabablar,
        'title': 'Bonus Qo\'shish'
    })

@staff_member_required
def jarima_qoshish(request):
    if request.method == 'POST':
        form = JarimaRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.created_by = request.user
            record.save()
            messages.success(request, 'Jarima muvaffaqiyatli qo\'shildi!')
            return redirect('dashboard')
    else:
        form = JarimaRecordForm()
    
    sabablar = JarimaSabab.objects.filter(active=True)
    return render(request, 'main/jarima_form.html', {
        'form': form,
        'sabablar': sabablar,
        'title': 'Jarima Qo\'shish'
    })

@staff_member_required
def sabablar_boshqaruvi(request):
    bonus_sabablar = BonusSabab.objects.all()
    jarima_sabablar = JarimaSabab.objects.all()
    
    if request.method == 'POST':
        if 'bonus_qoshish' in request.POST:
            nom = request.POST.get('bonus_nom')
            pul = request.POST.get('bonus_pul')
            ball = request.POST.get('bonus_ball')
            BonusSabab.objects.create(nom=nom, pul_miqdori=pul, ball_miqdori=ball)
            messages.success(request, 'Bonus sababi qo\'shildi!')
        
        elif 'jarima_qoshish' in request.POST:
            nom = request.POST.get('jarima_nom')
            pul = request.POST.get('jarima_pul')
            ball = request.POST.get('jarima_ball')
            JarimaSabab.objects.create(nom=nom, pul_miqdori=pul, ball_miqdori=ball)
            messages.success(request, 'Jarima sababi qo\'shildi!')
        
        elif 'ochirish' in request.POST:
            tur = request.POST.get('tur')
            pk = request.POST.get('pk')
            if tur == 'bonus':
                BonusSabab.objects.filter(id=pk).delete()
            else:
                JarimaSabab.objects.filter(id=pk).delete()
            messages.success(request, 'Sabab o\'chirildi!')
        
        return redirect('sabablar_boshqaruvi')
    
    return render(request, 'main/sabablar_boshqaruvi.html', {
        'bonus_sabablar': bonus_sabablar,
        'jarima_sabablar': jarima_sabablar
    })