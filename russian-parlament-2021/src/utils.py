import pandas as pd
import numpy as np

import re
from wordcloud import WordCloud
import umap

import matplotlib.pyplot as plt 
from scipy.cluster.hierarchy import dendrogram
from sklearn.cluster import KMeans, AgglomerativeClustering


def remove_name_from_text(x):
    deputy_full_name = x['deputy_name'].lower().split()
    surname = a[0]
    name = a[1][0]
    fathers_name = a[2][0]
    deputy_full_name = '{} {} {} '.format(surname, name, fathers_name)
    return re.sub(deputy_full_name, "", x['lines_processed'])

def plot_word_cloud(topics, topic_number):
    """
        Строит визуализацию слов на основе текстов топиков
    """
    # получаем частоты и слова топика
    
    text = dict(topics[topic_number][1])
    
    # строим облако слов
    wordcloud = WordCloud(background_color="white", max_words=100, width=900, height=900, collocations=False)
    wordcloud = wordcloud.generate_from_frequencies(text)
    plt.figure(figsize=(12, 8))
    plt.title("Топик номер {}".format(topic_number))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()  
    
def get_umap_representation(data, random_state=0):
    umap_model = umap.UMAP(metric='cosine', min_dist=0.0, random_state=random_state)
    umap_rep = umap_model.fit_transform(data)
    return umap_rep

def plot_distortions(data, n_clusters_range=(1, 10)):
    distortions = []
    K = range(*n_clusters_range)
    for k in K:
        clust = KMeans(n_clusters=k)
        clust.fit(data)
        distortions.append(clust.inertia_)
        
    plt.figure(figsize=(6,4))
    plt.plot(K, distortions, 'bx-')
    plt.xlabel('k')
    plt.ylabel('Distortion')
    plt.title('The Elbow Method showing the optimal k')
    plt.show()
        
def plot_dendrogram(model, **kwargs):
    # Create linkage matrix and then plot the dendrogram

    # create the counts of samples under each node
    counts = np.zeros(model.children_.shape[0])
    n_samples = len(model.labels_)
    for i, merge in enumerate(model.children_):
        current_count = 0
        for child_idx in merge:
            if child_idx < n_samples:
                current_count += 1  # leaf node
            else:
                current_count += counts[child_idx - n_samples]
        counts[i] = current_count

    linkage_matrix = np.column_stack([model.children_, model.distances_,
                                      counts]).astype(float)

    # Plot the corresponding dendrogram
    dendrogram(linkage_matrix, **kwargs)