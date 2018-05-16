#coding=utf-8;


import tornado.ioloop
import tornado.httpserver
import tornado.web

import os


import bs4

from bs4 import BeautifulSoup

import urllib.request
import requests
import re
import json
baseUrl = "https://www.dushu.com";


MeiWenURL = "http://www.85nian.net/category/renwu";

OneDayOneBookURL = "http://book.ifeng.com/listpage/65986/1/list.shtml";



# 设置配置
settings = dict(
    template_path = os.path.join(os.path.dirname(__file__),"template"),
    static_path = os.path.join(os.path.dirname(__file__),"static")
)

# 推荐书籍的数据
recommond_book_list = [];

# 美文的数据
meiwen_info_list = [];

# 每日一文的list
one_day_one_book_list = [];

# 书评的list
book_comment_list = [];

# 人生哲理list
zheli_list = [];

# 爱情感悟list

ganwu_list = [];


# 渲染首页的模板
class HomeHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        global recommond_book_list;
        global meiwen_info_list;
        global one_day_one_book_list;
        global book_comment_list;
        global zheli_list;
        global ganwu_list;


        self.render("home.html",recommond_books=recommond_book_list,meiwen_infos = meiwen_info_list,oneday_lists = one_day_one_book_list,comment_list = book_comment_list,zheli_list = zheli_list,ganwu_list = ganwu_list);

# 详情页面的模板
class BookDetailInfoHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        path = self.get_argument('path',default=None);
        img_src = self.get_argument('img_src',default=None);
        rep = getHtml(path)
        detail_info = getBookInfo(rep);
        self.render('detail.html',book_detail_info = detail_info,img_src = img_src);

# 美文的详情页面
class MeiWenDetailHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        # 获取具体的href
        detailURL = self.get_argument('path',default=None);
        rep = getHtml(detailURL);
        res_dict = getArtDetail(rep);
        self.render('meidetail.html',res_dict = res_dict);





# 在线美文节后 根据前天请求的类型 数据返回
class MeiWenHandler(tornado.web.RequestHandler):

    def post(self, *args, **kwargs):
        cate = self.get_argument('cate', default=None);
        # 根据前端的请求 爬取对应的网页数据 进行返回
        reqURL = "http://www.85nian.net/category/"+cate;
        rep = getHtml(reqURL);
        res_list = getArticleList(rep);
        dict = {
            'res':res_list
        };
        # 返回给前端的数据
        self.write(dict);
# 每日详情
class OneDayDetailHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        href = self.get_argument('path',default=None);
        title = self.get_argument('title',default=None);

        rep = getHtml(href);
        res_list = getOneDayBookInfo(rep);
        self.render('oneday.html',res_list = res_list,title= title);


# 每日书评页面
class DayCommentHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        title = self.get_argument('title',default=None);
        aid = self.get_argument('path',default=None);
        # 根据对应的aid 找到对应的contents
        global  book_comment_list;
        targetDic = {};
        for item in book_comment_list:
            if item["aid"] == aid:
                targetDic = item;


        # 渲染到页面去
        self.render("shuping.html",res_dict = targetDic);

# 人生哲理详情
class ZheLiDetailHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        title = self.get_argument('title',default=None);
        aid = self.get_argument('path',default=None);
        # 根据对应的aid 找到对应的contents
        global  zheli_list;
        targetDic = {};
        for item in zheli_list:
            if item["aid"] == aid:
                targetDic = item;


        # 渲染到页面去
        self.render("zheli.html",res_dict = targetDic);


class GanWuDetailHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        title = self.get_argument('title',default=None);
        aid = self.get_argument('path',default=None);
        # 根据对应的aid 找到对应的contents
        global  ganwu_list;
        targetDic = {};
        for item in ganwu_list:
            if item["aid"] == aid:
                targetDic = item;


        # 渲染到页面去
        self.render("ganwu.html",res_dict = targetDic);


# app 的编写
app = tornado.web.Application(handlers=[(r"/index",HomeHandler),
                                        (r"/detail",BookDetailInfoHandler),
                                        (r"/meiwen",MeiWenHandler),
                                        (r"/meidetail",MeiWenDetailHandler),
                                        (r"/oneday",OneDayDetailHandler),
                                        (r"/shuping",DayCommentHandler),
                                        (r"/zheli",ZheLiDetailHandler),
                                        (r"/ganwu",GanWuDetailHandler)

                                        ], **settings);

