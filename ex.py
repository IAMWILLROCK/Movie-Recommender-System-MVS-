from flask import Flask, render_template,url_for,request,session,render_template,abort,redirect,json,jsonify,abort
from login_form import PasswordCheck,LoginForm,RegisterForm,RegisterCheck
from utility_functions import TopRated,MoviesRated,GetUserData,GetUserRatingInformation,UpdateUserInterests,PredictRatings3,PredictRatings2,ClearData,MoviesbyInterest,GetUserInterests,NumberMoviesRated,MovieDetails,RateMovie,ClearRating,ExploreMovies,PredictRatings,MoviesRecommended,GetPredictedRating
from pymongo import MongoClient
import numpy as np
import pprint

client=MongoClient()

db=client.test 

users=db.users
movies=db.movies

genres={'Comedy':0, 'Horror':0, 'Children':0, 'Action':0, 'Adventure':0, 'Film-Noir':0, 'Western':0, 'Drama':0, 'Fantasy':0, 'Crime':0, 'Romance':0, 'IMAX':0, 'Animation':0, 'Mystery':0, 'Documentary':0, 'Thriller':0, 'War':0, 'Musical':0, 'Sci-Fi':0}

l=[]
i=0
for k in movies.find():
	data={}
	data['movieName']=k['movieName']
	data['imgLink']=k['imgLink']
	data['moviePage']='/movie/'+str(k['movieId'])
	l.append(data)


app = Flask(__name__)

app.secret_key='any random string'

@app.route("/")
def index():
	if 'username' in session and session['username']!='':
		return redirect(url_for('userHome'))
	return render_template("site2/index.html")

@app.after_request
def add_header(response):
    # response.cache_control.no_store = True
    if 'Cache-Control' not in response.headers:
        response.headers['Cache-Control'] = 'no-store'
    return response

@app.route("/login/check",methods=['POST','GET'])
def loginCheck():
	form=LoginForm()
	if 'username' in session and session['username']!='':
		return redirect(url_for('userHome'))
	if request.method=='POST':
		if form.validate()==True:
			password_check=PasswordCheck(request.form['user'],request.form['password'])
			if password_check==1:
				session['username']=request.form['user']
				GetUserData(session['username'])				
				return redirect(url_for('userHome'))
			else:
				return render_template('site2/login.html',form=form,errors=1)
		else:
			return render_template('site2/login.html',form=form,errors=0)
	else:
		return render_template("site2/login.html",form=form,errors=0)

@app.route("/userhome")
def userHome():
	if 'username' in session and session['username']!='':
		GetUserData(session['username'])
		k=NumberMoviesRated(session['username'])
		m=GetUserInterests(session['username'])
		print('m is ',m)

		if k!=0 or m!=0:
			name=session['username']
			if k>=15:
				PredictRatings2(name)
			l=TopRated(8)
			k,p=MoviesRated(name,8)
			if k>=15:
				m=MoviesRecommended(name,8)
			else:
				m=MoviesbyInterest(name,8)
			return render_template("site2/userhome.html",name=session['username'],no_movies_rated=NumberMoviesRated(session['username']),top_rated=l,number_movies_rated=k,movies_rated=p,movies_recommended=m)
		else:
			return redirect(url_for('interestedGenre'))

	return redirect(url_for('login'))

@app.route('/interestedGenre')
def interestedGenre():
	if 'username' in session and session['username']!='':
		k=NumberMoviesRated(session['username'])
		m=GetUserInterests(session['username'])
		if m==0:
			return render_template('site2/userinterests.html')
		else:
			return redirect(url_for('userHome'))
	else:
		return redirect(url_for('login'))

@app.route('/getInterestedGenre',methods=['GET'])
def GetInterestedGenre():
	if 'username' in session and session['username']!='':
		k=NumberMoviesRated(session['username'])
		if k==0:
			if request.args.get('genre')==None:
				return redirect(url_for('interestedGenre'))
			l=request.args.getlist('genre')
			UpdateUserInterests(session['username'],l)
			return redirect(url_for('userHome'))
		else:
			return redirect(url_for('userHome'))
	else:
		return redirect(url_for('login'))
	
@app.route("/login")
def login():
	if 'username' in session and session['username']!='':
		name=session['username']
		return redirect(url_for("userHome"))
	form=LoginForm()
	return render_template("site2/login.html",form=form,errors=0)

