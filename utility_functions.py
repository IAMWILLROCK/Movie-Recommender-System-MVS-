from pymongo import MongoClient
import numpy as np
from sklearn.metrics import pairwise
import pprint


client=MongoClient()

db=client.test 

users=db.users
movies=db.movies
md=db.matrix_db
rbm=db.ratings_by_movie
mi=db.movie_indexes
nm=db.normalized_matrix
sm=db.sparse_matrix


reverse_index=mi.find_one({'col':2})

index=reverse_index['reverse_index']



matrix=np.zeros((671,9084))
for i in range(0,671):
	matrix[i]=np.array(md.find_one({'userId':int(i+1)})['ratings'])
predicted_ratings=np.zeros(9084)

original_ratings=np.zeros(9084)

genres={'Comedy':0, 'Horror':0, 'Children':0, 'Action':0, 'Adventure':0, 'Film-Noir':0, 'Western':0, 'Drama':0, 'Fantasy':0, 'Crime':0, 'Romance':0, 'IMAX':0, 'Animation':0, 'Mystery':0, 'Documentary':0, 'Thriller':0, 'War':0, 'Musical':0, 'Sci-Fi':0}
genres_index={'Comedy':0, 'Horror':1, 'Children':2, 'Action':3, 'Adventure':4, 'Film-Noir':5, 'Western':6, 'Drama':7, 'Fantasy':8, 'Crime':9, 'Romance':10, 'IMAX':11, 'Animation':12, 'Mystery':13, 'Documentary':14, 'Thriller':15, 'War':16, 'Musical':17, 'Sci-Fi':18}
user_interests=[]


def GetUserData(username):
	user=users.find_one({'userId':username})
	global original_ratings
	global user_interests
	original_ratings=np.array(user['ratings'])
	user_interests=user['interests']
	return


def NumberMoviesRated(username):
	cnt=0
	for i in range(0,9084):
		if original_ratings[i]!=0:
			cnt=cnt+1
	return cnt

def GetUserInterests(username):
	return len(user_interests)

def UpdateUserInterests(username,l):
	global user_interests
	user_interests=l
	users.update_one({'userId':username},{'$set':{'interests':l}})
	return

def TopRated(limit):
	top_rated=movies.find().sort('avgRating',-1)
	i=0
	l=[]
	for movie in top_rated:
		if i==limit:
			break
		k=rbm.find_one({'movieId':str(movie['movieId'])})
		if len(k['ratings'].keys())>50:
			l.append(movie)
			i=i+1
	return l

def MoviesRated(username,limit):
	i=0
	l=[]
	user=users.find_one({'userId':str(username)})
	rating=user['ratings']
	no_rated=0
	for j in range(0,9084):
		if rating[j]!=0:
			no_rated=no_rated+1
	for j in range(0,9084):
		if i==limit:
			break
		if rating[j]!=0:
			movieId=index[str(j)]
			i=i+1
			k=movies.find_one({'movieId':int(movieId)})
			l.append(k)
	return no_rated,l

def MovieDetails(username,movieId):
	r=users.find_one({'userId':str(username)})
	ratings=r['ratings']
	r=mi.find_one({'col':1})
	index=r['index'][str(movieId)]
	movie=movies.find_one({'movieId':int(movieId)})
	#print(ratings[index])
	return ratings[index],movie

def RateMovie(username,movieId,rating):
	r=users.find_one({'userId':str(username)})
	ratings=r['ratings']
	r=mi.find_one({'col':1})
	index=r['index'][str(movieId)]
	ratings[index]=float(rating)
	#print(ratings[index])
	users.update_one({'userId':str(username)},{'$set':{'ratings':ratings}})
	return

def ClearRating(username,movieId):
	r=users.find_one({'userId':str(username)})
	ratings=r['ratings']
	r=mi.find_one({'col':1})
	index=r['index'][str(movieId)]
	ratings[index]=0
	users.update_one({'userId':str(username)},{'$set':{'ratings':ratings}})
	return

def GetMovies():
	l=[]	
	index=mi.find_one({'col':1})['index']
	for i in movies.find():	
		p=rbm.find_one({'movieId':str(i['movieId'])})
		if p!=None:
			if len(p['ratings'].keys())>=20:
				d=i
				d['predicted_rating']=predicted_ratings[index[str(i['movieId'])]]
				l.append(d)
	return l

