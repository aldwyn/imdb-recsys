from bottle import *
from pprint import pprint
from recsys.algorithm.factorize import SVD
from recsys.datamodel.data import Data
import pickle
import json
import sqlite3


@route('/')
def index():
	movielist = {}
	with sqlite3.connect('data/data100.db') as con:
		cur = con.cursor()
		cur.execute("SELECT * FROM movies")
		movies = cur.fetchall()
		for m in movies:
			cur.execute("SELECT AVG(ratings) FROM ratings WHERE movie_id = ?", (m[0],))
			avg = cur.fetchone()[0]
			movielist[avg] = {
				'mid': m[0],
				'title': m[1],
				'description': m[2],
				'image': m[3],
				'year': m[4]
			}
	session_user = request.get_cookie('session_user', secret='recsys') if 'session_user' in request.cookies else None
	return template('static/index.html', movielist=movielist, session_user=session_user)


@route('/feeds')
def get_feeds():
	movielist = {}
	with sqlite3.connect('data/data100.db') as con:
		cur = con.cursor()
		cur.execute("SELECT * FROM ratings WHERE user_id = ?", (request.get_cookie('session_user', secret='recsys')[0],))
		if cur.fetchone():
			cur.execute("SELECT ratings, movie_id, user_id FROM ratings")
			rating_results = cur.fetchall()
			d = Data()
			d.set(rating_results)
			# with open('data/tmp.dat', 'a') as f:
			# 	for l in rating_results:
			# 		f.write('%d,%d,%d\n' % (l[0], l[1], l[2]))
			svd = SVD()
			# svd.load_data(filename='data/tmp.dat', sep=',', format={'col': 0, 'row': 1, 'value': 2, 'ids':int})
			svd.set_data(d)
			recommendations = [str(s[0]) for s in svd.recommend(request.get_cookie('session_user', secret='recsys')[0], is_row=False)]
			cur.execute("SELECT * FROM movies WHERE movie_id IN (%s)" % (', '.join(recommendations)))
			similar_movies = cur.fetchall()
			for m in similar_movies:
				movielist[m] = {
					'mid': m[0],
					'title': m[1],
					'description': m[2],
					'image': m[3],
					'year': m[4]
				}
		else:
			cur.execute("SELECT * FROM movies")
			movies = cur.fetchall()
			for m in movies:
				cur.execute("SELECT AVG(ratings) FROM ratings WHERE movie_id = ?", (m[0],))
				avg = cur.fetchone()[0]
				movielist[avg] = {
					'mid': m[0],
					'title': m[1],
					'description': m[2],
					'image': m[3],
					'year': m[4]
				}
	session_user = request.get_cookie('session_user', secret='recsys') if 'session_user' in request.cookies else None
	return template('static/feeds.html', movielist=movielist, session_user=session_user)


@route('/movie/<movie_id>')
def get_movie(movie_id):
	movie = {}
	rating = 0
	with sqlite3.connect('data/data100.db') as con:
		cur = con.cursor()
		cur.execute("SELECT * FROM movies WHERE movie_id = ?", (movie_id,))
		movie_result = cur.fetchone()
		cur.execute("SELECT director FROM movie_directors WHERE movie_id = ?", (movie_id,))
		directors = cur.fetchall()
		cur.execute("SELECT actor FROM movie_actors WHERE movie_id = ?", (movie_id,))
		actors = cur.fetchall()
		cur.execute("SELECT writer FROM movie_writers WHERE movie_id = ?", (movie_id,))
		writers = cur.fetchall()
		cur.execute("SELECT genre FROM movie_genres WHERE movie_id = ?", (movie_id,))
		genres = cur.fetchall()
		if 'session_user' in request.cookies:
			cur.execute("SELECT * FROM ratings WHERE user_id = ? AND movie_id = ?", (request.get_cookie('session_user', secret='recsys')[0], movie_id,))
			rating = cur.fetchone()
		cur.execute("SELECT * FROM ratings")
		rating_results = cur.fetchall()
		d = Data()
		d.set(rating_results)
			# with open('data/tmp.dat', 'a') as f:
			# 	for l in rating_results:
			# 		f.write('%d,%d,%d\n' % (l[0], l[1], l[2]))
		svd = SVD()
			# svd.load_data(filename='data/tmp.dat', sep=',', format={'col': 0, 'row': 1, 'value': 2, 'ids':int})
		svd.set_data(d)
		similar_list = [str(s[0]) for s in svd.similar(int(movie_id))]
		cur.execute("SELECT * FROM movies WHERE movie_id IN (%s)" % (', '.join(similar_list)))
		similar_movies = cur.fetchall()
		movie = {
			'mid': movie_result[0],
			'title': movie_result[1],
			'description': movie_result[2],
			'image': movie_result[3],
			'year': movie_result[4],
			'directors': [d[0] for d in directors],
			'writers': [w[0] for w in writers],
			'actors': [a[0] for a in actors],
			'genres': [g[0] for g in genres],
			'rating': rating,
			'similar_movies': similar_movies,
		}
	session_user = request.get_cookie('session_user', secret='recsys') if 'session_user' in request.cookies else None
	return template('static/movie.html', movie=movie, session_user=session_user)


