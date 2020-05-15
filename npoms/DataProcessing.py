import jieba
import time
import re
import pymysql
import gc
import pandas as pd
import numpy as np
from KMeansStudy import distance_p2p, my_k_means
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from TopicSpider import get_topic_id
from SearchTerm import SearchTerm
from OtherTools import clear_all_var
from Visualization import wc4tf_idf, wc4k_means
from TF_IDFStudy import tf_idf_matrix


np.seterr(divide='ignore', invalid='ignore')  # 尝试去除警报


def connect_mysql(start_time, end_time, topic_id):  # str str str
    coon = pymysql.connect(
                            host='localhost',
                            port=3306,
                            user='root',
                            password='jjkl',
                            db='db4zhihuspider',
                            charset='utf8'
                            )
    my_cursor = coon.cursor()
    print("================== 数据链接完成：游标生成 ====================")
    # print('flag A', topic_id, type(topic_id))
    table_name = 'topic' + topic_id
    # print(table_name)
    sql_select = 'SELECT UPTIME,TITLE,AUTHOR,CONTENT FROM {} WHERE UPTIME >= {} AND UPTIME <= {};'.format(table_name, start_time, end_time + '235959')

    # 连接开始，获取数据
    df = pd.read_sql(sql_select, coon)
    print('本次获得的文本的条数为： %d' % len(df['CONTENT']))
    # 获取数据后关闭数据库
    my_cursor.close()
    coon.close()
    print("================== 数据获取完成：游标关闭、数据库关闭 ====================")
    del my_cursor
    del coon
    return df


def jieba_cut(data):
    """
    对所有文本完成分词，其中单个字认为没有意义，将被过滤掉
    :param data: MySQL中取出来的文本
    :return: 词汇组成的矩阵
    """
    print("================== 结巴切词正在生成列表：请稍候 ====================")
    special_list = jieba.load_userdict('./data/setup/jieba_suggestions.txt')

    tmp_list = []
    stop_words_list = [line.strip() for line in open('./data/setup/stop_words.txt', 'r').readlines()]
    collector = []

    for item in data['CONTENT']:
        # if len(item) <= 1:
        #     continue
        item = re.sub("[^\u4e00-\u9fa5]", '', item)
        tmp = jieba.lcut(item)
        tmp = [w for w in tmp if w not in stop_words_list]
        tmp = [w for w in tmp if len(w) > 1]
        tmp = ' '.join(tmp)
        collector.append(tmp)
    # print(type(collector))
    # print(collector)
    return collector  # <class 'list'> ['aa bb cc', '', '']


def tf_idf(o_collector):
    """
    这一步中讲把频率高的词语拿出来方便WordCloud使用
    :param o_collector: 单个词汇为x轴，文本（数）为y轴组成的矩阵
    :return: 权重和特征（词
    """
    print("================== TF-IDF：请稍候 ====================")
    weight, features = tf_idf_matrix(o_collector)

    print("================== 词频统计中 ====================")

    # 取前面300个词作为词云的对象
    tmp_word_cloud = open('./data/tmp4tfidf/tmp4wordcloud.txt', 'w', encoding='utf-8')
    i = 0
    weight_fre = np.sum(weight, axis=0)
    for i in range(len(features)):
        fre = weight_fre[i]
        if fre < 1.1:  # 过滤异常数据
            tmp_word_cloud.write(features[i] + ' ' + str(fre) + '\n')
    tmp_word_cloud.close()
    print('需要词云处理的tfidf临时文件已经生成，\n正在等待可视化模块的调用，请稍候...')
    return weight, features


def k_means_mine(o_weight, o_features, k):
    """
    完成K-Means聚类，把同类的词语分在一起，分别保存为临时文件
    :param o_weight: 词权重
    :param o_features: 特征词
    :param k: 簇类
    :return: null
    """
    weight, features, cluster = o_weight, o_features, k
    print('================== KMenas ====================')

    centroids, index_distance = my_k_means(weight, cluster)

    tmp = centroids.argsort()[:, ::-1]

    for i in range(cluster):
        print("cluster %d:" % i, end='')
        tmp_words_txt = open("./data/tmp4kmeans/Cluster{}.txt".format(i), "w", encoding='utf-8')
        for j in tmp.A[i, :50]:
            print(' %s ' % features[j], end='')
            tmp_words_txt.write(features[j] + '\n')
        tmp_words_txt.close()
        print()
    print('需要词云处理的kmeans临时文件已经生成，\n正在等待可视化模块的调用，请稍候...')
    clear_all_var()
    return


def analysis(start_time, end_time, topic_id, k):
    """
    统合前面的所有函数
    :param start_time: 开始时间
    :param end_time: 结束时间
    :param topic_id: 话题ID
    :param k: 簇类
    :return: 作为其他函数处理的标志
    """
    start = time.time()
    data = connect_mysql(start_time, end_time, topic_id)
    try:
        print(data['CONTENT'][0])
    except Exception:
        print('您所查日期内并没有值，告辞')
        return 0

    collector = jieba_cut(data)
    x, y = tf_idf(collector)

    k_means_mine(x, y, k)

    # 根据词频生成词云
    wc4tf_idf(topic_id, k)
    # 根据KMeans生成词云
    wc4k_means(topic_id, k)
    print("================== 词云已经生成 ====================")
    end = time.time()
    print("分析结束！运行时间: %f" % (end - start) + 's')
    clear_all_var()
    return 1


if __name__ == '__main__':
    # search = SearchTerm('武汉')
    # search.topic_id, note = get_topic_id(search.keywords, search.header)
    # analysis('20191201', '20200418', '19622792', 3)
    # 3月2号，痛苦，正文文本是“求而不得”，造成了一连串的异常，测试使用’的，及‘导致了异常，结巴分词产生的单字会造成异常tf-idf异常
    # 但是同时某些单字是能够表达情绪的，但是在实际表达之中，这类单个字的形容词玩玩会跟上一个程度副词表示程度，在例子
    # '我痛他有点痛大家很痛' 中，分词的结果为'我痛', '他', '有点痛', '大家', '很痛'
    # 因此认为单字缺乏足够的意义，同时也因为没有更好地处理方式，结巴分析时会过滤掉这些单字。
    analysis('20200901', '20200904', '19570564', 4)


