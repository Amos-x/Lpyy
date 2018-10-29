# __author__: Amos,Chinese
# Email：379833553@qq.com

from django import forms


class AuthForm(forms.Form):
    username_or_email = forms.CharField(label='username_or_email',max_length=128, widget=forms.TextInput,required=True)
    password = forms.CharField(label='password',max_length=128,widget=forms.PasswordInput,required=True)


class ForgotForm(forms.Form):
    username_or_email = forms.CharField(required=True,label='username_or_email',widget=forms.TextInput)
    captcha = forms.CharField(required=False)


class ChangePasswordForm(forms.Form):
    password = forms.CharField(max_length=100,min_length=6,required=True)
    r_password = forms.CharField(max_length=100,min_length=6,required=True)

    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError(u"所有项都为必填项")
        elif self.cleaned_data['password'] != self.cleaned_data['r_password']:
            raise forms.ValidationError(u"两次输入的密码不一致")
        else:
            cleaned_data = super(ChangePasswordForm, self).clean()
        return cleaned_data


class ChangeEmail(forms.Form):
    email = forms.EmailField(max_length=128,required=True)


class EditUserInfo(forms.Form):
    full_name = forms.CharField(max_length=10,required=True)
    username = forms.CharField(max_length=32,required=True)


class UploadImage(forms.Form):
    image = forms.ImageField()