# 获取文章详情
def getArtDetail(rep):
    soup = BeautifulSoup(rep, 'lxml');
    # 文章标题
    s_title = soup.find_all('h1',{'class':{'entry-title'}})[0];
    # 找到作者
    s_author = soup.find_all('span',{'class':{'author'}})[0];
    # 时间 bwn-date
    s_content_list = [];
    s_date = soup.find_all('span',{'class':{'bwn-date'}})[0];
    # 文章
    s_content = soup.find_all('p');
    sep_idx = 0;
    for item in s_content:
        if item.text != '':
            s_content_list.append(item.text)
            if '电子邮件地址不会被公开' in item.text:
                sep_idx = len(s_content_list);


    # 处理一下 截取文章部分

    dict = {
        'title':s_title.text,
        'author':s_author.text,
        'date':s_date.text,
        'content':s_content_list[0:sep_idx - 1]
    }


    return dict;



# 访问网页 获取响应
def getHtml(url):
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:59.0) Gecko/20100101 Firefox/59.0"
    # 构建请求
    req = urllib.request.Request(url);
    # 添加请求头信息
    req.add_header('User-Agent',user_agent);
    # 打开请求
    res = urllib.request.urlopen(req);

    html = res.read();

    return html;



# 获取ifeghuang 一日一书的信息
def getOneDayOneBook(rep):
    soup = BeautifulSoup(rep, 'lxml');
    # 根据href 正则表达式筛选
    s_title_list = soup.find_all(name='a', attrs={"href": re.compile(r'^http://book.ifeng.com/a/')});

    temp_res_list = [];

    res_list = [];
    href_list = [];
    for item  in s_title_list:
        if item.text != None and item.text != u'详细':
            temp_res_list.append(item);

    for i  in range(0,14):
        if i % 2 == 0:
            res_list.append(temp_res_list[i].text);
            href_list.append(temp_res_list[i]['href']);

    result_list = [];
    for i in range(0,6):
        dict = {
            "href":href_list[i],
            "title":res_list[i]
        }
        result_list.append(dict);

    return result_list;

# 爬取一日一书的详情页面  http://book.ifeng.com/a/20180508/108748_0.shtml
def getOneDayBookInfo(rep):
    soup = BeautifulSoup(rep, 'lxml');
    # soup.find_all("div", style="display: flex")
    # 通过style 选择器选择出来水元素
    s_span_list = soup.find_all("span",style="font-size: 14px;");
    content_list = [];
    for item in s_span_list:
        content_list.append(item.text);

    return content_list;


# 读取本地json 文件 书评
def getLocalCommentBookInfo(path):
    file = open(path, "rb")
    fileJson = json.load(file)
    res_list = fileJson['res'];

    return res_list;





# 获取首页的推荐图书的详情字典
def getRecommondBook(rep):

    soup = BeautifulSoup(rep, 'lxml');

    s_bookname_list = soup.find_all('div',{'class':{'bookname'}});

    # 所有的书名放在这里
    s_a_list = soup.find_all('a');
    # 书名数组
    book_name_list = [];
    # 书的详细介绍list
    book_detail_list = [];



    for item in s_a_list:
        if item.text != '' and '/book' in item['href']:

            book_name_list.append(item.text);


    # '更多>'
    start_idx = book_name_list.index(u'更多>') + 1;
    end_idx = start_idx + 10;
    # 截取数组
    book_name_list = book_name_list[start_idx:end_idx];

    # 根据书名找链接
    face_img_list = [];
    # 书的详情连接
    book_info_list = [];

    # 盛放的结果的array

    res_list = [];
    for i in range(0,10):
        # 先找书名
        book_filter = book_name_list[i];
        if '…' in book_filter:
            book_filter = book_filter.strip('…');

        s_face_img_url = soup.find_all(attrs={'alt': book_filter})[0];

        face_img_list.append(s_face_img_url["data-original"]);
        face_img_list = face_img_list[0:10];

        # 书的详情处理
        s_book_href = soup.find_all('div',{'class':{'border books'}});

        for item in s_a_list:
            if book_name_list[i] == item.text:
                book_info_list.append(baseUrl + item['href']);
        # 作者
        src_idx = i + 1;
        # 拼接数据
        res_dic = {
            "book_name":book_name_list[i],
            "book_face_img_url":'../static/resource/home_'+ str(src_idx) + '.jpg',
            "book_info_url":book_info_list[i]
        };
        res_list.append(res_dic);


    return res_list;
    # print(res_list);


