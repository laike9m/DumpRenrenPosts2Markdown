import requests
import os,sys
import lxml.html as html
import pickle
import re
import getpass

HTML_DIR = 'original html'
DUMP_DIR = 'markdown'

class LoginRenRen():  
    
    s = requests.Session() 
      
    def __init__(self,name='',password='',domain=''):  
        self.name=name  
        self.password=password  
        self.domain=domain  
    
    def output_html(self, text, filename):
        filename += '.html'
        with open(os.path.join(HTML_DIR,filename), mode='w', encoding='utf-8') as f:
            f.write(text)
          
    def login(self):  
        params = {'domain': self.domain, 'email': self.name, 'password': self.password}  
        
        r = self.s.post(  
            'http://www.renren.com/PLogin.do',  
            data = params,
            allow_redirects = True,
        )  

        print('login.....')  
        
        print(r.url)
        self.user_url = r.url
        self.main_page = r.text


class Get_Blogpost(LoginRenRen):
    
    def __init__(self, name, password, domain):
        self.name=name  
        self.password=password  
        self.domain=domain  
        self.test_post_url = 'http://blog.renren.com/blog/282456584/863989702'  
        # 日志《《世界羽联的运动员行为条例》，先看看原文再说话》


    def get_test_post(self):
        r = self.s.get(self.test_post_url)
        with open('test_post.html', 'wt', encoding='utf-8') as f:
            f.write(r.text)  
    
    
    def get_posts_list(self):
        profile_page = self.user_url + '/profile'
        self.s.get(profile_page)
        rizhi_tab = profile_page + '?v=blog_ajax&undefined'
        r = self.s.get(rizhi_tab)
        #self.output_html(text=r.text, filename='pre')
        first_blog_url = html.fromstring(r.text).cssselect('[stats="blog_blog"]')[0].attrib['href']
        first_blog_title = html.fromstring(r.text).cssselect('[stats="blog_blog"]')[0].text
        r = self.s.get(first_blog_url)
        print("Generating 《%s》" % first_blog_title)
        self.output_html(text=r.text, filename='0.'+first_blog_title)
        
        # 先弄100篇, 之后可根据状态码或页面元素判断已到末尾
        for i in range(1,10000):
            try:
                next_blog_url = html.fromstring(r.text).cssselect(".a-nav .float-right a")[0].attrib['href']
                next_blog_title = html.fromstring(r.text).cssselect(".a-nav .float-right a")[0].text.lstrip('较旧一篇:')
                r = self.s.get(next_blog_url)
                print("Generating 《%s》" % next_blog_title)
                next_blog_title = re.sub(r'[<>"*\\/|?]', '', next_blog_title)   # 标题中的? -> '',: -> -
                next_blog_title = re.sub(':', '-', next_blog_title)
                self.output_html(text=r.text, filename=str(i)+'.'+next_blog_title)
            except:
                print("Unexpected error:", sys.exc_info()[0])
                print('Existing program...')
                break
              
              
if __name__=='__main__':
    0 if os.path.exists(HTML_DIR) else os.mkdir(HTML_DIR)
    0 if os.path.exists(DUMP_DIR) else os.mkdir(DUMP_DIR)
    
    domain = 'renren.com' 
    
    if os.path.exists('personal_info'):
        username, password = pickle.load(open('personal_info', 'rb'))
    else:  
        username = input('请输入用户名: ')
        password = getpass.getpass('请输入密码: ')
        
    #ren = LoginRenRen(username, password, domain)  
    #ren.login()
    
    ren_get_blogpost = Get_Blogpost(username, password, domain)
    try:
        ren_get_blogpost.login()
        ren_get_blogpost.get_posts_list()
        pickle.dump((username, password), open('personal_info', 'wb'))
    except:
        print("用户名或密码错误, 程序终止")
    