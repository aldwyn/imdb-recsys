import pickle
import numpy

from pprint import pprint

class movie_recommender():
	def __init__(self):
		self.movies = self.load_movies()
		self.movie_ratings = self.load_ratings()

	def load_movies(self):
		movies = {}
		with open('imdb100.pickle') as f:
			p = pickle.load(f)
			for element in p:
				movie =  p[element]
				movies[element] = movie
		return movies

	def load_ratings(self):
		movie_ratings = {}
		for i in xrange(1,101):
			movie_ratings[i] = []
		with open('data100') as f:
			for line in f:
				i = line.split(',')
				movie_id = int(i[1])
				rating = int(i[2])
				movie_ratings[movie_id].append(rating)
		return movie_ratings

	def most_rated(self):
		top_rated = {}
		for movie in self.movie_ratings:
			if len(self.movie_ratings[movie]) == 0:
				average = 0
			else:
				average = numpy.mean(self.movie_ratings[movie])
			top_rated[movie] = average
		top_rated = sorted(top_rated, key = top_rated.get, reverse=True)
		return self.movies[top_rated[0]], self.movies[top_rated[1]],self.movies[top_rated[2]]

	def new_user_recommend(self, preferences):
		movies = []
		top_rated = {}
		for i in self.movies:
			movie = self.movies[i]
			for genre in movie['genres']:
				if genre in preferences:
					movies.append(movie)
					break

		for m in movies:
			movie_id = int(m['id'])
			ratings = self.movie_ratings[movie_id]
			if len(ratings) == 0:
				average = 0
			else:
				average = numpy.mean(ratings)
			top_rated[movie_id] = average
		top_rated = sorted(top_rated, key = top_rated.get, reverse=True)
		recommend = []
		counter = 0
		for i in top_rated:
			recommend.append(self.movies[i])
			if counter == 2:
				break
			counter += 1
		return recommend


if __name__ == '__main__':
	x = movie_recommender()
	user_preferences = ['Animation']
	pprint(x.new_user_recommend(user_preferences))

