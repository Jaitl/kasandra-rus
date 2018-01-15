from app.lib.normalizing import nomalize
from app.lib.vectorization import tf_idf, sem_groups
from app.lib.clustering import kmeans, affinity_propagation
from app.lib.cluster_specter import compute_for_cluster, generate_plot
from app.lib.hirst import SelfSimilarityHirst

from app.config import path_to_tmp_image

from sklearn import metrics
import uuid
from itertools import groupby


def compute_matrix(data, news):
    news_content = list(map(lambda x: x['content'], news))

    if data['limit_words'] == True:
        word_count = data['words_count']
    else:
        word_count = None

    if data['vect_algorithm'] == "tf_idf":
        norm_texts = nomalize(news_content)
        (names, vect_res) = tf_idf(norm_texts, word_count)
    elif data['vect_algorithm'] == "sem_group_tf_idf":
        norm_texts = nomalize(news_content, with_pos=True)
        (names, vect_res) = sem_groups(norm_texts, word_count)
    else:
        raise Exception("unknown vectorization algorithm: %s" %
                        data['vect_algorithm'])

    return (names, vect_res)


def compute_clusters(data, matrix):
    if data['cluster_algorithm'] == 'kmeans':
        cluster_count = data['cluster_count']
        labels = kmeans(matrix, cluster_count)
    elif data['cluster_algorithm'] == 'aff_prop':
        labels = affinity_propagation(matrix)
    else:
        raise Exception("unknown clustering algorithm: %s" %
                        data['cluster_algorithm'])

    return labels


def do_vectorization(data, news):
    (names, vect_res) = compute_matrix(data, news)

    vect_list = [[round(y, 3) for y in x] for x in vect_res.toarray()]

    result = {
        "title": names,
        "matrix": vect_list,
        "rows": vect_res.shape[0],
        "columns": vect_res.shape[1]
    }
    return result


def do_clustering(data, news):
    news_titles = list(map(lambda x: x['title'], news))
    (names, matrix) = compute_matrix(data, news)
    labels = compute_clusters(data, matrix)

    ss = metrics.silhouette_score(matrix, labels)

    labels_list = sorted(list(set(labels.tolist())))

    labels_map = { x: str(uuid.uuid4()) for x in labels_list}

    clusters_three = []

    for l in labels_list:
        count = len([x for x in labels if x == l])
        three_node = {
            "id": labels_map[l],
            "parent": "#",
            "text": "Кластер %s (кол-во новостей: %s)" % (l + 1, count)
        }
        clusters_three.append(three_node)

    for lab, news_title in zip(labels, news_titles):
        three_node = {
            "id": str(uuid.uuid4()),
            "parent": labels_map[lab],
            "text": news_title
        }
        clusters_three.append(three_node)

    result = {
        "clusters_three": clusters_three,
        "cluster_count": len(labels_list),
        "silhouette_score": round(ss, 3)
    }

    return result


def do_analysis(data, news):
    (names, matrix) = compute_matrix(data, news)
    labels = compute_clusters(data, matrix)

    news_info = sorted(zip(news, labels, matrix), key=lambda x: x[1])

    for label, news_data in groupby(news_info, lambda x: x[1]):
        cluster_data = list(news_data)
        news_and_vector = [(x[0], x[2]) for x in cluster_data]
        (cos_news, start_year, end_year) = compute_for_cluster(news_and_vector, matrix.shape)

        path_to_image_spect = path_to_tmp_image(str(uuid.uuid4()) + ".spect.png")
        generate_plot(cos_news, start_year, end_year, label + 1, path_to_image_spect)

        hirst = SelfSimilarityHirst()
        h_res = hirst.compute(list(cos_news.items()))

        path_to_image_hirst = path_to_tmp_image(str(uuid.uuid4()) + ".hirst.png")
        h_res.plot(path_to_image_hirst)


    return 'ok'