# 根据书的详情页面链接 爬取对应的信息
def getBookInfo(rep):
    soup = BeautifulSoup(rep,'lxml');
    # 获取信息
    s_title = soup.find_all('div',{'class':{'book-title'}})[0];
    # 书名
    book_title = s_title.text;

    # 书的封面
    s_pic = soup.find_all(attrs={'alt':book_title})[0];
    book_face_url = s_pic["src"];

    # 书的价格
    s_price= soup.find_all('span',{'class':{'num'}})[0];
    book_price = s_price.text;

    # 书的作者
    s_author = soup.find_all(attrs={'title':'更多同作者相关图书'})[0];
    book_author = s_author.text;

    # 书的出版社
    s_public =  soup.find_all(attrs={'title':'点击查看更多该出版社图书'})[0];
    book_public = s_public.text;

    # 书的类别

    # 输的出版时间
    s_pub_time = soup.find_all('td',{'class':{'rt'}})[1];
    book_pub_time = s_pub_time.text;

    # 内容简介
    s_info = soup.find_all('div',{'class':{'text txtsummary'}})[0];
    book_info = s_info.text;

    # 作者简介
    s_author_info =  soup.find_all('div',{'class':{'text txtsummary'}})[1];
    book_author_info = s_author_info.text;

    # 图书目录
    s_index_info =  soup.find_all('div',{'class':{'text txtsummary'}})[2];
    book_index_info = s_index_info.text;


    # 将信息装入字典 返回
    book_detail_info_dic = {
        'book_title':book_title,
        'book_face_url':book_face_url,
        'book_price':book_price,
        'book_author':book_author,
        'book_public':book_public,
        's_pub_time':book_pub_time,
        'book_info':book_info,
        'book_author_info':book_author_info,
        'book_index_info':book_index_info
    }

    return book_detail_info_dic;


# 获取美文的数据

# 获取链接
def getArticleList(rep):
    soup = BeautifulSoup(rep, 'lxml');
    # 文章标题的list
    article_title_list = []
    # 文章详情链接list
    article_href_list = [];
    # 封面图片
    article_face_img = [];

    # 获取标题
    s_title = soup.find_all(attrs={'rel':'bookmark'});

    for item in s_title:
        # 过滤一下子
        if item.text != '':
            article_title_list.append(item.text);
            article_href_list.append(item["href"]);

    # 获取封面的照片
    s_face_img = soup.find_all('img', {'class': 'alignleft'});
    for item in s_face_img:
        article_face_img.append(item["src"]);


    # 返回的数据
    cate_info_list = [];
    for i in range(0,8):
        dict = {
            "title":article_title_list[i],
            "href":article_href_list[i],
            "faceImg":article_face_img[i]
        }
        cate_info_list.append(dict);

    return cate_info_list;


# main 函数
if __name__ == '__main__':

    comment_json_path =  os.path.dirname(__file__) + '/shuping.json';
    zheli_json_path = os.path.dirname(__file__) + '/zheli.json';
    ganwu_json_path = os.path.dirname(__file__) + '/ganwu.json';
    book_comment_list = getLocalCommentBookInfo(comment_json_path);
    zheli_list = getLocalCommentBookInfo(zheli_json_path);
    ganwu_list = getLocalCommentBookInfo(ganwu_json_path);



    # 获取推荐书籍的数据
    rep = getHtml(baseUrl);
    rep2 = getHtml(MeiWenURL);
    rep3 = getHtml(OneDayOneBookURL);
    recommond_book_list = getRecommondBook(rep);
    meiwen_info_list = getArticleList(rep2);
    one_day_one_book_list = getOneDayOneBook(rep3)
    http_server = tornado.httpserver.HTTPServer(app);
    http_server.listen(8181);
    tornado.ioloop.IOLoop.instance().start();



