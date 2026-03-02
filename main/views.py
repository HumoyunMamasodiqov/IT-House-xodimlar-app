from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Sum, Count, Avg
from django.contrib import messages
from datetime import datetime, timedelta
from django.utils import timezone
from .models import *
from .forms import *


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

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Xodim, BonusRecord, JarimaRecord
from .forms import XodimRasmForm


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Xodim, BonusRecord, JarimaRecord
from .forms import XodimRasmForm

@login_required
def mening_profilim(request):
    """Xodim o'z profilini ko'rishi"""
    try:
        xodim = request.user.xodim
    except:
        messages.error(request, 'Siz xodim sifatida ro\'yxatdan o\'tmagansiz!')
        return redirect('dashboard')
    
    # Rasm yuklash
    if request.method == 'POST':
        if 'rasm_yuklash' in request.POST:
            form = XodimRasmForm(request.POST, request.FILES, instance=xodim)
            if form.is_valid():
                form.save()
                messages.success(request, 'Rasm muvaffaqiyatli yuklandi!')
                return redirect('mening_profilim')
        
        elif 'rasm_ochirish' in request.POST:
            if xodim.rasm:
                xodim.rasm.delete()  # Faylni o'chirish
                xodim.rasm = None
                xodim.save()
                messages.success(request, 'Rasm o\'chirildi!')
                return redirect('mening_profilim')
    
    # Xodimning barcha bonus va jarimalari
    bonuslar = BonusRecord.objects.filter(xodim=xodim).select_related('sabab').order_by('-sana')[:20]
    jarimalar = JarimaRecord.objects.filter(xodim=xodim).select_related('sabab').order_by('-sana')[:20]
    
    # Reytingdagi o'rni
    joylashuv = Xodim.objects.filter(reyting_ball__gt=xodim.reyting_ball).count() + 1
    jami_xodimlar = Xodim.objects.count()
    
    context = {
        'xodim': xodim,
        'bonuslar': bonuslar,
        'jarimalar': jarimalar,
        'umumiy_bonus_ball': xodim.bonus_ball,
        'umumiy_bonus_pul': xodim.bonus_pul,
        'umumiy_jarima_ball': xodim.jarima_ball,
        'umumiy_jarima_pul': xodim.jarima_pul,
        'reyting_ball': xodim.reyting_ball,
        'reyting_pul': xodim.reyting_pul,
        'joylashuv': joylashuv,
        'jami_xodimlar': jami_xodimlar,
    }
    return render(request, 'main/mening_profilim.html', context)



@login_required
def rasm_ochirish(request):
    """Profil rasmini o'chirish"""
    try:
        xodim = request.user.xodim
        if xodim.rasm:
            xodim.rasm.delete()
            xodim.save()
            messages.success(request, 'Rasm o\'chirildi!')
    except:
        messages.error(request, 'Xatolik yuz berdi!')
    return redirect('mening_profilim')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Sum, Count, Avg
