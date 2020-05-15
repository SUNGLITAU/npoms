# -*- coding: utf-8 -*-
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from collections import defaultdict
from collections import Counter
import math
import operator
import pandas as pd
import numpy as np
import jieba


def std_td_idf():
    tmp_data = ['我 正在 学习 计算机 打酱油 刚下飞机 人在美国',
                '它 正在 吃饭 人在蒙古 沙特公主',
                '我 的 书 还 在 你 那儿',
                '今天 不 上班']
    vector = TfidfVectorizer()
    transform = TfidfTransformer()
    tmp = vector.fit_transform(tmp_data)
    tf_idf = transform.fit_transform(tmp)
    features = vector.get_feature_names()
    weight = tf_idf.toarray()
    print(features)  # <class 'list'>
    # print(type(features))
    print(weight)  # <class 'numpy.ndarray'>
    # print(type(weight))
    return


def tf_idf_matrix(tnp):
    # 读取待编码的文件
    docs_ = tnp

    # 将文件每行分词，分词后的词语放入words中
    words = []
    docs = []
    # for i in range(len(docs)):
    #     docs[i] = jieba.lcut(docs[i].strip("\n"))
    #     words += docs[i]
    # print(words)
    # words = tnp

    # print(docs)
    # print(words)

    for i in range(len(docs_)):
        docs.append(docs_[i].split(' '))
    for i in docs:
        words += i

    # 找出分词后不重复的词语，作为词袋
    # print(words.index)  # <built-in method index of list object at 0x0E39BB68>
    vocab = sorted(set(words), key=words.index)

    # 过滤单字 到底过滤不过滤还需要考虑
    vocab_true = []
    for i in vocab:
        if len(i) != 1:
            vocab_true.append(i)
    # print(vocab_true)
    del vocab

    # 建立一个M行V列的全0矩阵，M问文 档样本数，这里是行数，V为不重复词语数，即编码维度
    V = len(vocab_true)
    print(V)
    M = len(docs)
    print(M)
    onehot = np.zeros((M, V))  # 二维矩阵要使用双括号
    tf = np.zeros((M, V))

    for i, doc in enumerate(docs):
        for word in doc:
            if word in vocab_true:
                pos = vocab_true.index(word)
                onehot[i][pos] = 1
                tf[i][pos] += 1  # tf,统计某词语在一条样本中出现的次数

    row_sum = tf.sum(axis=1)  # 行相加，得到每个样本出现的词语数
    # 计算TF(t,d)
    tf = tf / row_sum[:, np.newaxis]  # 分母表示各样本出现的词语数，tf为单词在样本中出现的次数，[:,np.newaxis]作用类似于行列转置
    # 计算DF(t,D)，IDF
    df = onehot.sum(axis=0)  # 列相加，表示有多少样本包含词袋某词
    idf = list(map(lambda x: math.log10((M + 1) / (x + 1)), df))

    # 计算TFIDF
    tfidf = tf * np.array(idf)
    # tfidf = pd.DataFrame(tfidf, columns=vocab)
    return tfidf, vocab_true


if __name__ == '__main__':
    data = [['我', '正在', '学习', '计算机', '打酱油', '刚下飞机', '人在美国'],
            ['它', '正在', '吃饭', '人在蒙古', '沙特公主'],
            ['我', '的', '书', '还', '在', '你', '那儿'],
            ['今天', '不', '上班']]
    data2 = ['谢邀，人在美国，刚下飞机',
             '访问普金，会话川普',
             '刚订完婚，沙特公主，闲来无事玩玩知乎',
             '利益相关，匿了匿了']
    data3 = ['我 正在 学习 计算机 打酱油 刚下飞机 人在美国',
             '它 正在 吃饭 人在蒙古 沙特公主',
             '我 的 书 还 在 你 那儿',
             '今天 不 上班']

    # print('标准的tf_idf=====================================')
    # std_td_idf()

    print("测试使用的tf_idf 》》》》》》》》》》》》》》》》》》")
    vector_array, features = tf_idf_matrix(data3)
    print(vector_array)
    print(features)





