import requests
import re
import json
import time
import random
import pymysql
import sys
from lxml import etree
from bs4 import BeautifulSoup
from SearchTerm import SearchTerm

from warnings import filterwarnings
# 针对 DROP TABLE IF EXISIT 的处理办法
filterwarnings("error", category=pymysql.Warning)


# 所有的都是功能模块
def get_json_html(url, header):
    """
    解析json数据
    :param url: api
    :param header:
    :return: html
    """
    response = requests.get(url, headers=header)
    response.encoding = 'utf-8'
    html = response.json()
    return html


def get_topic_id(key_words, header):
    """
    获取ID，找到话题对应的ID
    :param key_words:
    :param header:
    :return: ID
    """
    base_url = 'https://www.zhihu.com/api/v4/search_v3?t=topic' \
               '&q={}&correction=1&offset=0&limit=0&lc_idx=26&show_all_topics=1' \
               '&search_hash_id=a463f45555bd5be912ee6f0fa8b246f2'.format(key_words)

    html = get_json_html(base_url, header)
    print(html)
    topic_id = 0
    try:
        topic_id = html['data'][0]['object']['id']
        message = 'ID获取完毕，{}的ID或者最接近该话题的ID是：{}'.format(key_words, topic_id)
    except Exception:
        # TODO 这句话实际上没有用。话题非常少的时候会触发这个
        message = '您输入的关键词话题过少，请检查关键字'
    if topic_id != 0:
        return topic_id, message
    else:
        return sys.exit()


# 处理在数据获取的过程中时间格式的函数
def check_time(num):
    """
    处理时间戳
    :param num:
    :return: 2019/6/3  22:51:11
    """
    time_array = time.localtime(num)
    other_style_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
    return other_style_time


def get_urls_data(url, header):
    """
    获取api的数据
    :param url: 组装完成的api
    :param header:
    :return: 主要是判断是否到达尾页
    """
    tmp_data = []
    api_url = url
    html = get_json_html(api_url, header)

    # flag = html['paging']['is_end']
    flag2 = len(html['data'])

    for i in range(flag2):
        target = html['data'][i]['target']
        list_type = target['type']
        # headline/title 需要根据类型进行判定
        if list_type == 'answer':
            list_title = target['question']['title']
            list_time = target['created_time']
        elif list_type == 'article':
            list_title = target['title']
            list_time = target['updated']
        else:
            # 必定异常，数据没有意义，跳过此次循环
            print("本轮中弹出了一个错误数据 》》》》》》》》》》》》》》》》》》》》》")
            continue
        list_time = check_time(list_time)
        list_name = target['author']['name']
        list_ups = target['voteup_count']
        # print(type(target['content']))
        content_text = target['content']
        soup = BeautifulSoup(content_text, 'lxml')
        list_content = soup.get_text()
        tmp_data.append({"Type": list_type, "UPdate": list_time, "Title": list_title,
                             "AuthorName": list_name, "VoteUP": list_ups,
                             "Content": list_content})
    # for i in RESULTS_DATA:
    #     print(i)
    # print(" 此时这个results_data会被清空， 这里建议储存或者使用别的写法")
    if flag2 < 10:
        return tmp_data, 1
    else:
        return tmp_data, 0


