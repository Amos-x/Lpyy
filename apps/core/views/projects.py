from django.shortcuts import render,HttpResponse,HttpResponseRedirect,reverse
from .. import models
from ..forms import AuthForm,ForgotForm,ChangePasswordForm,EditUserInfo,ChangeEmail,UploadImage
import requests
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from ..utils import send_mail_to_user,is_email
from django.views import View
from django.utils import timezone
from django.contrib import messages


def joblog(request,c,p,s,j):
    """ get job's log """
    if request.method == 'GET':
        if c and p and s and j:
            try:
                client_obj = models.Client.objects.get(id=c)
                url = 'http://{ip}:{port}/logs/{project}/{spider}/{job}.log'.format(ip=client_obj.ip,
                                                                                   port=client_obj.port,
                                                                                    project=p,
                                                                                    spider=s,
                                                                                    job=j)
                response = requests.get(url, timeout=5,
                                        auth=(client_obj.username, client_obj.password) if client_obj.auth else None)
                if response.status_code == 200:
                    return HttpResponse(response.text,content_type='text/plain')
            except:
                pass
        return HttpResponse(status=400)


@login_required
def index(request):
    clients = models.Client.objects.count()
    projects = models.Project.objects.count()
    running = 0
    tasks = 0
    return render(request,'index.html', {'clients': clients,'projects':projects,'running':running,'tasks':tasks})


def login(request):
    if request.method == 'GET':
        return render(request,'login.html')
    if request.method == 'POST':
        form = AuthForm(request.POST)
        if form.is_valid():
            username_or_email = request.POST.get('username_or_email')
            if is_email(username_or_email):
                user_obj = models.UserProfile.objects.filter(email=username_or_email).first()
            else:
                user_obj = models.UserProfile.objects.filter(username=username_or_email).first()
            if user_obj:
                password = request.POST.get('password')
                user = auth.authenticate(username=user_obj.username,password=password)
                if user is not None and user.is_active:
                    auth.login(request,user)
                    return HttpResponseRedirect(reverse('index'))
        messages.error(request,'账号或密码错误')
        return HttpResponseRedirect(reverse('login'))


@login_required
def logout(request):
    auth.logout(request)
    return HttpResponseRedirect(reverse('login'))


def forgot_password(request):
    if request.method == 'GET':
        return render(request, 'forgotpassword.html')

    if request.method == 'POST':
        forgot_form = ForgotForm(request.POST)
        if forgot_form.is_valid():
            username_or_email = request.POST.get('username_or_email')
            if is_email(username_or_email):
                user = models.UserProfile.objects.filter(email=username_or_email).first()
            else:
                user = models.UserProfile.objects.filter(username=username_or_email).first()
            if user and user.is_active:
                email_obj = models.EmailRecord.objects.filter(email=user.email).order_by('create_time').reverse().first()
                if email_obj:
                    time_diff = timezone.now() - email_obj.create_time
                    if time_diff.seconds < 60:
                        messages.warning(request,'请求过于频繁，请稍后一分钟再重试')
                        return HttpResponseRedirect(reverse('forgot_password'))
                status = send_mail_to_user(user.email,'forgot')
                if status:
                    messages.success(request,'重置密码邮件已发送')
                else:
                    messages.warning(request,'网络繁忙，请稍后重试')
            else:
                messages.warning(request,'该用户不存在或不可用')
        return HttpResponseRedirect(reverse('forgot_password'))


def reset_password(request,reset_code):
    if request.method == 'GET':
        email_obj = models.EmailRecord.objects.filter(code=reset_code,is_use=False).order_by('expire_time').reverse().first()
        if email_obj:
            expire_time = email_obj.expire_time
            now = timezone.now()
            if now < expire_time:
                return render(request,'resetpassword.html',{'reset_code':reset_code})
        messages.error(request,'此链接已失效，请重新发送重置密码邮件')
        return HttpResponseRedirect(reverse('forgot_password'))

    if request.method == 'POST':
        change_password_form = ChangePasswordForm(request.POST)
        if change_password_form.is_valid():
            email_obj = models.EmailRecord.objects.filter(code=reset_code, is_use=False).order_by('expire_time').reverse().first()
            user_obj = models.UserProfile.objects.get(email=email_obj.email)
            new_password = request.POST.get('password')
            user_obj.set_password(new_password)
            user_obj.save()
            email_obj.is_use = True
            email_obj.save()
            messages.success(request,'重置密码成功')
            return HttpResponseRedirect(reverse('login'))
        messages.error(request,'两次输入的密码不一致')
        return HttpResponseRedirect(reverse('reset_password'))


