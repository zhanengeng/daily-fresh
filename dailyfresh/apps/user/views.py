from django.shortcuts import render, redirect # 渲染，重定向
from django.http import HttpResponse 
from django.urls import reverse # 反向解析
from user.models import User, Address # 从模块导入User，用于写入数据库
from goods.models import GoodsSKU #导入商品SKU类
from django.views import View # 导入类视图

# 用户激活所需模块
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer# 加密用模块
from itsdangerous import SignatureExpired # 加密过期时的异常
from django.conf import settings # 导入settings.py.这里用于导入秘钥
from celery_tasks.tasks import send_register_active_email # 导入自定义的celery发送邮件模块

# django自带用户验证模块（django文档里找）
from django.contrib.auth import authenticate, login, logout # db查验用户，session记录登录状态, 退出并删除session
from django.contrib.auth.mixins import LoginRequiredMixin # 拒绝非登录用户访问类视图
from django_redis import get_redis_connection # 链接redis原生客户端（for 储存浏览记录）



import re # 正则

# Create your views here.

# /user/register
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

        # 3.业务处理：进行用户注册。利用django自带注册模块create_user
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

        # 3-2 发邮件（利用celery来发送）
        send_register_active_email.delay(email, username, token)
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
        # 判断是否记住了用户名
        if "username" in request.COOKIES:
            username = request.COOKIES.get("username")
            checked = "checked" # 同时checkbox自动勾选
        else:
            username = ""
            checked = ""
        
        # 使用模板
        return render(request, "login.html",{"username":username, "checked":checked})

    def post(self,request):
        '''进行登录校验'''
        # 接受数据
        username = request.POST.get("username")
        password = request.POST.get("pwd")

        # 校验数据
        if not all([username, password]):
            return render(request, "login.html", {"errmsg":"数据不完整"})
        
        
        # 业务处理（用django自带的认证系统）
        user = authenticate(username=username, password=password) # django会去数据库对比,正确是返回一个用户对象
        if user is not None:
            # 用户名或密码正确
            
            if user.is_active:
                # 用户已激活
                login(request, user) # 在session中记录用户登录状态(django自带)

                # 获取登录后索要跳转的地址(next), 默认跳转到首页reverse("goods:index")
                next_url = request.GET.get("next", reverse("goods:index"))

                # 跳转到next_url
                response = redirect(next_url) # HttpResponseRedirect

                # 判断是否需要记住用户名
                remember = request.POST.get("remember")
                if remember == "on":
                    # 需要记住用户名（cookie）
                    response.set_cookie("username", username, max_age=7*24*3600)
                else:
                    response.delete_cookie("username")
                # 返回response
                return response

            else:
                # 用户未激活
                return render(request, "login.html", {"errmsg":"用户未激活，请激活"})

        else:
            # 用户名或密码错误
            return render(request, "login.html", {"errmsg":"用户名或密码错误"})

# user/logout
class LogoutView(View):
    def get(self, request):
        '''退出登录'''
        # 清楚用户session信息
        logout(request)

        #跳转到首页
        return redirect(reverse('goods:index'))


# 以下三个页面，用户登录后才能访问，传入LoginRequiredMixin
# /user
class UserInfoView(LoginRequiredMixin,View):
    '''用户中心-信息页面'''
    def get(self, request):
        # 获取用户个人信息
        user = request.user
        address = Address.objects.get_default_address(user)

        # 获取用户历史浏览(Redis数据库)
        # from redis import StrictRedis
        # StrictRedis(host="127.0.0.1", port="6379" ,db=2) # redis的2号数据库保存用户浏览信息
        con = get_redis_connection("default") # default是setting里设定的redis数据库信息。con得到StrictRedis对象，用的2号数据库
        history_key = f"history_{user.id}" # 人为设定redis中储存格式为history_id:[1，2，3]
        # 获取用户最新浏览的5条商品id（看redis与python交互）
        sku_ids = con.lrange(history_key, 0, 4) # 向con传入key，得到一个浏览记录id列表
        # 从mysql数据库中查询用户浏览商品的具体信息,为了保证顺序不乱，使用以下遍历的方法获得商品实例对象
        goods_li = []
        for id in sku_ids:
            goods = GoodsSKU.objects.get(id=id)
            goods_li.append(goods)
        
        context = {"page":"user", 
                    "address":address,
                    "goods_li":goods_li}

        # page='user'用于定位所显示页面
        return render(request, "User_center_info.html", context)



# /user/order
class UserOrderView(LoginRequiredMixin, View):
    '''用户中心-订单页面'''
    def get(self, request):
        # 获取用户订单信息

        # page='order'
        return render(request, "User_center_order.html", {"page":"order"})

# /user/address
class AddressView(LoginRequiredMixin, View):
    '''用户中心-地址页面'''
    def get(self, request):
        # 获取用户登录的user对象
        user = request.user
        # try:
        #     # 获取用户默认收货地址
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     # 不存在默认收货地址
        #     address = None
        address = Address.objects.get_default_address(user)

        # 使用模板
        return render(request, "User_center_site.html",{"page":"address","address":address})

    def post(self, request):
        '''地址添加'''
        # 接受数据
        receiver = request.POST.get("receiver")
        addr = request.POST.get("addr")
        zip_code = request.POST.get("zip_code")
        phone = request.POST.get("phone")

        # 校验数据
        if not all([receiver, addr, phone]):
            return render(request, "user_center_site.html", {"errmsg":"数据不完整"})
        # 校验手机号
        if not re.match(r"^1[3|4|5|7|8][0-9]{9}$", phone):
            return render(request, "user_center_site.html", {"errmsg":"手机号格式不正确"})

        # 业务处理：地址添加
        # 如果用户已存在默认收货地址，添加的地址不作为默认地址，否则作为默认收货地址
        # 获取用户登录的user对象
        user = request.user
        # try:
        #     address = Address.objects.get(user=user, is_default=True)
        # except Address.DoesNotExist:
        #     # 不存在默认收货地址
        #     address = None
        address = Address.objects.get_default_address(user)

        if address:
            # 用户有默认收货地址
            is_default = False
        else:
            # 用户没有默认地址，则此次上传地址作为默认
            is_default = True

        # 添加地址
        Address.objects.create(user=user, 
                                receiver=receiver, 
                                addr=addr, 
                                zip_code=zip_code,
                                phone=phone, 
                                is_default=is_default)

        # 返回应答,刷新地址页面
        return redirect(reverse("user:address")) # get方式访问