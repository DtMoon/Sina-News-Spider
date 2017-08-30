# -*- coding:utf-8 -*-

import datetime
from multiprocessing.dummy import Pool as ThreadPool

from lxml import etree
import pymongo
import requests

class SinaNewsSpider():
   
    def __init__(self):
        self.connection = pymongo.MongoClient('localhost:27017')
        self.db = self.connection.News
        self.table = self.db.SinaNews
        self.success = 0
        self.failure = 0
        
    def __del__(self):
        self.connection.close()
    
    def spider(self, url):
        try:
            html = requests.get(url)
            selector = etree.HTML(html.text)
            results = selector.xpath('//ul[@class="list_009"]/li')
            for each in results:
                '''
                encode(encoding)：将unicode转换为str，并使用encoding编码
                decode(encoding)：将str转换为unicode，其中str以encoding编码
                使用isinstance(string, str)来判断string是不是str格式的
                使用isinstance(string, unicode)来判断string是不是unicode格式的         
                很重要的一点是：要查看源网页的编码方式，在<head>的<meta charset=编码方式>中查看
                下面的title中的内容为u'\xc3\xc0\xba\xab\xd4'，这种样子的要像下面这样处理，才能转成utf8编码
                下面的title所在的网页是用gb2312编码的，所以要先用gb2312解码，在用utf8编码
                '''
                title = each.xpath('a/text()')[0].encode('unicode_escape').decode('string_escape').decode('gb2312').encode('utf8')
                link = each.xpath('a/@href')[0].encode('utf8')
                html1 = requests.get(link)
                selector1 = etree.HTML(html1.text)
                '''
                下面的result_1所在的网页使用utf-8编码的，所以只需要执行.encode('unicode_escape').decode('string_escape')即可
                由于.encode('unicode_escape').decode('string_escape')之后，字符串中还可能有无效的utf8字符，
                所以可以先.decode("utf8", 'ignore')将无效的utf8字符忽略，然后再.encode("utf8")变成有效的utf8字符串
                比如'\xe7\xad\x899\xe5\x9c\xb0\xe3\x80\x82\xa0\xef\xbc\x88\xe5\xbc\xa0\xe6\x96\x87\xe5\xa8\x87'中就有在utf8编码下是乱码的内容
                '''
                timestamp = self.convertToUtf8(selector1.xpath('//span[@id="navtimeSource"]/text()')[0])[:-7]
                releaseFrom = self.convertToUtf8(selector1.xpath('//span[@data-sudaclick="media_name"]/a/text()')[0])
                keyword = self.convertToUtf8(' '.join(selector1.xpath('//div[@class="article-keywords"]/a/text()')))
                # Exclude certain elements from selection in XPath
                content = self.convertToUtf8((''.join(selector1.xpath('//div[@class="article article_16"]/*[not(div[@class="artical-player-wrap"])]/text()')))).replace('\n', '').replace('\t', '')
                # MongoDB: strings in documents must be valid UTF-8
                self.table.insert({"title":title, "link":link, "timestamp":timestamp, "releaseFrom":releaseFrom, "keyword":keyword, "content":content})
                self.success += 1
        except Exception, e:
            self.failure += 1
            print e
            
    def convertToUtf8(self, text):
        return text.encode('unicode_escape').decode('string_escape').decode("utf8", 'ignore').encode("utf8")
    
if __name__ == '__main__':
    mySpider = SinaNewsSpider()
    urls = []
    baseURLs = ['http://roll.news.sina.com.cn/news/gnxw/gdxw1/%s_%s.shtml',
                'http://roll.news.sina.com.cn/news/shxw/shwx/%s_%s.shtml',
                'http://roll.news.sina.com.cn/news/gjxw/gjmtjj/%s_%s.shtml']
    startDate = datetime.datetime(2017, 6, 1)
    for day in range(56):
        date = startDate + datetime.timedelta(days=day)
        for i in range(1, 6):
            urls.extend([url % (datetime.datetime.strftime(date, "%Y-%m-%d"), i) for url in baseURLs])

    # multi-threaded web crawler
    pool = ThreadPool(4)
    pool.map(mySpider.spider, urls)

    print mySpider.success
    print mySpider.failure

    
    