@login_required
def change_password(request):
    if request.method == 'GET':
        email = request.user.email
        email_obj = models.EmailRecord.objects.filter(email=email).order_by('create_time').reverse().first()
        if email_obj:
            time_diff = timezone.now() - email_obj.create_time
            if time_diff.seconds < 60:
                messages.warning(request,'请求过于频繁，请稍后一分钟再重试')
                return HttpResponseRedirect(reverse('userinfo'))
        status = send_mail_to_user(email, 'forgot')
        if status:
            messages.success(request,'重置密码邮件已发送')
        else:
            messages.warning(request,'网络繁忙，请稍后重试')
        return HttpResponseRedirect(reverse('userinfo'))


@login_required
def change_email(request):
    if request.method == 'POST':
        form = ChangeEmail(request.POST)
        if form.is_valid():
            email = request.POST.get('email')
            if request.user.email != email:
                user_obj = models.UserProfile.objects.filter(email=email)
                if user_obj:
                    messages.error(request,'此邮箱已被使用，无法重复绑定')
                else:
                    email_obj = models.EmailRecord.objects.filter(email=email).order_by('create_time').reverse().first()
                    if email_obj:
                        time_diff = timezone.now() - email_obj.create_time
                        if time_diff.seconds < 60:
                            messages.warning(request, '请求过于频繁，请稍后一分钟再重试')
                            return HttpResponseRedirect(reverse('userinfo'))
                    status = send_mail_to_user(email,'change_email',request.user.id)
                    if status:
                        messages.success(request,'验证绑定邮箱邮件已发送')
                    else:
                        messages.warning(request,'网络繁忙，请稍后重试')
        else:
            messages.error(request,'格式错误，请输入正确的邮箱')
        return HttpResponseRedirect(reverse('userinfo'))


def reset_email(request,user_id,reset_code):
    if request.method == 'GET':
        email_obj = models.EmailRecord.objects.filter(code=reset_code,is_use=False).order_by('create_time').reverse().first()
        if email_obj:
            if timezone.now() < email_obj.expire_time:
                user = models.UserProfile.objects.get(id=user_id)
                user.email = email_obj.email
                user.save()
                email_obj.is_use = True
                email_obj.save()
                messages.success(request,'邮箱已重置')
                return HttpResponseRedirect(reverse('userinfo'))
        messages.error(request,'此链接已失效，请重新发送绑定邮箱邮件')
        return HttpResponseRedirect(reverse('userinfo'))


@login_required
def user_profile(request):
    return render(request,'userprofile.html')


@login_required
def edit_userinfo(request):
    if request.method == 'POST':
        form = EditUserInfo(request.POST)
        if form.is_valid():
            username = request.POST.get('username')
            if request.user.username != username:
                user = models.UserProfile.objects.filter(username=username)
                if user:
                    messages.error(request,'用户信息更新失败，此用户名已被使用')
                    return HttpResponseRedirect(reverse('userinfo'))
                full_name = request.POST.get('full_name')
                request.user.username = username
                request.user.full_name = full_name
                request.user.save()
                messages.success(request,'用户信息更新成功')
        return HttpResponseRedirect(reverse('userinfo'))


def upload_img(request):
    # TODO 这里不知为何，用表单验证 is_vaild 无法验证成功，识别不了图片格式
    if request.method == 'POST':
        form = UploadImage(request.POST, request.FILES)
        # if form.is_valid():
        request.user.image = request.FILES.get('profile_photo')
        request.user.save()
        messages.success(request,'用户头像已更新')
        # else:
        #     messages.error(request,'请上传图片文件')
        return HttpResponseRedirect(reverse('userinfo'))


def settings(request):
    pass


def client_index(request):
    return render(request,'clients.html')