def spider(key_words, topic_id, header):
    """
    统合前面所有的函数，保存到MySQL中
    :param key_words:
    :param topic_id:
    :param header:
    :return: null
    """
    start = time.time()  # 计时器
    off_set = 0
    error_count = 0
    turn = 1
    tmp_data = []

    # 操作数据库
    coon = pymysql.connect(host='localhost',
                           port=3306,
                           user='root',
                           password='jjkl',
                           db='db4zhihuspider',
                           charset='utf8')
    # 创建游标
    my_cursor = coon.cursor()
    # 组装表名
    print("==========  数据库完成链接， 游标已经生成  =========")
    table_name = 'TOPIC' + topic_id
    # 创建表
    try:
        my_cursor.execute('drop table if exists {};'.format(table_name))
        print("已经存在可能过时的数据，开始重建")
    except pymysql.Warning:
        print("您输入的话题关键词没有相关表，立即创建")
    finally:
        sql_x = '''CREATE TABLE IF NOT EXISTS {} (
                TTYPE VARCHAR(15) NOT NULL, 
                UPTIME DATETIME NOT NULL,
                TITLE VARCHAR(60) NOT NULL, 
                AUTHOR VARCHAR(24) NOT NULL, 
                VOTEUP MEDIUMINT(255) NOT NULL, 
                CONTENT MEDIUMTEXT,
                PRIMARY KEY(UPTIME));
                '''.format(table_name)
    my_cursor.execute(sql_x)
    # 准备查询语句, REULTS_DATA现在有没数据，但是这是在调用的时候才会准备，if时有就有参数了
    sql = 'INSERT INTO {}(TTYPE, UPTIME, TITLE, AUTHOR, VOTEUP, CONTENT) VALUES (%s, %s, %s, %s, %s, %s);'.format(table_name)

    while True:
        # test(url)
        url = 'https://www.zhihu.com/api/v4/topics/{}/feeds/essence?include=' \
              'data%5B%3F%28target.type%3Dtopic_sticky_module%29%5D.target.data%5B%3F%28target.type' \
              '%3Danswer%29%5D.target.content%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_' \
              'thanked%2Cis_nothelp%3Bdata%5B%3F%28target.type%3Dtopic_sticky_module%29%5D.target.data' \
              '%5B%3F%28target.type%3Danswer%29%5D.target.is_normal%2Ccomment_count%2Cvoteup_count%2Ccont' \
              'ent%2Crelevant_info%2Cexcerpt.author.badge%5B%3F%28type%3Dbest_answerer%29%5D.topics%3Bdata%5' \
              'B%3F%28target.type%3Dtopic_sticky_module%29%5D.target.data%5B%3F%28target.type%3Darticle%2' \
              '9%5D.target.content%2Cvoteup_count%2Ccomment_count%2Cvoting%2Cauthor.badge%5B%3F%28type%3D' \
              'best_answerer%29%5D.topics%3Bdata%5B%3F%28target.type%3Dtopic_sticky_module%29%5D.target.dat' \
              'a%5B%3F%28target.type%3Dpeople%29%5D.target.answer_count%2Carticles_count%2Cgender%2Cfollower_' \
              'count%2Cis_followed%2Cis_following%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics%3Bdata%5B' \
              '%3F%28target.type%3Danswer%29%5D.target.annotation_detail%2Ccontent%2Chermes_label%2Cis_labe' \
              'led%2Crelationship.is_authorized%2Cis_author%2Cvoting%2Cis_thanked%2Cis_nothelp%3Bdata%5B' \
              '%3F%28target.type%3Danswer%29%5D.target.author.badge%5B%3F%28type%3Dbest_answerer%29%5D.' \
              'topics%3Bdata%5B%3F%28target.type%3Darticle%29%5D.target.annotation_detail%2Ccontent%2C' \
              'hermes_label%2Cis_labeled%2Cauthor.badge%5B%3F%28type%3Dbest_answerer%29%5D.topics%3Bda' \
              'ta%5B%3F%28target.type%3Dquestion%29%5D.target.annotation_detail%2Ccomment_count%3B&lim' \
              'it=10&offset={}'.format(topic_id, off_set)
        tmp_data, flag_breaker = get_urls_data(url, header)

        # 传递参数，清楚数据，免得列表里数据放太多太多炸了，此时的RESULT_DATA 里面已经有10条数据了
        # print(RESULTS_DATA)
        for result_data in tmp_data:
            params = (result_data['Type'], result_data['UPdate'], result_data['Title'],
                      result_data['AuthorName'], result_data['VoteUP'],
                      result_data['Content'])
            try:
                # 执行命令
                my_cursor.execute(sql, params)
                coon.commit()
                # print("===================  success !!!!")
            except Exception:
                print("===========  出现错误！本条数据跳过 疑似推测日报数据（非采集范围===========")
                error_count += 1
                # 这里必须用continue
                continue
        # 试图清空数据，减少缓存
        tmp_data = []
        # 函数中的这个计数器已经增加了1了，这里是提示上的纠正
        print("第 %d 轮数据已经存储完毕，已经清空tmp_data" % turn)
        if flag_breaker == 1:
            break
        time.sleep(random.randint(3, 5))
        off_set += 10
        turn += 1
    my_cursor.close()
    coon.close()
    end = time.time()
    print("+++++++++++++++++  数据库已经关闭  +++++++++++++++++")
    print("程序完全结束！运行时间: %f" % (end - start) + 's' + '  已知错误跳过的数据：%d' % error_count)
    return


if __name__ == '__main__':
    search = SearchTerm('渣男')
    search.topic_id, note = get_topic_id(search.keywords, search.header)
    # spider(search.keywords, search.topic_id, search.header)

    print(search.topic_id)
    print(note)


# 测试完成
