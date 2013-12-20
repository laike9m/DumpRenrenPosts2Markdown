import requests
import os
import lxml.html as html
import cssselect
import pickle

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
        with open(os.path.join(DUMP_DIR,'test_post.html'), mode='w', encoding='utf-8') as f:
            f.write(r.text)  
    
    
    def get_posts_list(self):
        self.s.get("http://www.renren.com/282456584/profile")   # person page
        r = self.s.get("http://www.renren.com/282456584/profile?v=blog_ajax&undefined") # rizhi tab
        self.output_html(r.text, 'pre')
        first_blog_url = html.fromstring(r.text).cssselect('[stats="blog_blog"]')[0].attrib['href']
        first_blog_title = html.fromstring(r.text).cssselect('[stats="blog_blog"]')[0].text
        r = self.s.get(first_blog_url)
        print("Generating 《%s》" % first_blog_title)
        self.output_html(r.text, 'post_0')
        
        # 先弄100篇, 之后可根据状态码或页面元素判断已到末尾
        for i in range(1000):
            try:
                next_blog_url = html.fromstring(r.text).cssselect(".a-nav .float-right a")[0].attrib['href']
                next_blog_title = html.fromstring(r.text).cssselect(".a-nav .float-right a")[0].text
                r = self.s.get(next_blog_url)
                print("Generating 《%s》" % next_blog_title)
                self.output_html(r.text, 'post_'+str(i))
            except:
                break
              
if __name__=='__main__':
    0 if os.path.exists(HTML_DIR) else os.mkdir(HTML_DIR)
    0 if os.path.exists(DUMP_DIR) else os.mkdir(DUMP_DIR)
    
    domain = 'renren.com' 
    if os.path.exists('personal_info'):
        username, password = pickle.load(open('personal_info', 'rb'))
    else:  
        username = input('请输入用户名: ')
        password = input('请输入密码: ')
        pickle.dump((username, password), open('personal_info', 'wb'))
        
    #ren = LoginRenRen(username, password, domain)  
    #ren.login()
    
    ren_get_blogpost = Get_Blogpost(username, password, domain)
    ren_get_blogpost.login()
    ren_get_blogpost.get_posts_list()
    