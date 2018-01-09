import os
import re
import math
import time
import numpy as np
import snowballstemmer as stem
from scipy.sparse import csr_matrix, linalg
import sklearn.preprocessing

def stem_text(text, stemming=stem.stemmer('english')):
    for word in stemming.stemWords(re.findall(r"[\w']+", text.lower())):
        yield word

#bag of file - ile razy w pliku wystepuje i-te slowo
#bag of all - zliczamy wszystkie slowa i na ktorej sa pozycji
def create_bag_of_words(path, bag_of_all):
    """Create bag of words for parsed file.
    :param path: path to file
    :param bag_of_all: bag_of_words set from previous iterations
    :return: bag_of_file set for parsed file
    """
    stem_algorithm = stem.stemmer('english')
    bag_of_file = {}
    with open(path, 'rt',encoding='ISO-8859-1') as file:
        for line in file.readlines():
            for word in stem_text(line.lower(), stem_algorithm):

                if word not in bag_of_all:
                    bag_of_all[word] = len(bag_of_all)

                if bag_of_all[word] in bag_of_file:
                    bag_of_file[bag_of_all[word]] += 1
                else:
                    bag_of_file[bag_of_all[word]] = 1
    return bag_of_file

def generate_docs_bags(dir_path, bag_of_all):
    docs_bags = {name: create_bag_of_words(dir_path + "/" + name, bag_of_all)
                  for name in os.listdir(dir_path)}
    return docs_bags

def inverse_document_frequency(docs_bag, bag_of_all ):
    for word in bag_of_all:
        nw = 0
        for file_ in docs_bag:
            if bag_of_all[word] in docs_bag[file_]:
                nw+=1

        idf = math.log10(len(docs_bag) / nw)

        for file_ in docs_bag:
            if bag_of_all[word] in docs_bag[file_]:
                docs_bag[file_][bag_of_all[word]] *= idf

def create_term_by_doc_matrix(docs_bag,bag_of_all):
        rows = []
        cols = []
        data = []
        docs = list(docs_bag.keys())

        #w ktorym pliku ktore slowo ile razy wystepuje

        for i, doc in enumerate(docs):
            col = docs_bag[doc].keys() #kolejne slowa indeksy
            data.extend([docs_bag[doc][x] for x in col])
            cols.extend(col)
            rows.extend([i] * len(col))

        term_matrix = csr_matrix((data, (rows, cols)),
                            shape=(len(docs_bag), len(bag_of_all)), dtype=float)
        return term_matrix

def single_value_decompose(matrix,k):
    U, S, V = linalg.svds(matrix, k)
    matrix = csr_matrix(U.dot(np.diag(S)).dot(V))
    return matrix

def normalize_matrix(matrix):
    sklearn.preprocessing.normalize(matrix, norm='l1', axis=1, copy=False)
    return matrix

def handle_matrix(dir_path,idf=True,svd=True):
    bag_of_all = {}
    docs_bags = generate_docs_bags(dir_path, bag_of_all)

    docs_names = list(docs_bags.keys())
    #print(docs_names)

    if idf:
        inverse_document_frequency(docs_bags, bag_of_all)

    term_matrix = create_term_by_doc_matrix(docs_bags,bag_of_all)
    if svd:
        term_matrix = single_value_decompose(term_matrix, 30)

    term_matrix = normalize_matrix(term_matrix)
    #print(term_matrix)



    return bag_of_all, docs_names, term_matrix

def query_into_vec(query, bag):
    vec = np.zeros(shape=len(bag))
    for word in stem_text(query.lower()):
        if word in bag:
            #print(bag[word])
            vec[bag[word]] += 1

    normalized_vec = vec / np.linalg.norm(vec)
    return normalized_vec


def docs_with_highest_corr(matrix, vec, n, names):
    arr = matrix.dot(vec)
    newarr = [b[0] for b in sorted(enumerate(arr),key=lambda i:i[1])]
    newarr = newarr[::-1]
    newarr = newarr[:10]

    print("\nTop %d results are:" % len(newarr))
    ind = []
    for index in newarr:
        ind.append(names[index])
        print(names[index])

    return ind

def search(name):
    bag, names, matrix = handle_matrix('set')
    vec = query_into_vec(name, bag)
    ind = docs_with_highest_corr(matrix,vec, 10, names)
    return ind


if __name__ == "__main__":
    main()
