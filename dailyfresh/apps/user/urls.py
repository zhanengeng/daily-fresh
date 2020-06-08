from django.urls import path, re_path
# from user import views
from user.views import * # 导入类视图
from django.contrib.auth.decorators import login_required

 
urlpatterns = [
    # path("register", views.register, name="register"), # 注册
    # path("register_handle", views.register_handle, name="register_handle"), # 注册处理
    # path("send", views.sendmsg) # 测试邮件发送命令
    path("register", RegisterView.as_view(), name="register"), # 用类视图注册，as_view是继承于View的方法
    re_path("active/(?P<token>.*)", ActiveView.as_view(), name="active"), # 用户激活。这里选用了关键词捕获
    
    path("login", LoginView.as_view(), name="login"), # 登录页面
    path("logout", LogoutView.as_view(), name="logout"), # 注销登录

    path("", UserInfoView.as_view(), name="user"), # 用户中心-信息页
    path("order", UserOrderView.as_view(), name="order"), # 用户中心-订单页
    path("address", AddressView.as_view(), name="address"), # 用户中心-地址页
    



]


