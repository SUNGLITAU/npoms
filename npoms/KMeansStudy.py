import numpy as np


# print("》》》》》》》》》》》》》》》》》载入 K-Means算法 模块《《《《《《《《《《《《《《《《《《《")


# 距离函数：参数是两个向量
def distance_p2p(x, y):
    return np.sqrt(np.sum(np.power(x - y, 2)))
    # 多维向量的欧里几德距离是相同的
    # 有建议使用余弦距离的：在处理中文文本的时候


def cosine_p2p(vector1, vector2):
    op7 = 1 - np.dot(vector1, vector2)/(np.linalg.norm(vector1)*(np.linalg.norm(vector2)))
    return op7


def my_k_means(data, k):
    sample_num = np.shape(data)[0]
    index_distance_matrix = np.mat(np.zeros((sample_num, 2)))

    feature_num = np.shape(data)[1]
    # 初始化质心矩阵
    centroids_array = np.mat(np.zeros([k, feature_num]))
    for i in range(feature_num):
        min_feature = np.min(data[:, i])
        max_feature = np.max(data[:, i])
        # centroids_array: (cluster_num(k), sample_num)
        centroids_array[:, i] = min_feature + (max_feature - min_feature) * np.random.rand(k, 1)

    # 变化判断标志
    cluster_changed_flag = True
    while cluster_changed_flag:  # 这个个人命名为聚类循环（最外层循环）
        cluster_changed_flag = False
        # 在centroids_array中，sample是列
        for i in range(sample_num):
            # 初始化 该样本到簇心的最小距离 和 该样本的索引：这两个值一定会被更新，但是必须排除干扰
            min_distance = np.inf
            min_index = -1
            for j in range(k):
                # points_dist = distance_p2p(centroids_array[j, :], data[i, :])
                points_dist = cosine_p2p(centroids_array[j, :], data[i, :])
                if points_dist < min_distance:
                    min_distance = points_dist
                    min_index = j

            if index_distance_matrix[i, 0] != min_index:
                cluster_changed_flag = True
            # 没搞懂这里为什么参考文章存储的是最小距离距离是（欧里几德式）的平方
            index_distance_matrix[i, :] = min_index, min_distance

        for centroid in range(k):
            update_centroid = data[np.nonzero(index_distance_matrix[:, 0].A == centroid)[0]]
            if len(update_centroid) != 0:
                centroids_array[centroid, :] = np.mean(update_centroid, axis=0)

    return centroids_array, index_distance_matrix


if __name__ == '__main__':
    print("===== distance_P2P test =====")
    point_x, point_y = np.array([2, 3]), np.array([3, 4])
    print(distance_p2p(point_x, point_y))
    # 1.4142135623730951 2 ** 0.5

    print("===== cosine_P2P test =====")
    point_x, point_y = np.array([2, 3]), np.array([3, 4])
    print(cosine_p2p(point_x, point_y))

    print("=======   KMeans test =======")
    data_test = np.arange(90).reshape((9, 10))
    print("原始矩阵：")
    print(data_test)
    centroids, index_distance = my_k_means(data_test, 3)
    print("簇心矩阵（数组）：")
    print(centroids, type(centroids))
    # 一共有sample_num个矩阵
    print("簇的索引-到该簇的最小距离矩阵：")
    # print(index_distance[:, 1])
    print(index_distance, type(index_distance))
    print(type(data_test))

