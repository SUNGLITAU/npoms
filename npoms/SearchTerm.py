import sys
from fake_useragent import UserAgent
# 增强代码的重复利用性
# 搜索类


class SearchTerm:
    def __init__(self, key_words):
        self.keywords = key_words
        self.ua = UserAgent().random
        # 读取cookie
        with open('./data/setup/zhihu_cookie.txt') as fp:
            cookie = fp.read()
        self.cookie = cookie
        self.header = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2',
            'User-Agent': str(self.ua),
            'cookie': str(cookie),
            'Referer': 'https://www.zhihu.com/search?type=topic&q=%E7%9F%A5%E4%B9%8E',
            'x-zse-83': '3_2.0',
            'x-zse-86': '1.0_a0O8NvL0o72xFwFqT9xySAX02LtY6720f8YygbuqrMFX',
            'x-app-za': 'OS=Web',

        }
        self.domain = 'https://www.zhihu.com'
        # 初始化，在后面的过程中被替换
        self.topic_id = -1


if __name__ == '__main__':
    keywords = SearchTerm('武汉')
    print(keywords.keywords)
    # print(keywords.topic_id)
    # print(keywords.cookie)
    print(keywords.header['User-Agent'])
    print(keywords.header['cookie'])
    # print(keywords.ua)

