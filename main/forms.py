from django import forms
from django.contrib.auth.models import User
from .models import *

class XodimForm(forms.ModelForm):
    username = forms.CharField(max_length=150, label='Login')
    password = forms.CharField(widget=forms.PasswordInput, label='Parol', required=False)
    
    class Meta:
        model = Xodim
        fields = ['ism', 'familya', 'telefon', 'rasm']  # rasm qo'shildi
    
    def save(self, commit=True):
        # User yaratish yoki mavjudini olish
        username = self.cleaned_data['username']
        password = self.cleaned_data.get('password')
        
        user, created = User.objects.get_or_create(username=username)
        if password:
            user.set_password(password)
            user.save()
        
        # Xodim yaratish
        xodim = super().save(commit=False)
        xodim.user = user
        
        if commit:
            xodim.save()
        
        return xodim

class BonusRecordForm(forms.ModelForm):
    class Meta:
        model = BonusRecord
        fields = ['xodim', 'sabab', 'izoh']
        widgets = {
            'izoh': forms.Textarea(attrs={'rows': 3}),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.sabab:
            instance.pul_miqdori = instance.sabab.pul_miqdori
            instance.ball_miqdori = instance.sabab.ball_miqdori
        
        if commit:
            instance.save()
        return instance

class JarimaRecordForm(forms.ModelForm):
    class Meta:
        model = JarimaRecord
        fields = ['xodim', 'sabab', 'izoh']
        widgets = {
            'izoh': forms.Textarea(attrs={'rows': 3}),
        }
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.sabab:
            instance.pul_miqdori = instance.sabab.pul_miqdori
            instance.ball_miqdori = instance.sabab.ball_miqdori
        
        if commit:
            instance.save()
        return instance

class XodimRasmForm(forms.ModelForm):
    class Meta:
        model = Xodim
        fields = ['rasm']