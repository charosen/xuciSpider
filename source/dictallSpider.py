import requests, re

# 使用requests爬取词都网站，使用re解析出英文翻译、补充资料, 并存储成文本
# 注意定义一个元组的方法
url_base = ('http://www.dictall.com/dictall/result.jsp?keyword=', )
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}


# 定义url_manager函数，将叙词拼接到url中，返回一个url列表供请求使用
def url_manager(word, *urls):
    # 参数检验：
    if urls is ():
        urls = url_base
    if not isinstance(word, str):
        raise TypeError('word param is not str.')

    return [ url + word for url in urls]


# 定义html_downloader函数，获取一个网站的源代码,返回英文译文、补充内容所处的部分源代码
def html_downloader(url):
    # 参数检验：
    if not isinstance(url, str):
        raise TypeError('URL param is not str.')

    # 获取网页源代码
    html = requests.get(url, headers=headers)
    # 截取英文译文同补充内容的部分源代码
    html= html.text.replace('&nbsp;', ' ')
    english_trans = re.search('"catelist">(.*)</div>(.*?)<div\sid="bk"', html, re.S).group(1)
    completary_cont = re.search('"bk">(.*)</div>(.*?)<div\sid="bknotice"', html, re.S).group(1)

    # test:
    # print('>> html =', repr(html),
    #       '>> english_translation =', english_trans,
    #       '>> completary_cont =', completary_cont,
    #       sep='\n')
    return english_trans, completary_cont


# 定义html_parser函数，将英语译文、补充内容等信息提取出来
def html_parser(html):
    # 参数检验
    if not isinstance(html, tuple):
        raise TypeError('html param is not tuple.')

    info = {}
    trans_list = re.findall('<span>\d\)(.*?)</span>', html[0], re.S)
    completary_cont = re.sub('<br>', '\n', html[1], re.S, re.I)
    info['translation'] = clean_trans(trans_list)
    info['completary'] = extract_content(completary_cont)

    # test:
    # print(">> completary type:", type(info['completary']), 'completary =', info['completary'])
    return info


# 定义clean_trans函数， 将重复的英文译文清洗掉
def clean_trans(dirty_trans):
    # 参数检验
    if dirty_trans is None:
        raise ValueError("translation regex dosen't work.")

    clean_list = []
    for each in dirty_trans:
        each = each.strip().capitalize()
        # print('>> each =', repr(each))
        if each not in clean_list:
            clean_list.append(each)
    # test:
    # print('>> clean_list =', repr(clean_list))
    return tuple(clean_list)


# 定义extract_content函数，将补充内容文本提取出来
def extract_content(content):
    # 去除html源码中的table标签
    content = re.sub('<table[^>]*?>.*?</table>', '', content, re.S)
    # 去除html源码中的span标签
    content = re.sub('<span[^>]*?>.*?</span>', '', content, re.S)
    # 去除html源码中的剩余标签
    content = re.sub('<[^>]*>', '', content, re.S)
    # content = re.sub('<(?!br).*?>', '', content, re.S)
    # content = re.sub('<.*?>', '', content, re.S)
    # content = content.replace('&nbsp;', ' ')
    return content

# test:
if __name__ == '__main__':
    url_list = url_manager('cpu')
    print('>> url_list =', url_list)

    content = html_downloader(url_list[0])
    dict = html_parser(content)
    print('>> dict =', dict)
    print(">> dict['translation'] =", dict['translation'])
    print(">> dict['completary'] =", dict['completary'])
