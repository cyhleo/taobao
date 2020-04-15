# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from PIL import Image
from io import BytesIO
from taobao import chaojiying
import random
from lxml import etree
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import pymongo
import logging
from taobao.settings import *


# 定义一个taobao类
class taobao_info(object):

    # 对象初始化
    def __init__(self):

        self.login_url = 'https://login.taobao.com/member/login.jhtml'
        # 微博账号
        self.wb_username = WB_USERNAME
        # 微博密码
        self.wb_password = WB_PASSWORD

        # 超级鹰账号
        self.cy_username = CY_USERNAME
        # 超级鹰密码
        self.cy_password = CY_PASSWORD
        # 超级鹰软件ID
        self.cy_id = CY_ID
        chrome_options = webdriver.ChromeOptions()

        # 添加无界面模式
        chrome_options.add_argument('--headless')

        # 不加载图片,加快访问速度
        chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})

        # 添加代理

        chrome_options.add_argument('--proxy-server=%s'%PROXY)

        # 添加user-agent
        chrome_options.add_argument(
            'user-agent={}'.format(USER_AGENT))

        chromedriver_path = 'D:/new python project/spider_files/new_spider_learn/taobao_test/chromedriverv75.exe'
        self.browser = webdriver.Chrome(executable_path=CHROMEDRIVER_PATH, chrome_options=chrome_options)


        # 超时时长为10s
        self.wait = WebDriverWait(self.browser, 10)

        # 连接MongoDB数据库
        client = pymongo.MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        self.collection = db[MONGO_COLLECTION]

        # 初始化日志
        self.logger = logging.getLogger(__name__)

    # 登录淘宝
    def login(self):
        """
        登录淘宝
        """

        # 打开网页
        self.browser.get(self.login_url)
        time.sleep(5)

        # 最大化网页
        self.browser.maximize_window()

        # 点击微博登录
        weibo_button = self.wait.until(EC.element_to_be_clickable((By.XPATH,'.//li[@id="J_OtherLogin"]/a[1]')))
        weibo_button.click()

        # 输入微博账号密码，并点击确认登录
        input_username = self.wait.until(EC.presence_of_element_located((By.NAME,'username')))
        input_username.send_keys(self.wb_username)
        time.sleep(1)
        input_password = self.browser.find_element_by_name('password')
        input_password.send_keys(self.wb_password)
        time.sleep(1)
        enter_button = self.browser.find_element_by_xpath('.//span[@node-type="submitStates"]')
        enter_button.click()

        # 如果出现验证码，将执行以下操作
        try:
            # 获取验证码
            img = self.wait.until(EC.presence_of_element_located((By.XPATH, './/div[@class="inp verify"]//img')))
            self.get_image_crop(img)
            time.sleep(1)
            # 通过超级鹰识别验证码
            code = self.get_code()

            # 输入验证码
            verifycode_input = self.browser.find_element_by_xpath('.//div[@class="inp verify"]/input')
            verifycode_input.send_keys(code)
            # 点击确认登录
            time.sleep(2)
            enter_button.click()
        except:
            pass

        self.wait.until(EC.presence_of_element_located((By.ID,'q')))


    def get_img_position(self, img):
        """
        或得验证码所在网页的相对位置
        :param img: 验证码img标签
        :return: 验证码相对于网页上下左右的位置
        """
        time.sleep(2)
        location = img.location
        size = img.size
        top, bottom, left, right = location['y'], location['y'] + size['height'], location['x'], location['x'] + size[
            'width']
        return top, bottom, left, right

    def get_image_crop(self, img):
        '''
        将验证码保存到./code.png文件中
        :param img:验证码img标签
        :return:
        '''
        top, bottom, left, right = self.get_img_position(img)

        # 获取网页的截屏screenshot
        screenshot = self.browser.get_screenshot_as_png()
        screenshot = Image.open(BytesIO(screenshot))

        # 将验证码从screenshot裁剪出来
        captcha = screenshot.crop((left, top, right, bottom))
        # 保存到文件中
        captcha.save(r'code.png')


    def get_code(self):
        """
        使用超级鹰获得验证码
        :return:验证码
        """
        cy = chaojiying.Chaojiying_Client(self.cy_username, self.cy_password, self.cy_id)
        im = open('code.png', 'rb').read()
        code = cy.PostPic(im, 1902)
        return code['pic_str']


    def search(self):

        # 在搜索框内输入要查询的物品
        input_q = self.wait.until(EC.presence_of_element_located((By.ID,'q')))
        input_q.send_keys(r'蒸烤一体机')
        time.sleep(2)
        button = self.wait.until(EC.element_to_be_clickable((By.XPATH,'.//button')))
        button.click()

        # 点击‘销量从高到低’按钮
        rank_button = self.wait.until(EC.presence_of_element_located((By.XPATH,'.//ul[@class="sorts"]/li[@class="sort"][2]/a[contains(@class,"link")]')))
        rank_button.click()

        # 等待页面加载完成
        self.wait.until(EC.presence_of_element_located((By.XPATH,'.//div[@class="total"]')))
        for page in range(1,101):
            self.get_page(page)



    def get_page(self,page):
        """
        获得网页的源码，并输入下一个要分析的页码
        :param page: 页码
        :return:
        """

        # 将网页下拉到最底部
        ActionChains(self.browser).send_keys(Keys.PAGE_DOWN).perform()
        time.sleep(3)

        # 获取页面输入框
        page_input = self.wait.until(EC.presence_of_element_located((By.XPATH,'.//input[contains(@class,"J_Input")]')))

        # 获取页面源码
        response = self.browser.page_source

        # 分析页面，提取item
        self.parse(response)


        s = random.uniform(1, 3)
        time.sleep(s)
        self.logger.info('正准备访问第{}页'.format(page))

        # 输入页码
        page_input.clear()
        page_input.send_keys(page)
        button = self.wait.until(EC.element_to_be_clickable((By.XPATH,'.//div[@class="form"]/span[contains(text(),"确定")]')))
        button.click()

    def parse(self,response):
        """
        分析页面，提取item
        :param response:
        :return:
        """
        html = etree.HTML(response)
        divs = html.xpath('.//div[@class="items"][1]/div')

        for div in divs:
            item = {}
            item['image'] = div.xpath('.//div[@class="pic"]//img/@src')[0]
            item['price'] = div.xpath('.//div[@class="price g_price g_price-highlight"]/strong/text()')[0]
            item['sale_num'] = div.xpath('.//div[@class="deal-cnt"]/text()')[0]
            a = div.xpath('.//div[@class="row row-2 title"]/a')
            item['title'] = a[0].xpath('string(.)').strip()
            item['shop'] = div.xpath('.//div[@class="shop"]/a/span[2]/text()')[0]

            self.mongo(item)


    def mongo(self,item):
        """
        将item保存至mongodb
        """
        self.collection.update({'title': item.get('title')}, {'$set': item}, True)

    def run(self):
        self.login()
        self.search()

if __name__ == "__main__":
    a = taobao_info()
    a.login()
    a.search()