@route('/login')
def login():
	with sqlite3.connect('data/data100.db') as con:
		cur = con.cursor()
		cur.execute("SELECT * FROM users WHERE name = ?", (request.query.username,))
		curr = cur.fetchone()
		if curr:
			response.set_cookie('session_user', curr, secret='recsys')
			redirect('/feeds')
		else:
			redirect('/')


@route('/logout')
def logout():
	response.delete_cookie('session_user')
	redirect('/')


@route('/signup')
def signup():
	curr_user = None
	with sqlite3.connect('data/data100.db') as con:
		cur = con.cursor()
		cur.execute("INSERT INTO users VALUES(?, ?)", (None, request.query.username))
		cur.execute("SELECT * FROM users WHERE name = ?", (request.query.username,))
		curr_user = cur.fetchone()
		for p in request.query.getlist('genre'):
			cur.execute("INSERT INTO user_preferences VALUES(?, ?)", (curr_user[0], p))
	response.set_cookie('session_user', curr_user, secret='recsys')
	redirect('/feeds')


@route('/genre/<genre>')
def search_genre(genre):
	movielist = {}
	with sqlite3.connect('data/data100.db') as con:
		cur = con.cursor()
		cur.execute("SELECT * FROM movies WHERE movie_id IN (SELECT movie_id FROM movie_genres WHERE genre = ?)", (genre,))
		movies = cur.fetchall()
		for m in movies:
			movielist[m[0]] = {
				'mid': m[0],
				'title': m[1],
				'description': m[2],
				'image': m[3],
				'year': m[4]
			}
	session_user = request.get_cookie('session_user', secret='recsys') if 'session_user' in request.cookies else None
	return template('static/search.html', movielist=movielist, keyword=genre, session_user=session_user)


@route('/search')
def search():
	movielist = {}
	with sqlite3.connect('data/data100.db') as con:
		cur = con.cursor()
		cur.execute("SELECT * FROM movies WHERE title LIKE ?", ('%' + request.query.keyword + '%',))
		movies = cur.fetchall()
		for m in movies:
			movielist[m[0]] = {
				'mid': m[0],
				'title': m[1],
				'description': m[2],
				'image': m[3],
				'year': m[4]
			}
	session_user = request.get_cookie('session_user', secret='recsys') if 'session_user' in request.cookies else None
	return template('static/search.html', movielist=movielist, keyword=request.query.keyword, session_user=session_user)


@route('/rate/<user_id>/<movie_id>')
def rate_movie(user_id, movie_id):
	with sqlite3.connect('data/data100.db') as con:
		cur = con.cursor()
		cur.execute("INSERT INTO ratings VALUES (?, ?, ?)", (int(user_id), int(movie_id), int(request.query.rating)))
	redirect('/movie/%s' % movie_id)


@route('/css/<filename>')
def get_stylesheet(filename):
	return static_file(filename, root='static/css/')


@route('/js/<filename>')
def get_script(filename):
	return static_file(filename, root='static/js/')


@route('/img/<filename>')
def get_image(filename):
	return static_file(filename, root='data/images/')


@route('/fonts/<filename>')
def get_stylesheet(filename):
	return static_file(filename, root='static/fonts/')


@error(404)
def error404(error):
	return 'Nothing here, sorry'


run(host='localhost', port=8080)