def ExploreMovies(username,genre,d_type,sortby):
	mov=GetMovies()
	l=[]
	if genre=='All':
		l=mov
	else:
		for i in mov:
			if i['genres'][genre]==1:
				l.append(i)
	# print('l is ',l)
	k=[]
	if d_type=='All':
		for i in l:
			k.append(i) 
	else:
		index=mi.find_one({'col':1})['index']
		if d_type=='rated':
			for i in l:
				if original_ratings[index[str(i['movieId'])]]!=0:
					k.append(i)
		else:
			for i in l:
				if original_ratings[index[str(i['movieId'])]]==0:
					k.append(i)
	final=[]
	if sortby=='predicted_rating':
		final=sorted(k,key=lambda x:x['predicted_rating'],reverse=True)
	else:
		final=sorted(k,key=lambda x:x['avgRating'],reverse=True)
	# print('final is ',final)

	x=min(200,len(final))
	return final[0:x]

# ExploreMovies('NarenVamsi','Action','All','predicted_rating')


def MoviesbyInterest(username,limit):
	user=users.find_one({'userId':username})
	l=[]
	interests=user['interests']
	cnt=0
	for i in movies.find().sort('avgRating',-1):
		if cnt==limit:
			break
		k=rbm.find_one({'movieId':str(i['movieId'])})['ratings']
		if len(k)>=10:
			for j in interests:				
				if i['genres'][j]==1:
					cnt=cnt+1
					l.append(i)
					break
	return l

def ClearData(username):
	global predicted_ratings
	global user_interests
	user_interests=[]
	global original_ratings
	original_ratings=np.zeros(9084)
	predicted_ratings=np.zeros(9084)

def PredictRatings(username):
	user=users.find_one({'userId':username})
	l=[]
	k=[]
	ra=[]
	r=user['ratings']
	no_movies_rated=NumberMoviesRated(username)
	for i in range(0,len(r)):
		if r[i]!=0:
			k.append(i)
			ra.append(r[i])
			indexes=mi.find_one({'col':2})
			l.append(indexes['reverse_index'][str(i)])
	a=np.zeros((1,len(k)))
	b=np.zeros((671,len(k)))
	a[0]=ra
	for i in range(0,671):
		ra=[]
		for j in k:
			ra.append(matrix[i][j])
		b[i]=np.array(ra)
	similar_users=pairwise.cosine_similarity(a,b)
	most_similar=[]
	for i in range(0,671):
		most_similar.append([similar_users[0][i],i])
	most_similar.sort(key=lambda x: x[0],reverse=True)
	print(most_similar[0:10])
	for i in range(0,9084):
		r=0
		for j in range(0,10):
			user=most_similar[j][1]
			r=r+matrix[user][i]
		predicted_ratings[i]=r/10;
	print(predicted_ratings[0:10])
	return

def PredictRatings2(username):
	matrix=np.zeros((671,9084))
	for i in range(0,671):
		matrix[i]=np.array(nm.find_one({'userId':str(int(i+1))})['ratings'])
	user=users.find_one({'userId':username})
	a=np.zeros((1,9084))
	b=np.zeros((671,9084))
	b=matrix
	a[0]=np.array(user['ratings'])
	global predicted_ratings
	cnt=0
	r=0
	for i in range(0,9084):
		if a[0][i]!=0:
			r=r+a[0][i]
			cnt=cnt+1
	avg_user=r/cnt
	for i in range(0,9084):
		if a[0][i]!=0:
			a[0][i]=a[0][i]-avg_user
	
	# print(avg_user)
	similar_users=pairwise.cosine_similarity(a,b)
	most_similar=[]
	for i in range(0,671):
		most_similar.append([similar_users[0][i],i])
	most_similar.sort(key=lambda x: x[0],reverse=True)
	# print(most_similar[0:10])
	for i in range(0,9084):
		r=0
		cnt=0
		usr_cnt=0
		for j in range(0,45):			
			user=most_similar[j][1]
			if b[user][i]!=0:
				usr_cnt=usr_cnt+1
				cnt=cnt+most_similar[j][0]
				r=r+b[user][i]*most_similar[j][0]
		if cnt!=0 and usr_cnt>=15:
			predicted_ratings[i]=avg_user+r/cnt;
		else:
			predicted_ratings[i]=avg_user;
	k=predicted_ratings.copy()
	ma=k.max()
	mi=k.min()
	if ma>5:
		for i in range(0,9084):
			if k[i]>avg_user:
				k[i]=avg_user+((k[i]-avg_user)/(ma-avg_user))*(5-avg_user)
	if mi<0:
		for i in range(0,9084):
			if k[i]<avg_user:
				k[i]=avg_user-((avg_user-k[i])/(avg_user-mi))*(avg_user)
	predicted_ratings=k
	return



