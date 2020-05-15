import pandas as pd
import gc
import re
import os
import time
from textrank4zh import TextRank4Keyword, TextRank4Sentence
from DataProcessing import connect_mysql
from OtherTools import clear_all_var
from snownlp import SnowNLP


def get_abstract(data, a, b, c):
    """
    生成excel可以打开的的摘要文件
    :param data: MySQL从取出的数据
    :param a: 起始时间的
    :param b: 结束时间
    :param c: 话题ID
    :return: null
    """
    now_path = os.getcwd()
    path = now_path.replace('\\', '/')
    tr4s = TextRank4Sentence()

    print('当前文章的摘要：')
    results = []
    for i in range(len(data['CONTENT'])):

        # i = re.sub("[^\u4e00-\u9fa5]", '', i)  # 记住只留文本？没有断句算不上摘要，这里需要用其他方式处理
        # print('\u3002 \uff1b \uff0c \uff1a \u201c \u201d'
        #       '\uff08 \uff09 \u3001 \uff1f \u300a \u300b')
        # # 。 ； ， ： “ ”（ ） 、 ？ 《 》
        tmp = re.sub("[^\u4e00-\u9fa5\u3002\uff1b\uff0c\uff1a\u201c\u201d\uff08\uff09\u3001\uff1f\u300a\u300b0-9]", '', data['CONTENT'][i])
        tr4s.analyze(text=tmp, lower=True)
        result = ''
        # print()
        # print('摘要：')
        for item in tr4s.get_key_sentences(num=3):
            # print(item.index, item.weight, item.sentence)
            result += item.sentence
        if len(result) != 0:
            results.append([data['UPTIME'][i], data['TITLE'][i], data['AUTHOR'][i], result])
        # data['CONTENT'][i] = results
    column_name = ['更新时间', '标题/题目', '作者', '摘要']

    tmp_text = pd.DataFrame(columns=column_name, data=results)
    tmp_text.to_csv('./data/textrank/topic{}_{}-{}abstract.csv'.format(c, a, b), encoding='utf_8_sig')
    print('>>>>>>>>>>>>>>  已经保存到csv等待计算或查看  >>>>>>>>>>>>>>>')
    # os.startfile(now_path + '/data/textrank/topic{}_{}-{}abstract.csv'.format(c, a, b))  # 弹出工作表
    # 但是这里需要完整的工作路径才行 T:/AC/Python/PublicOpinionMonitor/data/textrank/topic{}_abstract.csv
    # print(results)
    # print(' >>>>>> >>>>>>>>>   将在10秒后关闭excel   >>>>>>> >>>>>>>> ')
    time.sleep(10)
    clear_all_var()
    return


def data_get(a, b, c):
    data = connect_mysql(a, b, c)  # 恋爱：19564412 武汉：19570564 <class 'pandas.core.series.Series'>
    return data


def analysis_sentiment(a, b, c):
    """
    在摘要中追加注入感情的倾向值
    :param a: 开始时间
    :param b: 结束
    :param c: 话题ID
    :return: null
    """
    # 防读取错误
    time.sleep(3)
    cc = os.system('tasklist|find /i "excel.exe"')
    while cc == 0:
        os.system('taskkill /IM excel.exe')

        time.sleep(3)
        print('>>>> 正在尝试关闭了已经打开的csv文件， >>>>> >>>> >>>>')
        cc = os.system('tasklist|find /i "excel.exe"')
    else:
        print('>>>> 不存在打开的csv文件，开始执行情感分析 >>>>> >>>> >>>>')
        pass

    csv_file = './data/textrank/topic{}_{}-{}abstract.csv'.format(c, a, b)
    csv_data = pd.read_csv(csv_file, low_memory=False)  # 防止弹出警告

    # 情感分析
    results = []
    for i in csv_data['摘要']:
        s = SnowNLP(i)
        results.append(s.sentiments)

    csv_data['sentiment'] = results
    csv_data.to_csv('./data/textrank/topic{}_{}-{}abstract.csv'.format(c, a, b), encoding='utf_8_sig', index=False)
    print('............  情感值追加注入完成   ...........')

    # 直接计算数据库的数据太过庞大，改为计算摘要的情感
    clear_all_var()
    return


def get_abs(start_time, end_time, topic_id):
    """
    统合上面的所有功能
    :param start_time: 开始时间
    :param end_time: 结束时间
    :param topic_id: 话题id
    :return: null
    """
    start = time.time()
    tmp = data_get(start_time, end_time, topic_id)
    get_abstract(tmp, start_time, end_time, topic_id)
    # return
    # for i in range(len(tmp['CONTENT'])):
    #     print(tmp['TITLE'][i])
    #     print(tmp['AUTHOR'][i])
    #     break  # success!

    # 注意：无法追加写入打开了的文件。请关闭后重试（直接在这里面关闭文件夹算了
    analysis_sentiment(start_time, end_time, topic_id)  # 内容为空的时候无法进行下一步计算
    print(' 文本摘要和情感分析模块 消耗了 {} s'.format(time.time() - start))
    clear_all_var()
    return


if __name__ == '__main__':
    get_abs('20191201', '20200418', '19622792')


