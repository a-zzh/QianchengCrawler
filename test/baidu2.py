#encoding=utf-8
#运行这段代码，会自动打开浏览器，然后访问百度。
from selenium import webdriver

browser = webdriver.Chrome()
browser.get('http://www.baidu.com/')
# elem=browser.find_element_by_id("quickdelete")
elem=browser.find_element_by_xpath('//*[@id="kw"]')
elem.send_keys("诚智汇达")
elem=browser.find_element_by_xpath("//*[@id='su']")
elem.click()
# browser.close() #退出




