#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
定义一个名为BaikeSpider的爬虫类，用以爬取叙词的百度百科定义
'''


import requests
from lxml import etree


class BaikeSpider(object):
    '''
    百度百科爬虫类
    '''

    def __init__(self, keyword):
        '''
        constructor for class BaikeSpider.
        '''
        self.headers = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) '
                                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                                       'Chrome/64.0.3282.186 Safari/537.36')}
        self.definition = None
        self.logPath = '/Users/mac/projects/word_spider_test/'
        self.baseUrl = 'https://baike.baidu.com/search/word?word='
        self.keyword = keyword
        self.url = self.baseUrl + self.keyword
        self.htmlDownloader()


    def htmlDownloader(self):
        '''
        爬取指定叙词的百度百科页面
        '''
        try:
            print('>> Getting html content...')
            html = requests.get(self.url, headers=self.headers)
            print('>> Getting html done.')
        except requests.exceptions.RequestException as e:
            # http请求异常处理，并在日志中记录没有请求到百科页面的叙词
            print('>> Exceptions occured:', type(e), e)
            self.textLog('log_baike.txt')
        else:
            html.encoding = 'utf-8'
            self.htmlParser(html.text)


    def htmlParser(self, html):
        '''
        解析指定叙词的百度百科页面
        '''
        print('>> Parsing html content...')

        definition = etree.HTML(html).xpath('//div[@class="lemma-summary"]')
        if len(definition):
            self.definition = etree.tostring(definition[0],
                                             encoding='utf-8',
                                             method='text').decode('utf-8').strip()
        else:
            # 在叙词的百科页面中，没有找到关于叙词的定义，此时日志记录该叙词
            self.textLog('log_definition.txt')

        print('>> Parsing html done.')


    def textLog(self, filename):
        '''
        为没有找到定义的叙词做日志登记
        '''
        print(f'>>>>>>> No Result for {self.keyword} in website baidubaike.')
        with open(self.logPath+filename, 'a') as file:
            file.write(self.keyword + '\n')



if __name__ == '__main__':
        spider = BaikeSpider('绝缘材料')
        print(spider.keyword, spider.definition)
