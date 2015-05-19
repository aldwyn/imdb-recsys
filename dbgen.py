import sqlite3
import json
import pickle
from pprint import pprint

def parse_data100():
	users_keys_lookup = {}
	with sqlite3.connect('data/data100.db') as con:
		cur = con.cursor()
		imdb100 = pickle.load(open('data/imdb100.pickle', 'rb'))
		imdb100_tuple = []
		for d in imdb100:
			imdb100_tuple.append((d, imdb100[d]['title'], imdb100[d]['description'], imdb100[d]['image'], imdb100[d]['year']))
		try:
			cur.execute("CREATE TABLE movies (movie_id INTEGER, title TEXT, description TEXT, image TEXT, year INTEGER)")
			cur.execute("CREATE TABLE movie_directors (movie_id INTEGER, director TEXT)")
			cur.execute("CREATE TABLE movie_writers (movie_id INTEGER, writer TEXT)")
			cur.execute("CREATE TABLE movie_actors (movie_id INTEGER, actor TEXT)")
			cur.execute("CREATE TABLE movie_genres (movie_id INTEGER, genre TEXT)")
			cur.execute("CREATE TABLE users (user_id INTEGER PRIMARY KEY, name TEXT)")
			cur.execute("CREATE TABLE ratings (user_id INTEGER, movie_id INTEGER, ratings REAL)")
		except:
			pass
		print 'db-logging movies...'
		cur.executemany("INSERT INTO movies VALUES (?, ?, ?, ?, ?)", imdb100_tuple)
		print 'db-logging movie-directors...'
		for d in imdb100:
			for director in imdb100[d]['directors']:
				cur.execute("INSERT INTO movie_directors VALUES (?, ?)", (d, director,))
		print 'db-logging movie-writers...'
		for d in imdb100:
			for writer in imdb100[d]['writers']:
				cur.execute("INSERT INTO movie_writers VALUES (?, ?)", (d, writer,))
		print 'db-logging movie-actors...'
		for d in imdb100:
			for actor in imdb100[d]['stars']:
				cur.execute("INSERT INTO movie_actors VALUES (?, ?)", (d, actor,))
		print 'db-logging genres...'
		for d in imdb100:
			for genre in imdb100[d]['genres']:
				cur.execute("INSERT INTO movie_genres VALUES (?, ?)", (d, genre,))
		print 'preparing data/movielens.pickle...'
		movielens = pickle.load(open('data/movielens.pickle', 'rb'))
		i = 1
		users_tuple = []
		ratings_tuple = []
		for user in movielens['data']:
			users_keys_lookup[user] = i
			users_tuple.append((i, None))
			for r in movielens['data'][user]:
				ratings_tuple.append((i, r, movielens['data'][user][r]))
			i += 1
		print 'db-logging users...'
		cur.executemany("INSERT INTO users VALUES (?, ?)", users_tuple)
		print 'db-logging ratings...'
		while ratings_tuple:
			lindex = len(ratings_tuple) if (len(ratings_tuple) < 999) else 999
			to_execute = ratings_tuple[:lindex]
			ratings_tuple = ratings_tuple[lindex:]
			cur.executemany("INSERT INTO ratings VALUES (?, ?, ?)", to_execute)
		print 'FINISHED. See data/data100.db.'


if __name__ == '__main__':
	parse_data100()