# taobao
该项目实现了淘宝模拟登录，爬取了2019年12月3月13号，‘蒸烤一体机’的商品详情信息。

# 部分结果展示
![](https://github.com/cyhleo/taobao/blob/master/img/result.png)    

# 项目说明
![](https://github.com/cyhleo/taobao/blob/master/img/example1.png)               
![](https://github.com/cyhleo/taobao/blob/master/img/example2.png)         

1. 淘宝登录接口对selenium的webdriver进行了特征标识，选择如上图所示的微博登录接口，使用selenium来模拟登录，使用超级鹰来识别如下图所示的图形验证码，从而实现账号密码登录。       

![](https://github.com/cyhleo/taobao/blob/master/img/example3.png)     

2. 使用selenium和ChromeDriver实现页面的下载功能，为ChromeDriver添加user-agent和代理。ChromeDriver使用无界面模式，并禁用图片加载功能，提升爬取效率。          

3. 使用xpath将非结构数据转化为结构数据，并将其持久化到MongoDB数据库。


# 项目运行方式
在taobao\settings.py文件中填写微博账号密码、超级鹰账号密码等信息。            
运行taobao\run.py文件

# 告示
本代码仅作学习交流，切勿用于商业用途。如涉及侵权，请告知，会尽快删除。
