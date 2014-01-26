import requests
import os
import sys
import lxml.html as html
import pickle
import re
import getpass

import html2md

HTML_DIR = 'original html'
DUMP_DIR = 'markdown'


class LoginRenRen():  
    
    s = requests.Session() 
      
    def __init__(self, name='', password='', domain=''):
        self.name = name
        self.password = password
        self.domain = domain
        self.user_url = ''

    @staticmethod
    def output_html(text, filename):
        filename += '.html'
        with open(os.path.join(HTML_DIR, filename), mode='wt', encoding='utf-8') as f:
            f.write(text)
          
    def login(self):  
        params = {'domain': self.domain, 'email': self.name, 'password': self.password}  
        
        r = self.s.post(  
            'http://www.renren.com/PLogin.do',  
            data=params,
            allow_redirects=True,
        )  

        print('login.....')  
        print(r.url)
        self.user_url = r.url
        self.output_html(text=r.text, filename='main_page')  # step 1


class GetBlogpost(LoginRenRen):
    
    def __init__(self, name, password, domain):
        self.name = name
        self.password = password
        self.domain = domain

    def get_posts_list(self):
        profile_page = self.user_url + '/profile'
        r = self.s.get(profile_page)
        self.output_html(text=r.text, filename='profilepage')   # step 2
        
        rizhi_tab = profile_page + '?v=blog_ajax&undefined'
        r = self.s.get(rizhi_tab)
        self.output_html(text=r.text, filename='rizhi_tab')   # step 3 
        
        first_blog_url = html.fromstring(r.text).cssselect('[stats="blog_blog"]')[0].attrib['href']
        first_blog_title = html.fromstring(r.text).cssselect('[stats="blog_blog"]')[0].text
        r = self.s.get(first_blog_url)
        if sys.stdout.encoding == 'UTF-8':
            print("Generating 《%s》" % first_blog_title)
        else:
            print('0')
        self.output_html(text=r.text, filename='0.'+first_blog_title)
        
        # 根据状态码或页面元素判断已到末尾
        for i in range(1, 10000):
            next_blog_element = html.fromstring(r.text).cssselect(".a-nav .float-right a")
            if next_blog_element:
                next_blog_url = next_blog_element[0].attrib['href']
            else:
                break   # already the last blogpost
            next_blog_title = html.fromstring(r.text).cssselect(".a-nav .float-right a")[0].text.lstrip('较旧一篇:')
            r = self.s.get(next_blog_url)
            if sys.stdout.encoding == 'UTF-8':
                print("Generating 《%s》" % next_blog_title)
            else:
                print(i)
            next_blog_title = re.sub(r'[<>"*\\/|?]', '', next_blog_title)   # 标题中的? -> '',: -> -
            next_blog_title = re.sub(':', '-', next_blog_title)
            self.output_html(text=r.text, filename=str(i)+'.'+next_blog_title)


def main():
    os.environ["PYTHONIOENCODING"] = 'utf_8'
    0 if os.path.exists(HTML_DIR) else os.mkdir(HTML_DIR)
    0 if os.path.exists(DUMP_DIR) else os.mkdir(DUMP_DIR)

    domain = 'renren.com'

    if os.path.exists('personal_info'):
        username, password = pickle.load(open('personal_info', 'rb'))
    else:
        username = input('请输入用户名: ')
        password = getpass.getpass('请输入密码: ')

    ren_get_blogpost = GetBlogpost(username, password, domain)
    try:
        ren_get_blogpost.login()
    except:
        print("用户名或密码错误, 程序终止")

    ren_get_blogpost.get_posts_list()
    pickle.dump((username, password), open('personal_info', 'wb'))

    c = html2md.Convert()
    c.get_html_list()
    c.write2md()


if __name__ == '__main__':
    main()
