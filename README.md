# Movie-Recommender-System-MVS-

This is a complete website with the capability to provide meaning recommendations to a particular user basing on the Movies that he likes and the Movies that similar users like have watched.
The model uses Cosine Similarity to compute the similarity between two any users. So, whenever recommendations need to calculated the Cosine Similarity is calculated between
all the users and results are sorted in a decreasing order. The User with most similarity is in the top of the list. From that we start recommending the titles those users have
rated high.


## Built With
	Flask - Web Framework
	MongoDB - Database
  
## Getting Started
This was developed on Windows 10 and is not tested on other platforms.

### MongoDB

You must install MongoDB beforehand, this serves as the database. 
You can download from this link https://www.mongodb.com/dr/fastdl.mongodb.org/win32/mongodb-win32-x86_64-2008plus-ssl-3.6.2-signed.msi/download

To import database into your system, follow the below procedure.

1) The database is provided in the following link 
	https://drive.google.com/file/d/1ZLPvcu2zyESq9w8l5kwbkkGs1EUcNbRc/view?usp=sharing
 	Download and Extract it.
2) Open the Command Prompt. Change directory to mongodb/server/bin. For example in my system 
	cd C:\Program Files\MongoDB\Server\3.4\bin
3) Run "mongod.exe"
4) Open another Command Prompt without closing previous window.
5) Run "cd C:\Program Files\MongoDB\Server\3.4\bin"
6) Run the following command
	mongorestore -d test "~path to your test folder~\test"

	For example in my system
		mongorestore -d test C:\Users\Vamsi\Downloads\recoMe\test
7) The above command will import all the data into your system with database name test.


### Python Packages

You should have installed Python 3.x
You must have flask, flask-wtf, pymongo packages in your python libraries.
In windows, you can install through following in command prompt if you have pip installed in your system.

pip install flask

pip install flask-wtf

pip install pymongo
