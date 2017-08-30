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
        
    def __del__(self):
        self.connection.close()
    
    def spider(self, url):
            html1 = requests.get(url)
            selector1 = etree.HTML(html1.text)
            timestamp = self.convertToUtf8(selector1.xpath('//span[@id="navtimeSource"]/text()')[0])[:-7]
            releaseFrom = self.convertToUtf8(selector1.xpath('//span[@data-sudaclick="media_name"]/a/text()')[0])
            keyword = self.convertToUtf8(' '.join(selector1.xpath('//div[@class="article-keywords"]/a/text()')))
            # Exclude certain elements from selection in XPath
            content = self.convertToUtf8((''.join(selector1.xpath('//div[@class="article article_16"]/*[not(div[@class="artical-player-wrap"])]/text()')))).replace('\n', '').replace('\t', '')
            print keyword
            print content
            self.table.insert({"timestamp":timestamp, "releaseFrom":releaseFrom, "keyword":keyword, "content":content})
            
    def convertToUtf8(self, text):
        return text.encode('unicode_escape').decode('string_escape').decode("utf8", 'ignore').encode("utf8")
    
if __name__ == '__main__':
    mySpider = SinaNewsSpider()
    mySpider.spider('http://news.sina.com.cn/s/wh/2017-06-02/doc-ifyfuzny2068753.shtml')


    
    

