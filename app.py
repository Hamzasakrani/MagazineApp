from flask import Flask, render_template, url_for, request, session, redirect, flash
from flask_pymongo import PyMongo
import bcrypt
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'testing'

app.config['MONGO_dbname'] = 'magazineapp'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/magazineapp'

mongo = PyMongo(app)
@app.route("/")
def main():
    return render_template('home.html')

@app.route("/signup", methods=['POST'])
def signup():
    if request.method == 'POST':
        
        users = mongo.db.users
        signup_user = users.find_one({'email': request.form['email']})
        
        if signup_user:
            flash(request.form['email'] + ' email is already exist')
            return redirect(url_for('main'))

        hashed = generate_password_hash(request.form['password'])
        users.insert({'firstname': request.form['firstname'],'lastname': request.form['lastname'], 'password': hashed, 'email': request.form['email']})
        return redirect(url_for('main'))
       
      

@app.route('/signin', methods=['POST'])
def signin():
    if request.method == 'POST':
        users = mongo.db.users
        signin_user = users.find_one({'email': request.form['email']})

        if signin_user:
            
            if check_password_hash(signin_user["password"], request.form['password']):
                print(signin_user)
                session['firstname'] = signin_user['firstname']
                session['lastname'] = signin_user['lastname']
                session['email'] = signin_user['email']
                return redirect(url_for('dashboard'))

        flash('Username and password combination is wrong')
        return redirect(url_for('main'))
@app.route('/account', methods=['POST','GET'])
def account():
    if request.method == 'POST':
        magazines = mongo.db.users
        myquery = { "firstname": session['firstname'] ,"lastname": session['lastname']  ,"email": session['email']}
        newvalues = { "$set": { "firstname": request.form['firstname'] ,"lastname": request.form['lastname']  ,"email": request.form['email']}}
        magazines.update_one(myquery, newvalues)
        return redirect(url_for('main'))
    
    if 'firstname' in session:
       magazines = mongo.db.magazines
       mymagazine=magazines.find({'created_by': session['firstname']+" "+session['lastname']}) 
       return render_template('account.html',firstname=session['firstname'],lastname=session['lastname'],email=session['email'],mymagazine=mymagazine)   
    else:
       return redirect(url_for('main'))

@app.route('/new', methods=['POST','GET'])
def addMagazine():
    if request.method == 'POST':
        magazines = mongo.db.magazines
        magazines.insert({'title': request.form['title'],'description': request.form['description'],'created_by':session['firstname']+" "+session['lastname']})
        return redirect(url_for('dashboard'))
    if 'firstname' in session:
       return render_template('new.html')
    else:
       return redirect(url_for('main'))        

@app.route('/show/<id>', methods=['GET'])
def showMagazine(id):
    id=ObjectId(id)
    magazines = mongo.db.magazines
    magazineDetails=magazines.find({'_id': id})
    if 'firstname' in session:
       return render_template('show.html',magazineDetails=magazineDetails[0])  
    else:
       return redirect(url_for('main'))  

@app.route('/dashboard', methods=['GET'])
def dashboard():
   
    magazines = mongo.db.magazines
    allmagazine=magazines.find()
    if 'firstname' in session:
       return render_template('dashboard.html',magazines=allmagazine,name=session['firstname']+" "+session['lastname'])    
    else:
       return redirect(url_for('main'))


@app.route('/logout')
def logout():
    session.pop('firstname', None)
    session.pop('lastname', None)
    session.pop('email', None)
    return redirect(url_for('main'))



if __name__ == "__main__":
    app.run(debug=True)
    app.run()    