@app.route("/logout")
def logout():
	ClearData('username')
	session.pop('username',None)
	session.clear()
	return redirect(url_for('index'))

@app.route("/register")
def register():
	if 'username' in session and session['username']!='':
		name=session['username']
		return redirect(url_for("userHome"))
	form=RegisterForm()
	return render_template("site2/register.html",form=form,errors=0)

@app.route("/register/check",methods=['POST','GET'])
def registerCheck():
	form=RegisterForm()
	
	if 'username' in session and session['username']!='':
		return redirect(url_for('userHome'))
	
	if request.method=='POST':
		if form.validate()==True:
			registration_check=RegisterCheck(request.form)
			if registration_check==1:
				session['username']=request.form['user_name']
				return redirect(url_for('userHome'))
			else:
				return render_template('site2/register.html',form=form,errors=1)
		else:
			return render_template('site2/register.html',form=form,errors=0)		
	else:
		return render_template("site2/register.html",form=form,errors=0) 

@app.route("/movie/<movieId>")
def moviePage(movieId):
	if 'username' not in session or session['username']=='':
		return redirect(url_for('index'))
	if movieId=='search':
		return redirect(url_for('Search'))
	rated_flag,movie_details=MovieDetails(session['username'],movieId)
	predictedRating=GetPredictedRating(movieId)
	return render_template("site2/movie.html",name=session['username'],no_movies_rated=NumberMoviesRated(session['username']),rated_flag=rated_flag,movie_details=movie_details,predicted_rating=predictedRating)

@app.route("/rate/<movieId>",methods=['POST','GET'])
def rateMovie(movieId):
	if 'username' not in session or session['username']=='':
		return redirect(url_for('index'))
	if request.method=='POST':
		RateMovie(session['username'],movieId,request.form['Rating'])
		
		return redirect(url_for('moviePage',movieId=movieId))
	else:
		return redirect(url_for('moviePage',movieId=movieId))

@app.route("/clear/<movieId>",methods=['POST','GET'])
def clearRating(movieId):
	if 'username' not in session or session['username']=='':
		return redirect(url_for('index'))
	if request.method=='POST':
		ClearRating(session['username'],movieId)
		
		return redirect(url_for('moviePage',movieId=movieId))
	else:
		return redirect(url_for('moviePage',movieId=movieId))

@app.route("/livesearch")
def LiveSearch():
	return render_template('livesearchbar.html')

@app.route("/movie/search/movies")
def Search():
	
	return jsonify(l)

@app.route("/explore",methods=['GET'])
def exploreMovies():
	if 'username' not in session or session['username']=='':
		return redirect(url_for('index'))
	if request.args.get('genre')==None:
		genre='All'
	else:
		genre=request.args.get('genre')
	if request.args.get('sortby')==None:
		sortby='predicted_rating'
	else :
		sortby=request.args.get('sortby')
	if request.args.get('d_type')==None:
		d_type='All'
	else:
		d_type=request.args.get('d_type')
	genres_list=['Comedy', 'Horror', 'Children', 'Action', 'Adventure', 'Film-Noir', 'Western', 'Drama', 'Fantasy', 'Crime', 'Romance', 'IMAX', 'Animation', 'Mystery', 'Documentary', 'Thriller', 'War', 'Musical', 'Sci-Fi','All']
	d_type_list=['rated','not rated','All']
	sortby_list=['predicted_rating','avg_rating']
	print('genre ',genre,'sortby ',sortby,'d_type ',d_type)
	if genre not in genres_list or sortby not in sortby_list or d_type not in d_type_list:
		return abort(404);
	else:

		movies=ExploreMovies(session['username'],genre,d_type,sortby)
		return render_template("site2/explore.html",movies=movies,name=session['username'],no_movies_rated=NumberMoviesRated(session['username']))

@app.route('/userratinginformation')
def userRatingInformation():
	if 'username' not in session or session['username']=='':
		return redirect(url_for('index'))
	no_movies_rated=NumberMoviesRated(session['username'])
	if(no_movies_rated>0):
		d=GetUserRatingInformation(session['username'])
	else:
		d={}
	# print(d['genre_count'])
	return render_template("site2/userinformation.html",d=d,name=session['username'],no_movies_rated=NumberMoviesRated(session['username']))

@app.route('/header')
def Header():
	return render_template('site/header2.html')

if __name__ == '__main__':
   app.run(debug=True)