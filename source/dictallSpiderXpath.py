#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
定义一个名为DictallSpider的爬虫类，用以爬取叙词的英文翻译和补充内容
'''


import requests, re
from lxml import etree


class DictallSpider(object):
    '''
    dictall网站爬虫类
    '''

    def __init__(self, keyword):
        '''
        constructor for class dictallSpider
        '''
        self.headers = {'User-Agent': ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) '
                                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                                       'Chrome/64.0.3282.186 Safari/537.36')}
        self.translation = list()
        self.example = list()
        self.completary = None
        self.logPath = '/Users/mac/projects/word_spider_test/'
        self.baseUrl = 'http://www.dictall.com/dictall/result.jsp?keyword='
        self.keyword = keyword
        self.url = self.baseUrl + self.keyword
        self.htmlDownloader()


    def htmlDownloader(self):
        '''
        爬取指定叙词的dictall页面
        '''
        try:
            print('>> Getting html content...')
            html = requests.get(self.url, headers=self.headers)
            print('>> Getting html done.')
        except requests.exceptions.RequestException as e:
            # http请求异常处理，并在日志中记录没有请求到dictall页面的叙词
            print('>> Exceptions occured:', type(e), e)
            self.textLog('log_dictall.txt')
        else:
            html.encoding = 'utf-8'
            self.htmlParser(html.text)


    def htmlParser(self, html):
        '''
        解析爬取到的dictall页面，将dictall页面中id为catelist框和bk框
        分别提取出来，以备作进一步解析
        '''
        print('>> Parsing html content...')

        # 去除html源代码中的<br>标签
        html = re.sub('<br>', '\n', html, re.S, re.I)
        htmlCleaned = re.sub('<sup>.*?</sup>', '', html, re.S, re.I)
        # 使用lxml提取页面内容
        selector = etree.HTML(htmlCleaned)
        catelist = selector.xpath('//div[@id="catelist"]')
        bk = selector.xpath('//div[@id="bk"]')
        # http请求到dictall页面中不含叙词的相关内容，并在日志中记录该叙词
        if len(catelist) <= 0 and len(bk) <= 0:
            self.textLog('log_dictall.txt')
        # 对catelist框和bk框作进一步解析
        elif len(catelist) > 0 and len(bk) <= 0:
            assert len(catelist) <= 1, 'html code has multiple catelist div labels.'
            self.catelistParser(catelist)
            self.textLog('log_dictall_com.txt')
        elif len(catelist) <= 0 and len(bk) > 0:
            assert len(bk) <= 1, 'html code has multiple bk div labels.'
            self.bkParser(bk)
            self.textLog('log_dictall_trans.txt')
        else:
            assert len(catelist) <= 1, 'html code has multiple catelist div labels.'
            assert len(bk) <= 1, 'html code has multiple bk div labels.'
            self.catelistParser(catelist)
            self.bkParser(bk)


        print('>> Parsing html done.')
        # test:
        # print('>> html =', repr(html),
        #       '>> catelist =', etree.tostring(catelist[0],
        #                                       pretty_print=True,
        #                                       encoding='utf-8').decode('utf-8'),
        #       '>> bk =', etree.tostring(bk[0],
        #                                 encoding='utf-8').decode('utf-8'),
        #       sep='\n')


    def catelistParser(self, catelist):
        '''
        解析catelist框中叙词的英文翻译和实例
        '''
        print('>> Parsing catelist content...')

        transList = catelist[0].xpath('//div[@class="en"]/span[1]/text()')
        exampleList = catelist[0].xpath('//div[@class="cn"]/text()')
        # print('>> transList =', type(transList), transList)
        # print('>> exampleList =', type(exampleList), exampleList)

        self.cleanList(transList, exampleList)

        print('>> Parsing catelist done.')

    def bkParser(self, bk):
        '''
        解析bk框中叙词的补充内容
        '''
        print('>> Parsing bk content...')


        completaryCont = bk[0].xpath('//div[@id="bkCon"]')
        self.completary = etree.tostring(completaryCont[0],
                                         encoding='utf-8',
                                         method='text').decode('utf-8')



        print('>> Parsing bk done.')


    def cleanList(self, dirtyTrans, dirtyExams):
        '''
        定义cleanTrans函数， 将重复的英文译文、实例清洗掉
        '''
        cleanTrans = list()
        cleanExams = list()
        # if len(dirtyTrans) == len(dirtyExams):
        for i in range(len(dirtyTrans)):
            # print('>>>>trans, exam, keyword:', dirtyTrans[i],
            #                                    dirtyExams[i],
            #                                    self.keyword)
            if dirtyExams[i] == self.keyword:
                # print('>> equal.')
                tranCleaned = re.sub('\d\)', '', dirtyTrans[i])
                tranNormal = tranCleaned.strip().capitalize()
                # print('>> each =', repr(each))
                if tranNormal not in cleanTrans:
                    cleanTrans.append(tranNormal)
            else:
                # print('>> not equal.')
                if dirtyExams[i] not in cleanExams:
                    cleanExams.append(dirtyExams[i])

        self.translation = cleanTrans
        self.example = cleanExams
        # test:
        # print('>> cleanTrans =', repr(cleanTrans))
        # print('>> cleanExams =', repr(cleanExams))
        # else:
        #     self.textLog('log_dictall_trans.txt')


    def textLog(self, filename):
        '''
        为没有找到英文翻译、实例、补充内容的叙词做日志登记
        '''
        print(f'>>>>>>> No Result for {self.keyword} in website ditcall.')
        with open(self.logPath+filename, 'a') as file:
            file.write(self.keyword + '\n')


# 定义extract_content函数，将补充内容文本提取出来
# def extract_content(content):
#     # 去除html源码中的table标签
#     content = re.sub('<table[^>]*?>.*?</table>', '', content, re.S)
#     # 去除html源码中的span标签
#     content = re.sub('<span[^>]*?>.*?</span>', '', content, re.S)
#     # 去除html源码中的剩余标签
#     content = re.sub('<[^>]*>', '', content, re.S)
#     # content = re.sub('<(?!br).*?>', '', content, re.S)
#     # content = re.sub('<.*?>', '', content, re.S)
#     # content = content.replace('&nbsp;', ' ')
#     return content

# test:
if __name__ == '__main__':
    spider = DictallSpider('核磁共振波谱法')
    print('keyword =', spider.keyword)
    print('translation =', spider.translation)
    print('example =', spider.example)
    print('completary =', spider.completary)
