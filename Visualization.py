# coding=utf-8
import random
import PIL.Image as Image
from matplotlib import pyplot as plt
from wordcloud import WordCloud
from OtherTools import clear_all_var


# 这里实现，图片拼接，实现不同的颜色显示词云然后拼接相同这些图片
# 设置总图片大小为1920x1080.单张为 1920/CLUSTER_NUM，完成之后横向拼接


def get_stop_words():
    """
    读取data下setup中的自定义数据
    """
    stop_words = set()
    stop_words_file = open('./data/setup/word_cloud_stop_words.txt', encoding='utf-8')
    for tt in stop_words_file.readlines():
        stop_words.add(tt.strip('\n'))
    stop_words_file.close()
    clear_all_var()


def get_color():
    """
    因为WordCloud无法指定颜色，完成随机取色
    :return: 随机颜色
    """
    cmaps = [('Sequential', [
                'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
                'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
                'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']),
             ('Sequential (2)', [
                'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
                'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
                'hot', 'afmhot', 'gist_heat', 'copper']),
             ('Qualitative', [
                'Pastel1', 'Pastel2', 'Paired', 'Accent',
                'Dark2', 'Set1', 'Set2', 'Set3',
                'tab10', 'tab20', 'tab20b', 'tab20c'])]  # <class 'list'>
    boob = random.randint(0, 2)
    poop = cmaps[boob][1]
    color = poop[random.randint(0, len(poop) - 1)]
    return color


def wc4tf_idf(topic_id, k):
    """
    TF-IDF生成词云
    :param topic_id:
    :param k:
    """
    frequencies = {}
    for line in open('./data/tmp4tfidf/tmp4wordcloud.txt', encoding='utf-8'):
        arr = line.split(" ")
        frequencies[arr[0]] = float(arr[1])
    wc = WordCloud(
        font_path="./data/msyh.ttc",
        max_words=300,
        width=1920,
        height=1080,
        background_color='white',
        stopwords=get_stop_words()
    )
    word_cloud = wc.generate_from_frequencies(frequencies)
    # 写词云图片
    word_cloud.to_file("./data/wordcloud/wc_tf_idf_topic{}.png".format(topic_id))
    # 显示词云文件
    print('TF / IDF 词频图云已经完成，正在弹出图片，请稍候...')
    # Image.open("./data/wordcloud/wc_tf_idf_topic{}.png".format(topic_id)).show()
    clear_all_var()


def wc4k_means(topic_id, k):
    """
    主要根据临时文件的数据，在固定大小的情况下，先单独一张张地生成图片，再拼接起来
    :param topic_id:
    :param k:
    """
    tmp_width = int(1920 / k)
    for i in range(k):
        words = set()
        for line in open('./data/tmp4kmeans/Cluster{}.txt'.format(i), 'r', encoding='utf-8'):
            words.add(line.strip('\n'))
        words = ' '.join(words)  # <class 'str'>
        wc = WordCloud(
            font_path="./data/msyh.ttc",
            max_words=100,
            width=tmp_width,
            height=1080,
            background_color='white',
            stopwords=get_stop_words(),
            colormap=get_color()
        )
        word_cloud = wc.generate(words)
        # 写词云图片
        word_cloud.to_file("./data/wordcloud/wc_k_means_topic{}_{}.png".format(topic_id, i))
        # 显示词云文件
        plt.imshow(word_cloud)
        plt.axis("off")
        # plt.show()
        print("第 {}/{} 张分图已经切片完成".format(i+1, k))

    print('开始拼图')
    image_collector = []
    for i in range(k):
        tmp = Image.open('./data/wordcloud/wc_k_means_topic{}_{}.png'.format(topic_id, i))
        image_collector.append(tmp)
    width, height = image_collector[0].size
    result = Image.new(image_collector[0].mode, (width * len(image_collector), height))
    for i, im in enumerate(image_collector):
        result.paste(im, box=(i * width, 0))
    result.save('./data/wordcloud/wc_k_means_topic{}_result.png'.format(topic_id))
    print("图片拼接完成，正在弹出图片，请稍候...")
    # Image.open('./data/wordcloud/wc_k_means_topic{}_result.png'.format(topic_id)).show()
    clear_all_var()


if __name__ == '__main__':
    wc4tf_idf('19639859', 3)
    wc4k_means('19639859', 3)