from django.contrib import messages
from datetime import datetime, timedelta
from django.utils import timezone
from .models import *
from .forms import *
@login_required
def reytinglar(request):
    """Reytinglar sahifasi - kunlik, haftalik, oylik, yillik"""
    
    davr = request.GET.get('davr', 'kunlik')  # Default: kunlik
    
    # Barcha xodimlar
    xodimlar = Xodim.objects.all()
    jami_xodimlar = xodimlar.count()
    
    # Bugungi sana
    bugun = timezone.now().date()
    
    # Hafta boshi (dushanba)
    hafta_boshi = bugun - timedelta(days=bugun.weekday())
    
    # Oy boshi
    oy_boshi = bugun.replace(day=1)
    
    # Yil boshi
    yil_boshi = bugun.replace(month=1, day=1)
    
    # Har bir xodim uchun davrlar bo'yicha ballarni hisoblash
    for xodim in xodimlar:
        # Kunlik
        kunlik_bonus = BonusRecord.objects.filter(
            xodim=xodim, 
            sana__date=bugun
        ).aggregate(Sum('ball_miqdori'))['ball_miqdori__sum'] or 0
        
        kunlik_jarima = JarimaRecord.objects.filter(
            xodim=xodim, 
            sana__date=bugun
        ).aggregate(Sum('ball_miqdori'))['ball_miqdori__sum'] or 0
        
        xodim.kunlik_reyting = kunlik_bonus - kunlik_jarima
        
        # Haftalik
        haftalik_bonus = BonusRecord.objects.filter(
            xodim=xodim, 
            sana__date__gte=hafta_boshi
        ).aggregate(Sum('ball_miqdori'))['ball_miqdori__sum'] or 0
        
        haftalik_jarima = JarimaRecord.objects.filter(
            xodim=xodim, 
            sana__date__gte=hafta_boshi
        ).aggregate(Sum('ball_miqdori'))['ball_miqdori__sum'] or 0
        
        xodim.haftalik_reyting = haftalik_bonus - haftalik_jarima
        
        # Oylik
        oylik_bonus = BonusRecord.objects.filter(
            xodim=xodim, 
            sana__date__gte=oy_boshi
        ).aggregate(Sum('ball_miqdori'))['ball_miqdori__sum'] or 0
        
        oylik_jarima = JarimaRecord.objects.filter(
            xodim=xodim, 
            sana__date__gte=oy_boshi
        ).aggregate(Sum('ball_miqdori'))['ball_miqdori__sum'] or 0
        
        xodim.oylik_reyting = oylik_bonus - oylik_jarima
        
        # Yillik
        yillik_bonus = BonusRecord.objects.filter(
            xodim=xodim, 
            sana__date__gte=yil_boshi
        ).aggregate(Sum('ball_miqdori'))['ball_miqdori__sum'] or 0
        
        yillik_jarima = JarimaRecord.objects.filter(
            xodim=xodim, 
            sana__date__gte=yil_boshi
        ).aggregate(Sum('ball_miqdori'))['ball_miqdori__sum'] or 0
        
        xodim.yillik_reyting = yillik_bonus - yillik_jarima
        
        # Bugungi o'zgarish (kunlik)
        xodim.bugungi_ball = kunlik_bonus
        xodim.bugungi_jarima = kunlik_jarima
    
    # Davr bo'yicha saralash
    if davr == 'kunlik':
        xodimlar = sorted(xodimlar, key=lambda x: x.kunlik_reyting, reverse=True)
    elif davr == 'haftalik':
        xodimlar = sorted(xodimlar, key=lambda x: x.haftalik_reyting, reverse=True)
    elif davr == 'oylik':
        xodimlar = sorted(xodimlar, key=lambda x: x.oylik_reyting, reverse=True)
    elif davr == 'yillik':
        xodimlar = sorted(xodimlar, key=lambda x: x.yillik_reyting, reverse=True)
    else:  # umumiy
        xodimlar = xodimlar.order_by('-reyting_ball')
    
    # Statistika
    eng_yuqori_xodim = Xodim.objects.order_by('-reyting_ball').first()
    eng_yuqori_ball = eng_yuqori_xodim.reyting_ball if eng_yuqori_xodim else 0
    
    # O'rtacha ball (umumiy)
    ortacha_ball = Xodim.objects.aggregate(Avg('reyting_ball'))['reyting_ball__avg'] or 0
    ortacha_ball = round(ortacha_ball)
    
    # Faol xodimlar (oxirgi 7 kunda harakat qilganlar)
    bir_hafta_oldin = timezone.now() - timedelta(days=7)
    faol_xodimlar = Xodim.objects.filter(
        Q(bonus_recordlari__sana__gte=bir_hafta_oldin) | 
        Q(jarima_recordlari__sana__gte=bir_hafta_oldin)
    ).distinct().count()
    
    # Podium uchun top 3 (tanlangan davr bo'yicha)
    top_3 = list(xodimlar)[:3]
    podium = {}
    
    for i, xodim in enumerate(top_3, 1):
        # Davrga mos ballni ko'rsatish
        if davr == 'kunlik':
            ball = xodim.kunlik_reyting
        elif davr == 'haftalik':
            ball = xodim.haftalik_reyting
        elif davr == 'oylik':
            ball = xodim.oylik_reyting
        elif davr == 'yillik':
            ball = xodim.yillik_reyting
        else:
            ball = xodim.reyting_ball
        
        # Ismni qisqartirish
        if len(xodim.ism) > 0 and len(xodim.familya) > 0:
            name_short = f"{xodim.ism} {xodim.familya[0]}."
        else:
            name_short = xodim.ism
        
        # RASM QO'SHILDI - MUHIM!
        rasm_url = None
        try:
            if xodim.rasm and hasattr(xodim.rasm, 'url') and xodim.rasm.url:
                rasm_url = xodim.rasm.url
                print(f"Rasm topildi: {xodim.ism} - {rasm_url}")  # Terminalda tekshirish
        except:
            rasm_url = None
            print(f"Rasm xatosi: {xodim.ism}")
        
        podium[i] = {
            'name': name_short,
            'full_name': f"{xodim.ism} {xodim.familya}",
            'initials': f"{xodim.ism[0]}{xodim.familya[0]}",
            'score': ball,
            'rasm': rasm_url,  # RASM URL QO'SHILDI
        }
    
    # Terminalga podium ma'lumotlarini chiqarish (tekshirish uchun)
    print("="*50)
    print(f"Davr: {davr}")
    print("Podium ma'lumotlari:")
    for key, value in podium.items():
        print(f"  {key}. {value['name']} - ball: {value['score']} - rasm: {value['rasm']}")
    print("="*50)
    
    context = {
        'xodimlar': xodimlar,
        'jami_xodimlar': jami_xodimlar,
        'eng_yuqori_ball': eng_yuqori_ball,
        'eng_yuqori_xodim': f"{eng_yuqori_xodim.ism[0]}. {eng_yuqori_xodim.familya[0]}." if eng_yuqori_xodim else '',
        'ortacha_ball': ortacha_ball,
        'ortacha_osish': 12,  # Hisoblash mumkin
        'faol_xodimlar': faol_xodimlar,
        'podium': podium,
        'davr': davr,
        'bugun': bugun,
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