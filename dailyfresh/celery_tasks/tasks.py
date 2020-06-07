# 使用celery
from celery import Celery
from django.conf import settings
from django.core.mail import send_mail # 发送邮件模块

# 为任务处理者(worker)进行django环境初始化，这段代码写于worker所在的电脑
#================================
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dailyfresh.settings') 
django.setup()
#================================


# 创建celery类的实例对象
#================================
app = Celery("celery_tasks.tasks", broker="redis://127.0.0.1:6379/1") # 1号数据库作为broker
#================================


# 定义任务函数
#================================
@app.task
def send_register_active_email(to_email, username, token):
    '''发送激活邮件'''
    # 阻止邮件信息
    subject = "天天生鲜欢迎信息"
    message = "" # 如果信息带格式（<h1>），用html_message发送
    html_message = f"<h1>{username},欢迎您成为天天生鲜会员</h1>请点击下面链接激活账户<br/><a href='http://127.0.0.1:8000/user/active/{token}'>http://127.0.0.1:8000/user/active/{token}</a>" 
    # 邮件地址的重点是user/active。向active发送token
    sender = settings.DEFAULT_FROM_EMAIL
    receiver_list = [to_email]
    send_mail(subject, message, sender, receiver_list, html_message=html_message)
#================================