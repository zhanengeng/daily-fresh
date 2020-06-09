## instructions
a django project

## functions
 1. register
 2. login/logout
 3. user_center: info ,order ,address
 4. index：can_order
 5. 

## virtualenv info:
|Package   |Version  |
|--|--|
amqp | 2.6.0      
billiard|       3.6.3.0
celery         |4.4.4  
Django         |2.2.6  
django-redis   |4.12.1  
django-tinymce |2.6.0  
future         |0.18.2  
itsdangerous   |1.1.0  
kombu          |4.6.10  
mysqlclient    |1.4.6  
Pillow         |7.1.2  
pip           | 20.1.1  
pytz           | 2020.1  
redis          |3.5.3  
setuptools    | 41.2.0  
sqlparse      | 0.3.1  
vine          | 1.3.0  

## 页面说明：
1.index.html   网站首页，顶部“注册|登录”和用户信息是切换显示的，商品分类菜单点击直接链接滚动到本页面商品模块。首页已加入幻灯片效果。
2.list.html  商品列表页，商品分类菜单鼠标悬停时切换显示和隐藏，点击菜单后链接到对应商品的列表页。
3.detail.html  商品详情页，某一件商品的详细信息。
4.cart.html 我的购物车页，列出已放入购物车上的商品
5.place_order.html 提交订单页
6.login.html 登录页面
7.register.html 注册页面，已加入了初步的表单验证效果
8.user_center_info.html 用户中心-用户信息页 用户中心功能一，查看用户的基本信息
9.user_center_order.html 用户中心-用户订单页 用户中心功能二，查看用户的全部订单
10.user_center_site.html 用户中心-用户收货地址页 用户中心功能三，查看和设置用户的收货地址
