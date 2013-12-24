'''
把每篇日志的html清理成只包含日志标题,正文,修改时间,分类,(评论)
识别:
<h3 class="title-article">
    <strong>缓慢地把人人日志导出...</strong>
    <span class="timestamp">2013-12-20 21:11</span>
    <span class="group">(分类:<a href='http://blog.renren.com/blog/0?bfrom=010203053&categoryId=0'>默认分类</a>)</span>
</h3>
<div id="blogContent" class="text-article" data-wiki="">
        正文...
</div>

从这里提取信息
'''

import lxml.html as html
import os
import glob


HTML_DIR = 'original html'
DUMP_DIR = 'markdown'

class Convert():
    def __init__(self):
        pass
    
    def get_html_list(self):
        self.html_list = glob.glob(os.path.join(HTML_DIR, '*.html'))
        
    
    def get_title(self, text):
        blog_page = html.fromstring(text)
        title = blog_page.cssselect('.title-article strong')[0].text
        return title
    
    
    def stringify_children(self, node):
        from lxml.etree import tostring
        from itertools import chain
        parts = ([node.text] +
                list(chain(*([tostring(c)] for c in node.getchildren()))) +
                [node.tail])
        # filter removes possible Nones in texts and tails
        return ''.join(filter(None, parts))

    
    def get_content(self, text):
        blog_page = html.fromstring(text)
        content = blog_page.cssselect('#blogContent')[0]
        content = self.stringify_children(content)
        #有待进一步研究
        #http://stackoverflow.com/questions/11938924/parsing-utf-8-unicode-strings-with-lxml-html
        #http://stackoverflow.com/questions/4624062/get-all-text-inside-a-tag-in-lxml#
        #http://stackoverflow.com/questions/6123351/equivalent-to-innerhtml-when-using-lxml-html-to-parse-html?lq=1
        return content
    
    
    def get_tag(self, text):
        blog_page = html.fromstring(text)
        tag = blog_page.cssselect('.title-article .group a')[0].text
        return tag
    

    def get_timestamp(self, text):
        blog_page = html.fromstring(text)
        timestamp = blog_page.cssselect('.timestamp')[0].text
        return timestamp
    
        
    def write2md(self):
        for file in self.html_list:
            with open(file, 'rt', encoding='utf-8') as f:
                text = f.read()
                title = self.get_title(text)
                content = self.get_content(text)
                tag = self.get_tag(text)
                timestamp = self.get_timestamp(text)
                lines = [title,'\n',timestamp,'\n',content,'\n',tag]
                filename = os.path.splitext(os.path.split(file))[0]
                with open(os.path.join(DUMP_DIR, filename), 'wt', encoding='utf-8') as md:
                    md.writelines(lines)


if __name__ == '__main__':
    c = Convert()
    c.get_html_list()
    c.write2md()