def PredictRatings3(username):
	matrix=np.zeros((671,9084))
	for i in range(0,671):
		matrix[i]=np.array(nm.find_one({'userId':str(int(i+1))})['ratings'])
	user=users.find_one({'userId':username})
	a=np.zeros((1,9084))
	b=np.zeros((671,9084))
	c=np.zeros((671,9084))
	for i in range(0,671):
		c[i]=np.array(sm.find_one({'userId':str(int(i+1))})['ratings'])
	b=matrix
	a[0]=np.array(user['ratings'])
	global predicted_ratings
	cnt=0
	r=0
	for i in range(0,9084):
		if a[0][i]!=0:
			r=r+a[0][i]
			cnt=cnt+1
	avg_user=r/cnt
	for i in range(0,9084):
		if a[0][i]!=0:
			a[0][i]=a[0][i]-avg_user
	
	# print(avg_user)
	similar_users=pairwise.cosine_similarity(a,b)
	most_similar=[]
	for i in range(0,671):
		most_similar.append([similar_users[0][i],i])
	most_similar.sort(key=lambda x: x[0],reverse=True)
	# print(most_similar[0:10])
	for i in range(0,9084):
		r=0
		cnt=0
		usr_cnt=0
		l=[]
		for j in range(0,45):			
			user=most_similar[j][1]
			if c[user][i]!=0:
				usr_cnt=usr_cnt+1
				l.append(np.mean(c[user][c[user]>0]))
				cnt=cnt+most_similar[j][0]
				r=r+c[user][i]*most_similar[j][0]
		if cnt!=0 and usr_cnt>=10:
			predicted_ratings[i]=np.mean(np.array(l))+r/cnt;
		else:
			predicted_ratings[i]=np.mean(np.array(l));


	# predicted_ratings=(predicted_ratings-predicted_ratings.min())/(predicted_ratings.max()-predicted_ratings.min())
	# print(predicted_ratings[0:100])
	return


def MoviesRecommended(username,limit):
	l=[]
	d=[]
	# user=users.find_one({'userId':username})
	for i in range(0,9084):
		l.append([predicted_ratings[i],i])
	k=sorted(l,key=lambda x: x[0],reverse=True)
	# print(k[0:10])
	j=0
	# original_ratings=user['ratings']
	# print(original_ratings[0:10])
	for i in range(0,9084):
		if j==limit:
			break
		if original_ratings[k[i][1]]==0:			
			reverse_index=mi.find_one({'col':2})['reverse_index']
			movieId=reverse_index[str(k[i][1])]
			p=rbm.find_one({'movieId':str(movieId)})
			if p!=None:
				if len(p['ratings'].keys())>=100:
					j=j+1
					movie=movies.find_one({'movieId':movieId})
					d.append(movie)
	return d



def GetPredictedRating(movieId):
	index=mi.find_one({'col':1})['index']
	return predicted_ratings[int(index[str(movieId)])]

def GetUserRatingInformation(username):
	user=users.find_one({'userId':username})
	ratings=user['ratings']
	index=mi.find_one({'col':2})['reverse_index']
	d={}
	genres={'Comedy':0, 'Horror':0, 'Children':0, 'Action':0, 'Adventure':0, 'Film-Noir':0, 'Western':0, 'Drama':0, 'Fantasy':0, 'Crime':0, 'Romance':0, 'IMAX':0, 'Animation':0, 'Mystery':0, 'Documentary':0, 'Thriller':0, 'War':0, 'Musical':0, 'Sci-Fi':0}
	rating_count={'0.5':0,'1.0':0,'1.5':0,'2.0':0,'2.5':0,'3.0':0,'3.5':0,'4.0':0,'4.5':0,'5.0':0}
	genre_count=genres.copy()
	genre_average=genres.copy()
	for i in range(0,9084):
		if ratings[i]!=0 and str(ratings[i]) in rating_count.keys():
			rating_count[str(ratings[i])]=rating_count[str(ratings[i])]+1
			movieId=index[str(i)]
			movie=movies.find_one({'movieId':movieId})
			movie_genre=movie['genres']
			for k in movie_genre.keys():
				if movie_genre[k]==1:
					genre_count[k]=genre_count[k]+1
					genre_average[k]=genre_average[k]+ratings[i]
	for k in movie_genre.keys():
		if genre_count[k]==0:
			genre_average[k]=0
		else:
			genre_average[k]=genre_average[k]/genre_count[k]
	d['rating_count']=rating_count
	# print(rating_count)
	d['genre_count']=genre_count
	# print(genre_count)
	d['genre_average']=genre_average
	# print(genre_average)
	return d

# PredictRatings('NarenVamsi')
# l=MoviesRecommended('NarenVamsi')


