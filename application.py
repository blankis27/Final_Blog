from flask import Flask, g, render_template, jsonify, url_for, flash
from flask import request, redirect, make_response
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from functools import wraps
from database_setup import Base, Blog, User, cliente
import random
import string
import json
import datetime

app = Flask(__name__)

# Connect to Database and create database session
engine = create_engine('sqlite:///blog.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/login', methods=['GET', 'POST'])
def login():

	if request.method == 'GET':
		state = ''.join(random.choice(
				string.ascii_uppercase + string.digits) for x in range(32))
		# store it in session for later use
		login_session['state'] = state
		return render_template('login.html', STATE = state)
	else:
		if request.method == 'POST':
			print ("dentro de POST login")
			
			user = session.query(User).filter_by(
				username = request.form['username'],
				password = request.form['password']).first()

			if not user:
				error = "Usuario no registrado!!!"
				return render_template('login.html', error = error)
			else:
				print ("dentro de user")
				login_session['username'] = request.form['username']
				return redirect(url_for('showMain', username=login_session['username']))
				#return render_template('public.html', username=login_session['username'])
				
def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if 'username' not in login_session:
			return redirect(url_for('login'))
		return f(*args, **kwargs)
	return decorated_function

def make_salt():
    return ''.join(random.choice(
                string.ascii_uppercase + string.digits) for x in range(32))

def make_pw_hash(name, pw, salt = None):
    if not salt:
        salt = make_salt()
    h = hashlib.sha256((name + pw + salt).encode('utf-8')).hexdigest()
    return '%s,%s' % (salt, h)

def valid_pw(name, password, h):
    salt = h.split(',')[0]
    return h == make_pw_hash(name, password, salt)

@app.route('/logout')
def logout():
		
		del login_session['username']

		return redirect(url_for('showMain'))

# Crear usuario
@app.route('/registrar', methods=['GET', 'POST'])
def registrar():

	if request.method == 'GET':
		return render_template('add-user.html')
	else:
		if request.method == 'POST':
			nuevoUsuario = User(
					username = request.form['username'],
					password=request.form['password'],
					email = request.form['email']) 
			session.add(nuevoUsuario)
			session.commit()
			login_session['username'] = request.form['username']
			return redirect(url_for('showMain'))

# Delete post
# /blog/eliminar/2
@app.route('/blog/eliminar/<int:id>', methods=['GET', 'POST'])
def eliminarItem(id):

	post = session.query(Blog).filter_by(id = id).one()
	# select * from blog where id=2
	if request.method == 'GET':
		return render_template('delete-post.html', username=login_session['username'], post = post)
	else:
		if request.method == 'POST':
			session.delete(post)
			# delete blog set id=2
			session.commit()
			return redirect(url_for('showMain'))

# Editar
# /blog/editar
@app.route('/blog/editar/<int:id>', methods=['GET', 'POST'])
def EditarItemRevie(id):
	if request.method == 'GET':

		post = session.query(Blog).filter_by(id = id).one()

	if request.method == 'GET':
		username = login_session['username']
		return render_template('Update-review.html', post = post,id = id, username=username)



	else:
		if request.method == 'POST':
			post = session.query(Blog).filter_by(id = id).one()
			post.titulo = request.form['titulo']
			post.contenido = request.form['contenido']
			session.commit()
			return redirect(url_for('showMain'))
					 
					 

# Crear Post
@app.route('/agregarPost', methods=['GET', 'POST'])
def agregarPost():

	if request.method == 'GET':
		if'username' in login_session:
			username = login_session['username']
			Autor = session.query(User).all()
			idautor = 0
			for user in Autor:
				if username == user.username:
					idautor=user.id
		return render_template('add-post.html', username=username, idau=idautor)
	else:
		if request.method == 'POST':
			post = Blog(
					titulo = request.form['titulo'],
					contenido=request.form['contenido'],
					fecha_creacion = datetime.datetime.now(),
					id_autor = request.form['autor'])
			session.add(post)
			session.commit()
			return redirect(url_for('showMain', username=login_session['username']))


# Crear Post
@app.route('/addpedidos', methods=['GET', 'POST'])
def addpedidos():

	if request.method == 'GET':
		if'username' in login_session:
			username = login_session['username']
			Autor = session.query(User).all()
			idautor = 0
			for user in Autor:
				if username == user.username:
					idautor=user.id
		return render_template('addpedidos.html', username=username, idau=idautor)
	else:
		if request.method == 'POST':
			post = cliente(
					medidas = request.form['medidas'],
					color = request.form['color'],
					cantidad = request.form['cantidad'],
					idpedido = request.form['autor'])
			session.add(post)
			session.commit()
			return redirect(url_for('showMain', username=login_session['username']))



# Show all
@app.route('/', methods=['GET'])
@app.route('/public/', methods=['GET'])
def showMain():
	#posts = session.query(Blog).all()
	posts = session.query(Blog,User).join(User, Blog.id_autor==User.id).all()
	# select * from blog
	
	if 'username' in login_session:
		username = login_session['username']
		return render_template('public.html', posts = posts, username=username)	
	else:
		return render_template('public.html', posts = posts)

if __name__ == '__main__':
	app.secret_key = "secret key"
	app.debug = True
	app.run(host = '0.0.0.0', port = 7000)
