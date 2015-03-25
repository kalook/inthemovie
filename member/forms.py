# -*- coding: utf-8 -*-
import re
from django import forms
from models import Users
from django.core.exceptions import ObjectDoesNotExist
import hashlib
# Login Form - 
class LoginForm(forms.Form):
    user_id = forms.CharField(label='Id ', widget=forms.TextInput(attrs={'class':'login_input'}), max_length=20)
    password = forms.CharField(
                               label='Password',
                               widget    = forms.PasswordInput(attrs={'class':'login_input'}),
                               max_length=20
                               )

    
    def clean(self):
        user_id     = self.cleaned_data.get('user_id')
        password    = self.cleaned_data.get('password')

# Join Form -
class JoinForm(forms.Form):
    user_id     = forms.CharField(label="아이디", max_length=20, 
                                  widget=forms.TextInput(attrs={'class':'memeber-form'})
                                  )
    
    password    = forms.CharField(label="비밀번호",
                               widget    = forms.PasswordInput(attrs={'class':'memeber-form'}),
                               max_length=20
                                  )
    password_re = forms.CharField(label="비밀번호확인",
                               widget    = forms.PasswordInput(attrs={'class':'memeber-form'}),
                               max_length=20
                                  )
    name        = forms.CharField(label="이름", max_length=20, 
                                  widget=forms.TextInput(attrs={'class':'memeber-form'})
                                  )
    nick_name   = forms.CharField(label="별명", max_length=20,
                                  widget=forms.TextInput(attrs={'class':'memeber-form'})
                                  )
    mobile_phone= forms.CharField(label="mobile phone", max_length=13,
                                  widget=forms.TextInput(attrs={'class':'memeber-form'})
                                  )
    email        = forms.EmailField(label='이메일',
                                    widget=forms.TextInput(attrs={'class':'memeber-form','size':50})
                                    )
    def clean_password_re(self):
        if 'password' in self.cleaned_data:
            password1 = self.cleaned_data['password']
            password2 = self.cleaned_data['password_re']
            if password1 == password2:
                return password2
        raise forms.ValidationError('비밀번호가 일치하지 않습니다.')

class MessageForm(forms.Form):
    recived_id  = forms.CharField(label="받는 사람",
                                 widget=forms.TextInput(attrs={'class':'memeber-form message-id'})
                                 )
    content     = forms.CharField(label="내용",
                                 widget=forms.Textarea(attrs={'class':'memeber-form message-content'})
                                  )
