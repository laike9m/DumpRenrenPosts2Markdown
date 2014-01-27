# -*- coding:utf-8 -*-
"""
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
"""

import lxml.html as html
import os
import glob
import re
import sys
from lxml import etree
from html.parser import HTMLParser


HTML_DIR = 'original html'
DUMP_DIR = 'markdown'


class GetElement():

    def __init__(self, text, css):
        self.text = text
        self.css = css

    def __enter__(self):
        blog_page = html.fromstring(self.text)
        result = blog_page.cssselect(self.css)
        element = result[0].text if result else None
        return element

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class Convert():
    def __init__(self):
        self.html_list = None
    
    def get_html_list(self):
        self.html_list = glob.glob(os.path.join(HTML_DIR, '*.html'))

    @staticmethod
    def get_title(text):
        with GetElement(text, '.title-article strong') as title:
            return title

    @staticmethod
    def get_body(text):
        blog_page = html.fromstring(text)
        result = blog_page.cssselect('#blogContent')
        if result:
            blogcontent_div = blog_page.cssselect('#blogContent')[0]
            h = HTMLParser()
            body_text = h.unescape(etree.tostring(blogcontent_div).decode('utf-8'))
            return body_text
        else:
            return None

    @staticmethod
    def get_tag(text):
        with GetElement(text, '.title-article .group a') as tag:
            return tag
    
    @staticmethod
    def get_timestamp(text):
        with GetElement(text, '.timestamp') as timestamp:
            return timestamp

    def write2md(self):
        count = 0
        for file in self.html_list:
            with open(file, 'rt', encoding='utf-8') as f:
                text = f.read()
                title = self.get_title(text)
                tag = self.get_tag(text)
                timestamp = self.get_timestamp(text)
                body = self.get_body(text)
                if all((text, title, timestamp, body)):
                    lines = [title, '\n', timestamp, '\n', tag, '\n', body]
                    if sys.stdout.encoding == 'UTF-8':
                        print(title + " finished, {0} converted".format(count))
                    else:
                        print(count)
                    count += 1
                    title = re.sub(r'[<>"*\\/|?]', '', title)
                    title = re.sub(':', '-', title)
                    filename = os.path.basename(file).split('.')[0] + ".{0}.md".format(title)  # num.title
                    with open(os.path.join(DUMP_DIR, filename), 'wt', encoding='utf-8') as md:
                        md.writelines(lines)


if __name__ == '__main__':
    c = Convert()
    c.get_html_list()
    c.write2md()
