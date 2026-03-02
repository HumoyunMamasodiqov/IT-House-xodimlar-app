from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from datetime import datetime, timedelta
from django.utils import timezone

class BonusSabab(models.Model):
    nom = models.CharField(max_length=200)
    pul_miqdori = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ball_miqdori = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nom} | {self.pul_miqdori} so'm | {self.ball_miqdori} ball"
    
    class Meta:
        verbose_name = "Bonus sababi"
        verbose_name_plural = "Bonus sabablari"

class JarimaSabab(models.Model):
    nom = models.CharField(max_length=200)
    pul_miqdori = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ball_miqdori = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nom} | {self.pul_miqdori} so'm | {self.ball_miqdori} ball"
    
    class Meta:
        verbose_name = "Jarima sababi"
        verbose_name_plural = "Jarima sabablari"

class Xodim(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='xodim')
    ism = models.CharField(max_length=100)
    familya = models.CharField(max_length=100)
    telefon = models.CharField(max_length=20)
    
    # YANGI: Rasm maydoni
    rasm = models.ImageField(upload_to='xodim_rasmlari/', null=True, blank=True)
    
    # Bonus (ALOHIDA)
    bonus_ball = models.IntegerField(default=0)
    bonus_pul = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Jarima (ALOHIDA)
    jarima_ball = models.IntegerField(default=0)
    jarima_pul = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Reyting uchun (farq)
    reyting_ball = models.IntegerField(default=0)
    reyting_pul = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.ism} {self.familya}"
    
    def update_reyting(self):
        """Reytingni yangilash (bonus - jarima)"""
        self.reyting_ball = self.bonus_ball - self.jarima_ball
        self.reyting_pul = self.bonus_pul - self.jarima_pul
        self.save()
    
    class Meta:
        ordering = ['-reyting_ball']
        verbose_name = "Xodim"
        verbose_name_plural = "Xodimlar"

class BonusRecord(models.Model):
    xodim = models.ForeignKey(Xodim, on_delete=models.CASCADE, related_name='bonus_recordlari')
    sabab = models.ForeignKey(BonusSabab, on_delete=models.SET_NULL, null=True)
    pul_miqdori = models.DecimalField(max_digits=10, decimal_places=2)
    ball_miqdori = models.IntegerField()
    sana = models.DateTimeField(auto_now_add=True)
    izoh = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def save(self, *args, **kwargs):
        # Xodimning bonuslarini yangilash
        xodim = self.xodim
        xodim.bonus_ball += self.ball_miqdori
        xodim.bonus_pul += self.pul_miqdori
        xodim.update_reyting()
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        xodim = self.xodim
        xodim.bonus_ball -= self.ball_miqdori
        xodim.bonus_pul -= self.pul_miqdori
        xodim.update_reyting()
        super().delete(*args, **kwargs)
    
    class Meta:
        ordering = ['-sana']
        verbose_name = "Bonus yozuvi"
        verbose_name_plural = "Bonus yozuvlari"

class JarimaRecord(models.Model):
    xodim = models.ForeignKey(Xodim, on_delete=models.CASCADE, related_name='jarima_recordlari')
    sabab = models.ForeignKey(JarimaSabab, on_delete=models.SET_NULL, null=True)
    pul_miqdori = models.DecimalField(max_digits=10, decimal_places=2)
    ball_miqdori = models.IntegerField()
    sana = models.DateTimeField(auto_now_add=True)
    izoh = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    def save(self, *args, **kwargs):
        xodim = self.xodim
        xodim.jarima_ball += self.ball_miqdori
        xodim.jarima_pul += self.pul_miqdori
        xodim.update_reyting()
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        xodim = self.xodim
        xodim.jarima_ball -= self.ball_miqdori
        xodim.jarima_pul -= self.pul_miqdori
        xodim.update_reyting()
        super().delete(*args, **kwargs)
    
    class Meta:
        ordering = ['-sana']
        verbose_name = "Jarima yozuvi"
        verbose_name_plural = "Jarima yozuvlari"

class Reyting(models.Model):
    DAVR_TANLOVLARI = [
        ('kunlik', 'Kunlik'),
        ('haftalik', 'Haftalik'),
        ('oylik', 'Oylik'),
        ('yillik', 'Yillik'),
    ]
    
    xodim = models.ForeignKey(Xodim, on_delete=models.CASCADE, related_name='reytinglari')
    davr = models.CharField(max_length=20, choices=DAVR_TANLOVLARI)
    bonus_ball = models.IntegerField(default=0)
    bonus_pul = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    jarima_ball = models.IntegerField(default=0)
    jarima_pul = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reyting_ball = models.IntegerField(default=0)
    reyting_pul = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sana = models.DateField(default=timezone.now)
    
    def save(self, *args, **kwargs):
        if not self.sana:
            self.sana = timezone.now().date()
        super().save(*args, **kwargs)
    
    class Meta:
        unique_together = ['xodim', 'davr', 'sana']
        ordering = ['-reyting_ball']