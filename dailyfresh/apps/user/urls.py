from django.urls import path, re_path
# from user import views
from user.views import * # 导入类视图

 
urlpatterns = [
    # path("register", views.register, name="register"), # 注册
    # path("register_handle", views.register_handle, name="register_handle"), # 注册处理
    # path("send", views.sendmsg) # 测试邮件发送命令
    path("register", RegisterView.as_view(), name="register"), # 用类视图注册，as_view是继承于View的方法
    re_path("active/(?P<token>.*)", ActiveView.as_view(), name="active"), # 用户激活。这里选用了关键词捕获
    path("login", LoginView.as_view(), name="login"), # 登录页面
]
