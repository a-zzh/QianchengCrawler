#encoding=utf-8
#运行这段代码，会自动打开浏览器，然后访问百度。
from selenium import webdriver

browser = webdriver.Chrome()
browser.get('http://www.baidu.com/')
browser.close() #退出



