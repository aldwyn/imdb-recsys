from bottle import *

from pprint import pprint
from recsys import recommend
from top_rated import movie_recommender
import pickle
import json
import sqlite3

@route('/')
def index():
	return static_file('index.html', root='static/')


@route('/css/<filename>')
def get_stylesheet(filename):
	return static_file(filename, root='static/css/')


@route('/js/<filename>')
def get_script(filename):
	return static_file(filename, root='static/js/')


@route('/img/<filename>')
def get_image(filename):
	return static_file(filename, root='data/images/')


@route('/feeds', method='post')
def get_feeds():
	preferences = request.forms.getall('genre')
	movielist = []
	with sqlite3.connect('data/data100.db') as con:
		cur = con.cursor()
		cur.execute("SELECT user_id FROM users WHERE name = ?", (request.forms.name,))
		curr_user = cur.fetchone()
		if curr_user:
			print 'hey'
		else:
			cur.execute("INSERT INTO users VALUES(?, ?)", (None, request.forms.name))
			cur.execute("SELECT * FROM users WHERE name = ?", (request.forms.name,))
			curr_user = cur.fetchone()
			for p in preferences:
				cur.execute("INSERT INTO user_preferences VALUES(?, ?)", (curr_user[0], p))
			query = "SELECT movie_id FROM movie_genres WHERE genre IN ('%s')" % ("', '".join(preferences))
			cur.execute("SELECT * FROM movies WHERE movie_id IN (%s)" % query)
			movielist = cur.fetchall()
	return template('static/feeds.html', curr_user=curr_user, movielist=movielist)


@route('/recommendations/<user_id>')
def get_recommedations(user_id):
	recsys_result = recommend(user_id)
	to_execute = []
	for r in recsys_result:
		to_execute.append(str(r[0]))
	movielist = []
	curr_user = None
	with sqlite3.connect('data/data100.db') as con:
		cur = con.cursor()
		cur.execute("SELECT * FROM movies WHERE movie_id IN (%s)" % (', '.join(to_execute)))
		movielist = cur.fetchall()
		cur.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
		curr_user = cur.fetchone()
	return template('static/recommendations.html', curr_user=curr_user, movielist=movielist)	


@error(404)
def error404(error):
	return 'Nothing here, sorry'


run(host='localhost', port=8080)