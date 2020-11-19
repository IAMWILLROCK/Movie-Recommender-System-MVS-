from flask_wtf import Form
from wtforms import TextField, IntegerField, TextAreaField, SubmitField, RadioField,PasswordField, SelectField

from wtforms import validators, ValidationError
from wtforms.fields.html5 import EmailField

from pymongo import MongoClient
import numpy as np

client=MongoClient()

db=client.test 

users=db.users



class LoginForm(Form):
   user = TextField("UserName",[validators.Required("User Name is required")])
   password=PasswordField("Password",[validators.Required("Password is required")])
   submit = SubmitField("Login")

class RegisterForm(Form):
   first_name = TextField("First Name",[validators.Required("Please enter your first name.")])

   last_name=TextField("Last Name",[validators.Required("Please enter your last name.")])

   user_name=TextField("User Handle",[validators.Required("Please enter your user handle.")])

   confirm_password=PasswordField("Confirm Password",[validators.InputRequired()])
   
   password=PasswordField("Password",[validators.InputRequired(),validators.Length(min=8),validators.EqualTo('confirm_password',message="Passwords must match")])   
   
   email = EmailField("Email",[validators.Required("Please enter your email address."),validators.Email("Address is not in Email Format.")])
   
   submit = SubmitField("Register")

def PasswordCheck(name,password):
   k=users.find_one({'userId':str(name)})
   if k==None:
      return 0
   if k['password']==str(password):
      return 1
   else:
      return 0

def RegisterCheck(form):
   userId=form['user_name']
   k=users.find_one({'userId':str(userId)})
   if k!=None:
      return 0
   d={}
   d['first_name']=str(form['first_name'])
   d['last_name']=str(form['last_name'])
   d['userId']=str(form['user_name'])
   d['password']=str(form['password'])
   d['email']=str(form['email'])
   d['interests']=[]
   r=np.zeros(9084)
   d['ratings']=list(r)
   users.insert_one(d)
   return 1
