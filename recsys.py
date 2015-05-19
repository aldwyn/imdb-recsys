from scikits.crab.models import MatrixPreferenceDataModel
from scikits.crab.metrics import pearson_correlation
from scikits.crab.similarities import UserSimilarity
from scikits.crab.recommenders.knn import UserBasedRecommender

import pickle
import sqlite3
from pprint import pprint


def recommend(target):
	ratings_dict = {}
	with sqlite3.connect('data/data100.db') as con:
		cur = con.cursor()
		cur.execute("SELECT * FROM ratings")
		ratings_tuple = cur.fetchall()
		for r in ratings_tuple:
			if r[0] not in ratings_dict:
				ratings_dict[r[0]] = {}
			ratings_dict[r[0]][r[1]] = r[2]
	model = MatrixPreferenceDataModel(ratings_dict)
	similarity = UserSimilarity(model, pearson_correlation)
	recommender = UserBasedRecommender(model, similarity, with_preference=True)
	return recommender.recommend(int(target))
