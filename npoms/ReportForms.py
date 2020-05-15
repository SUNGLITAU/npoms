import pandas as pd
import csv
import os
import calendar
from dateutil.parser import parse
from pyecharts import options as opts
from pyecharts.charts import Pie, Scatter, Page
from DataProcessing import connect_mysql
from OtherTools import clear_all_var


# 从数据库获取数据
def get_tpm(start_time, end_time, topic_id):  # times per month
    """
    日期变化，获取到生成饼图需要的数据
    :param start_time:
    :param end_time:
    :param topic_id:
    :return: null
    """
    start_time, end_time, topic_id = str(start_time), str(end_time), str(topic_id)
    start = parse(start_time)  # 'datetime.date' objects is not writable 日期不可修改
    print('times per month')
    change = start
    end = parse(end_time)
    results = []
    print('get_tpm 初始化成功')
    for count in range(1, (end.year-start.year) * 12 + end.month - start.month + 2):
        i = change.month
        if i % 12 == 0:
            i = 12
        else:
            i = i % 12
        last_day_tmp = calendar.monthrange(change.year, i)
        print(last_day_tmp)
        last_day = '%d%02d%d' % (change.year, i, last_day_tmp[1])
        print(last_day)
        tmp_data = connect_mysql('%s%02d%02d' % (change.year, change.month, change.day), last_day, topic_id)
        # '235959' 避免因为办闭半开丢失查询的数据
        results.append({'month': '%d%02d' % (change.year, i), 'num': tmp_data.shape[0]})
        # print(tmp_data)
        if change.month == 12:
            change = '%s%02d%s' % (change.year+1, 1, '01')
        else:
            change = '%s%02d%s' % (change.year, i+1, '01')  # <class 'str'>
        change = parse(change)
    return results


# 从csv获取数据
def get_tpm2(start_time, end_time, topic_id):  # times per month
    """
    获取到scatter的x，y轴的数据
    :param start_time:
    :param end_time:
    :param topic_id:
    :return: 返回的是两个列表，方便作为scatter的x，y轴
    """
    csv_file = './data/textrank/topic{}_{}-{}abstract.csv'.format(str(topic_id), str(start_time), str(end_time))
    csv_data = pd.read_csv(csv_file, low_memory=False)  # 防止弹出警告
    print('csv_data 读取成功')
    a = csv_data['更新时间']
    b = csv_data['sentiment']
    return a.tolist(), b.tolist()


def pie_html(data):
    name_list = []
    num_list = []
    for i in range(len(data)):
        num_list.append(data[i]['num'])  # value
        name_list.append(data[i]['month'])  # name

    c = (
        Pie(init_opts=opts.InitOpts(width='100%'))  # init_opts=opts.InitOpts(width='1000px', height='800px')
        .add(
            '',
            [list(z) for z in zip(name_list, num_list)],
            label_opts=opts.LabelOpts(position='center'),
            radius=["35%", "75%"],
            center="50%",  # 这个是 质心的位置
            rosetype="radius",  # 南丁格尔

        )
        .set_global_opts(
            title_opts=opts.TitleOpts(  # 标题
                title="话题精华每月数量南丁格尔图",
                pos_left='center',
                ),
            legend_opts=opts.LegendOpts(  # 注释
                pos_left="right",
                orient="vertical",
                pos_top='30',
                ),
        )
        .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))

    )
    # c.render('./data/reportforms/pie.html')
    print(' >>>>>  >>>>  Pie已经生成  >>>>  >>>>>')
    print(type(c))
    return c


def scatter_sentiment(x, y):
    y = [round(i, 4) for i in y]

    c = (
        Scatter(
            init_opts=opts.InitOpts(width='100%'),
        )
        .add_xaxis(x)
        .add_yaxis('情绪值（由snownlp进行计算）', y)
        .set_global_opts(
            title_opts=opts.TitleOpts(
                title="精华文本の情绪-时间 散点图",
                pos_left='center',
            ),
            xaxis_opts=opts.AxisOpts(
                splitline_opts=opts.SplitLineOpts(is_show=True),  # 显示x轴分割线
                axislabel_opts=opts.LabelOpts(position='center', ),
                name='时间线',

            ),
            yaxis_opts=opts.AxisOpts(
                splitline_opts=opts.SplitLineOpts(is_show=True),
                name='情绪值',  # 轴的名字
            ),
            legend_opts=opts.LegendOpts(
                pos_right='20',
                orient='vertical',
                pos_top='20'
            ),
            axispointer_opts=opts.MarkPointOpts(
                # 我太难了
            )
        )
    )
    # c.render("./data/reportforms/scatter_splitline.html")  # 这个拿出来之后就是又不是str了，醉了
    print(' >>>>>  >>>>  Scatter已经生成  >>>>  >>>>>')
    # print('情绪：', type(c))  # ？你为什么回事str
    return c


def html_report(a, b, c):
    """
    统合前面的函数并组装HTML报告
    :param a: 开始时间
    :param b: 结束时间
    :param c: 话题id
    :return:
    """
    x, y = get_tpm2(a, b, c)
    print(a, b, c, type(a), type(b), type(c))
    data = get_tpm(a, b, c)
    page = Page(layout=Page.SimplePageLayout, page_title='舆情分析统计报告')
    page.add(

        scatter_sentiment(x, y),
        pie_html(data),
    )
    page.render("./data/reportforms/report_topic{}_{}-{}.html".format(c, a, b))
    print('==================  动态网页组装完成,已保存 ==================')

    sao_operation = '''
    <h3 style="text-align:center">TF-IDF 关键词/主旨词汇提取</h1>
    <p style="text-align:center"><img src="../wordcloud/wc_tf_idf_topic{}.png" width=85% /></p>
    <h3 style="text-align:center">K-Means 聚类词汇展示</h2>
    <p style="text-align:center"><img src="../wordcloud/wc_k_means_topic{}_result.png" width=85% /></p>
    <h3 style="text-align:center">其他 资料</h2>
    <p style="text-align:center"><a href="../textrank/topic{}_{}-{}abstract.csv">点击打开您查询日期内的csv摘要文件</a></p>
    <p style="text-align:center"> 注： 以上所有报告均已去除无效值（仅含文本数据) </p>
    </body>
    </html>
    '''.format(c, c, c, a, b)

    with open('./data/reportforms/report_topic{}_{}-{}.html'.format(c, a, b), 'r', encoding='utf-8') as h:
        content = h.read()
        content = content.replace('</body>\n</html>', '')
    with open('./data/reportforms/report_topic{}_{}-{}.html'.format(c, a, b), 'w', encoding='utf-8') as h:
        tmp = content + sao_operation
        h.write(tmp)
    now_path = os.getcwd()
    path = now_path.replace('\\', '/')
    os.startfile(path + '/data/reportforms/report_topic{}_{}-{}.html'.format(c, a, b))
    clear_all_var()
    return


if __name__ == '__main__':
    data1 = [
        {'value': 235, 'name': '视频广告'},
        {'value': 274, 'name': '联盟广告'},
        {'value': 310, 'name': '邮件营销'},
        {'value': 335, 'name': '直接访问'},
        {'value': 400, 'name': '搜索引擎'}
    ]
    html_report('20191201', '20200418', '19622792')
    print('>>> >>> >>>> >>  完成  >> >>>> >>> >>>')




