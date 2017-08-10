#!/usr/bin/python
# encoding=utf-8
import os
import re
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from parse import *

# 设置selenium参数
browser = webdriver.Chrome()
# browser = webdriver.Firefox()
wait = WebDriverWait(browser, 1800)   #设置超时时间
# browser.set_window_size = (1400 * 900)
browser.set_window_size = (1366 * 768)


class Spider(object):
    def __init__(self, get_info):
        self.get_info = get_info

    # 模拟登录
    def login(self, member, user, password):
        logging.basicConfig(filename='error_index.log', level=logging.INFO)
        try:
            browser.get('http://ehire.51job.com/MainLogin.aspx')
            # 填入会员名、用户名、密码
            member_name = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#txtMemberNameCN')))
            user_name = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#txtUserNameCN')))
            passwd = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#txtPasswordCN')))
            member_name.clear()
            user_name.clear()
            passwd.clear()
            member_name.send_keys(member)
            user_name.send_keys(user)
            passwd.send_keys(password)
            # 点击验证码
            yzm = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#btnBeginValidate')))
            yzm.click()
            # 手工输入验证码完成后，自动点击验证按钮
            # verify = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '#btnValidate.yz-bot-btn.on')))
            verify = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#btnValidate.yz-bot-btn.on')))
            verify.click()
            # 点击登录
            submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#Login_btnLoginCN')))
            submit.click()
            # 检测是否模拟登陆是否成功(通过查看'立即登录'按钮是否存在进行判断)
            if BeautifulSoup(browser.page_source, 'lxml').find('a', {'id': 'Login_btnLoginCN'}):
                print('模拟登陆失败,请重试！')
                self.login(member, user, password)
            elif BeautifulSoup(browser.page_source, 'lxml').find('a',text='强制下线'):
                #判断是否需要强制下线,强制下线
                elem = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,'#gvOnLineUser > tbody > tr:nth-child(2) > td:nth-child(5) > a')))
                elem.click()
        except Exception as e:
            logging.info(member + '\n' + user + '\n' + password + '\n' + str(e.args))
            print('登录失败,错误信息已经纪录到error.log:%s' % str(e.args))

    #获取简历页面并保存
    def save_resume(self, url, headers, member, user):
        logging.basicConfig(filename='error.log', level=logging.INFO)
        try:
            # proxy = {'http':requests.get()}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                bsobj = BeautifulSoup(response.text, 'lxml')
                # 检测是否出现验证码,正常返回数据则调用解析简历函数get_info()
                if bsobj.find('a', {'id': 'btnValidate'}):
                    #在浏览器中打开验证码
                    browser.get(url)
                    yzm_verify = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.yz-bot-btn.on')))
                    yzm_verify.click()
                    #获取当前页数据
                    bsobj = BeautifulSoup(response.text, 'lxml')
                    if bsobj.find('td',text='求职意向'):
                        save_file_now(member, user,bsobj)
                else:
                    save_file_now(member, user, bsobj)
        except Exception as e:
            logging.info(str(member) + ':' + str(user) + ':' + url + '\n')
            print('解析简历详细资料出错,已经纪录到文件error.profile')

    # 解析简历页
    def parse_resume(self, url, headers, member, user, password):
        logging.basicConfig(filename='error_profile.log', level=logging.INFO)
        try:
            # proxy = {'http':requests.get()}
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                bsobj = BeautifulSoup(response.text, 'lxml')
                # 检测是否出现验证码,正常返回数据则调用解析简历函数get_info()
                if bsobj.find('td', text='求职意向') or bsobj.find('td', text='更多信息') or bsobj.find('td',
                                                                                                text='Job Preferences'):
                    # 解析简历页函数
                    get_info(bsobj)
                    print('%s的简历页解析完成' % re.compile(r'hidSeqID=(.*?)&').search(str(url)).group(1))
                # 没有出现预期数据,则判定为出现了验证码,在浏览器中打开验证码页面
                else:
                    browser.get(url)
                    yzm_verify = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.yz-bot-btn.on')))
                    yzm_verify.click()
                    if bsobj.find('td', text='求职意向') or bsobj.find('td', text='更多信息'):
                        # 解析简历页函数
                        self.get_info(bsobj)
                        print('%s的简历页解析完成' % re.compile(r'hidSeqID=(.*?)&').search(str(url)).group(1))
                    else:
                        self.parse_resume(url, headers)
        except Exception as e:
            logging.info(str(member) + ':' + str(user) + ':' + str(password) + ':' + url + '\n')
            print('解析简历详细资料出错,已经纪录到文件error.profile')

    # 获取索引页中所有简历的id,并下载简历
    def get_ids(self, num, member, user):
        try:
            i=0
            # 获取本页所有求职者id
            bsobj = BeautifulSoup(browser.page_source, 'lxml')
            urls = bsobj.findAll('a', {'class': 'a_username'})
            length = len(urls) #[0,length)
            for i in range(length):
                url = 'http://ehire.51job.com/' + urls[i].attrs['href']
                f_urls.write(url + '\n')
                # 获取简历详情页
                # self.save_resume(num,url, headers, member, user)

        except Exception as e:
            print('抓取%s-%s的第%s索引页id失败' % (member, user, i))

    # 处理索引页验证码输入错误,进行重新输入
    def yzm_index(self, i, member, user, password):
        try:
            # 跳转到下一页
            next_page = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#pagerBottomNew_nextButton')))
            next_page.click()
            # 检查是否跳验证码页面
            bsobj_verify = BeautifulSoup(browser.page_source, 'lxml')
            if not bsobj_verify.find('a', text='匹配度') and not bsobj_verify.find('a', {'id': 'Login_btnLoginCN'}):
                yz_able = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#btnValidate')))
                yz_able.click()
                # 检测验证码是否输入正确,不正确继续匹配验证
                if not BeautifulSoup(browser.page_source, 'lxml').find('a', text='匹配度'):
                    self.yzm_index(i, member, user, password)
                else:
                    # 获取该页的所有求职者id
                    self.get_ids(i, member, user)
            else:
                # 获取该页的所有求职者id
                self.get_ids(i, member, user)
                print('获取简历索引页第%s页数据成功' % str(i + 2))
        except Exception as e:
            self.yzm_index(i, member, user, password)
            print('翻页失败,正在进行重试:%s' % str(e.args))


    #实时获取cookies


    # 获取简历索引页中每份简历的id
    def get_resume(self, member, user, password):
        global headers
        global page_nums
        global i
        logging.basicConfig(filename='error.log', level=logging.INFO)
        try:
            # 跳转到应聘管理页
            resume = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#MainMenuNew1_m2')))
            resume.click()
            # 获取cookies(放在点击应聘管理页后,可以确保cookies中的HRUSERINFO加载完成)
            for item in browser.get_cookies():
                if item.get('name') == 'HRUSERINFO':
                    cookie = 'HRUSERINFO' + '=' + item.get('value')
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36',
                'Cookie': cookie
            }
            # 添加延迟,等待页码标签加载完成,获取页码数
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,
                                                               '#form1 > div.commonMain > div > div.fn-main.list-main > div.list-table-title.clearfix > ul.page-ft-r.clearfix > li.Search_num-set > span')))
            bsobj = BeautifulSoup(browser.page_source, 'lxml')
            page_nums = int(
                bsobj.find('ul', {'id': 'ul_selectlist'}).parent.findAll('ul')[1].find('select').parent.find(
                    'span').get_text().split('/')[1])
            # 获取第1页所有求职者id
            self.get_ids(1, member, user)
            print('获取简历索引页第1页数据成功')
            # 此处需要测试,看是否出现页数为0的情况!!
            if page_nums == 1:
                return True
            else:
                for i in range(page_nums - 1):
                    # 检测是否出现验证码,若未出现，获取下页全部简历id
                    self.yzm_index(i, member, user, password)
            return True
        except Exception as e:
            logging.info(member + '\n' + user + '\n' + password + '\n' + str(e.args))
            print('应聘管理页程序出错,正在重试%s' % str(e.args))
            # for x in range(page_nums-1-i):
            # self.yzm_index(i,member,user,password)

    # 主程序
    def main(self, member, user, password):
        logging.basicConfig(filename='error.log', level=logging.INFO)
        try:
            global f_urls
            f_urls = open(os.getcwd() + r'\\' + str(member) + '_' + str(user) + r'_urls.txt', 'a+', encoding='utf-8',
                          errors='ignore')
            #登录
            self.login(member, user, password)
            #得到账户下的所有简历
            result=self.get_resume(member, user, password)
            if result:
                with open(os.getcwd() + r'\\' + str(member) + '_' + str(user) + r'_urls.txt', 'r', encoding='utf-8',
                          errors='ignore') as f:
                    idl = f.read().split('\n')
                    f.close()
                    print(idl.__sizeof__())
                for url in idl:
                    # self.parse_resume(url, headers, member, user, password)
                    self.save_resume(url, headers, member, user)
            f_urls.close()
        except Exception as e:
            logging.info(member + '\n' + user + '\n' + password + '\n' + str(e.args))
            print('主程序出错啦:%s' % str(e.args))

    # 入口程序
    def run(self):
        # 遍历hr列表,拿到member,user,password
        ####
        self.main('诚智汇达', 'CZHD808', 'czhd1234')


if __name__ == '__main__':
    spider_51 = Spider(get_info)
    spider_51.run()
