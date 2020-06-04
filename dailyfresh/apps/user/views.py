from django.shortcuts import render, redirect # 渲染，重定向
from django.http import HttpResponse 
from django.urls import reverse # 反向解析
from user.models import User # 从模块导入User，用于写入数据库
from django.views import View # 导入类视图

# 用户激活所需模块
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer# 加密用模块
from itsdangerous import SignatureExpired # 加密过期时的异常
from django.conf import settings # 导入settings.py.这里用于导入秘钥
from django.core.mail import send_mail # 发送邮件模块

import re # 正则

# Create your views here.

# /user/register
def register(request):
    '''登録画面（getリクエスト）＆登録処理（Postリクエスト）'''
    if request.method == "GET":
        # 若为get请求，表示登録画面
        return render(request, 'register.html')

    elif request.method == "POST":
        # 若为post请求，说明是表单提出，进行登録処理
        # 1.接收数据
        username = request.POST.get("user_name")
        password = request.POST.get("pwd")
        email = request.POST.get("email")
        allow = request.POST.get("allow")

        # 2.进行校验
        # 2-1.校验数据完整性
        if not all([username, password, email]):
            # 数据不完整
            return render(request, 'register.html', {"errmsg":"数据不完整"})
        
        # 2-2.校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, "register.html", {"errmsg":"邮箱格式不正确"})

        # 2-3.是否勾选同意
        if allow != "on":
            return render(request, "register.html", {"errmsg":"请同意协议"})

        # 2-4.用户名是否重复
        try:
            # 用户名重复
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名还未被注册
            user = None

        if user:
            # 用户名已存在
            return render(request, "register.html", {"errmsg":"用户名已存在"})

        # 3.业务处理：进行用户注册
        # 一般方法：
        # user = User()
        # user.username = username
        # user.password = password
        # ...
        # user.save()

        # 利用django自带注册模块：
        user = User.objects.create_user(username, email, password) 
        user.is_active = 0
        user.save()

        # 4.返回应答，跳转首页。这里利用了重定向和反向解析
        return redirect(reverse('goods:index'))

def register_handle(request):
    '''和上方的post处理相同，可以用一个urls来处理，也可以这样分开来处理'''
    pass

class RegisterView(View):
    '''自己定义类视图，用于相应不同的解决方法'''
    def get(self, request):
        '''显示注册页面'''
        return render(request, "register.html")

    def post(self, request):
        '''注册处理'''
        # 若为post请求，说明是表单提出，进行登録処理
        # 1.接收数据
        username = request.POST.get("user_name")
        password = request.POST.get("pwd")
        email = request.POST.get("email")
        allow = request.POST.get("allow")

        # 2.进行校验
        # 2-1.校验数据完整性
        if not all([username, password, email]):
            # 数据不完整
            return render(request, 'register.html', {"errmsg":"数据不完整"})
        
        # 2-2.校验邮箱
        if not re.match(r'^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
            return render(request, "register.html", {"errmsg":"邮箱格式不正确"})

        # 2-3.是否勾选同意
        if allow != "on":
            return render(request, "register.html", {"errmsg":"请同意协议"})

        # 2-4.用户名是否重复
        try:
            # 用户名重复
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # 用户名还未被注册
            user = None

        if user:
            # 用户名已存在
            return render(request, "register.html", {"errmsg":"用户名已存在"})

        # 3.业务处理：进行用户注册。利用django自带注册模块
        # 向数据库写入username，email，password
        user = User.objects.create_user(username, email, password) 
        user.is_active = 0 # 默认是未激活状态，邮件确认后激活
        user.save()

        # 3-1.加密用户的身份信息
        # 创建实例对象 Serializer(秘钥，过期时间)
        serializer = Serializer(settings.SECRET_KEY, 3600)
        info = {"confirm":user.id} # 利用id确认用户身份
        token = serializer.dumps(info) # 利用实例对象的dumps方法进行加密.格式：bytes
        token = token.decode() # 把bytes => utf8

        # 3-2 发邮件
        subject = "天天生鲜欢迎信息"
        message = "" # 如果信息带格式（<h1>），用html_message发送
        html_message = f"<h1>{username},欢迎您成为天天生鲜会员</h1>请点击下面链接激活账户<br/><a href='http://127.0.0.1:8000/user/active/{token}'>http://127.0.0.1:8000/user/active/{token}</a>" 
        # 邮件地址的重点是user/active。向active发送token
        sender = settings.DEFAULT_FROM_EMAIL
        receiver_list = [email]
        send_mail(subject, message, sender, receiver_list, html_message=html_message)

        # 3-3 激活(用类ActiveView激活)
        # 4.返回应答，跳转首页。这里利用了重定向和反向解析
        return redirect(reverse('goods:index'))       

class ActiveView(View):
    # 用户点击邮件链接后，会像服务器发送一个get请求
    def get(self, request, token):  # token是从urls捕获的加密id
        '''用户激活'''
        # 进行解密，获取要激活的用户信息。
        # 创建实例对象，注意和上面加密用的对象具备相同的秘钥和加密时间。
        serializer = Serializer(settings.SECRET_KEY, 3600)
        try:
            info= serializer.loads(token) # 解密
            # 获取待激活用户id
            user_id = info["confirm"] # 加密前的info是个字典{"confirm":user.id}
            # 从数据库根据id获取用户
            user = User.objects.get(id=user_id)
            user.is_active = 1 # 激活
            user.save()
            # 激活后跳转到登录页面(利用反向解析)
            return redirect(reverse('user:login')) 


        except SignatureExpired as e:
            #激活链接已过期。（实际项目中，应该返回一个页面，点击按钮重新发送邮件）
            return HttpResponse("激活链接已过期")

# /user/login
class LoginView(View):
    '''登录页面'''
    def get(self, request):
        '''显示登录页面'''
        return render(request, "login.html")

# 邮件发送测试用。
# def sendmsg(request):
#     subject = "天天生鲜欢迎信息"
#     message = "邮件正文"
#     sender = settings.DEFAULT_FROM_EMAIL
#     receiver_list = ['zhanengeng1@yahoo.co.jp']
#     try:
#         send_mail(subject, message, sender, receiver_list)
#         return HttpResponse("成功发送邮件")
#     except Exception:
#         return HttpResponse("失败")