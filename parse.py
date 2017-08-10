#!/usr/bin/python
# encoding=utf-8
import time
import random
import os

def get_info(bsobj):
    info1 = bsobj.find('div', {'id': 'divHead'}).find('table').find('tbody').find('td').get_text()
    print(info1)

#将单个文件保存到本地
def save_file_now(member, user, bsobj):
    dir='E:/data/resumes/'+str(member)
    path=dir+"/"+str(user) + '_' + get_uid() + ".html"
    if not os.path.isdir(dir):
        os.makedirs(dir)

    file = open(path, 'w+', encoding='utf-8',
                errors='ignore')
    file.write(bsobj.prettify())
    file.flush()
    file.close()
    print("success!--"+path)

def get_uid():
    return str(int(time.time())) + str(int(random.uniform(0, 1) * 1000))
