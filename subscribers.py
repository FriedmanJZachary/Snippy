from flask import Flask, redirect, url_for, request, render_template
import MySQLdb
from lookupFunctions import lookup
from AkkadianReader import AKlookup
from AkkadianQuizzer import *
from BibleReader import *
from flask_mobility import Mobility
from flask_mobility.decorators import mobile_template
import config
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["10 per minute"],
)
Mobility(app)

#UNSUBSCRIPTION SERVICE #####################################################################

@app.route('/unsubscribePage')
def unsubscribePage():
      return render_template('unsubscribe.html')


@app.route('/unsubscribe', methods = ['POST', 'GET'])
def unsubscribe():
   if request.method == 'POST':
      user = request.form['nm'].lower().strip()
      return redirect(url_for('goodbye', name = user))
   else:
        return("ERROR: ILLEGITIMATE ACCESS")


@app.route('/goodbye/<name>')
def goodbye(name):
   print("NAME: " + name)

   mydb = MySQLdb.connect(
      host="localhost",
      user="servermanager",
      passwd="potato",
      db="emailusers"
   )

   mycursor = mydb.cursor()
   mycursor.execute("DELETE FROM user WHERE email = \'" + name + "\';")
   mydb.commit()
   myresult = mycursor.fetchall()
   
   return render_template('goodbye.html', name = name)


#SUBSCRIPTION SERVICE #######################################################################

@app.route('/subscribePage')
def subscribePage():
      return render_template('subscribe.html')


@app.route('/subscribe', methods = ['POST', 'GET'])
def subscribe():
   if request.method == 'POST':
      user = request.form['nm'].lower().strip()
      return redirect(url_for('welcome', name = user))
   else:
        return("ERROR: ILLEGITIMATE ACCESS")


@app.route('/welcome/<name>')
def welcome(name):
   print("NAME: " + name)

   mydb = MySQLdb.connect(
      host="localhost",
      user="servermanager",
      passwd="potato",
      db="emailusers"
   )

   mycursor = mydb.cursor()
   mycursor.execute("insert into user(email)  values (\"" + name + "\");")
   mydb.commit()
   myresult = mycursor.fetchall()

   return render_template('welcome.html', name = name)


#ACTIVE LOOKUP#########################################################

@app.route('/lookupPage')
def lookupPage():
   return render_template('lookup.html', site = config.site)


@app.route('/searchTransition', methods = ['POST', 'GET'])
def searchTransition():
   if request.method == 'POST':
      word = request.form['nm'].lower().strip()
      return redirect(url_for('searcher', word = word))
   else:
        return("ERROR: ILLEGITIMATE ACCESS")
         
@app.route('/searcher/<word>')
def searcher(word):
   try:
      result = lookup(word)
   except:
      result = render_template('error.html')
   return result


#HOMEPAGE##############################################################

@app.route('/home')
def home():
   if not request.MOBILE:
       result = render_template('home.html', site = config.site)
   else:
       result = render_template('mobileHome.html', site = config.site)
   return result

 
@app.route('/')
def goHome():
   return redirect(url_for('home'))

    
#AKKADIANLOOKUP########################################################

@app.route('/AKlookupPage')
def AKlookupPage():
   return render_template('AKlookup.html', site = config.site)


@app.route('/AKsearchTransition', methods = ['POST', 'GET'])
def AKsearchTransition():
   if request.method == 'POST':
      word = request.form['nm'].lower().strip()
      return redirect(url_for('AKsearcher', word = word))
   else:
        return("ERROR: ILLEGITIMATE ACCESS")
         
@app.route('/AKsearcher/<word>')
def AKsearcher(word):
   try:
      result = AKlookup(word)
   except:
      result = render_template('error.html')
   return result


#AKKADIANRANDOM########################################################

@app.route('/AKRandomHome')
def AKRandomHome():
   return render_template('randomHome.html', site = config.site)


@app.route('/AKRandomTransition', methods = ['POST', 'GET'])
def AKRandomTransition():
   if request.method == 'POST':
      chapter = request.form['chapter']
      return redirect(url_for('AKRandomUndefined', chapter = chapter))
   else:
        return("ERROR: ILLEGITIMATE ACCESS")
         
@app.route('/AKRandomUndefined/<chapter>')
def AKRandomUndefined(chapter):
   result = AKRand(chapter)
   return result


@app.route('/AKRandomDefinedTransition', methods = ['POST', 'GET'])
def AKRandomDefinedTransition():
   if request.method == 'POST':
      row = request.form['row']
      return redirect(url_for('AKRandomDefined', row = row))
   else:
        return("ERROR: ILLEGITIMATE ACCESS")

@app.route('/AKRandomDefined/<row>')
def AKRandomDefined(row):
   result = AKAnswer(row)
   return result


#BIBLELOOKUP########################################################


@app.route('/BibleSearchTransition', methods = ['POST', 'GET'])
def BibleSearchTransition():
   if request.method == 'POST':
      term = request.form['term'].strip()
      return redirect(url_for('BibleSearcher', term = term))
   else:
        return("ERROR: ILLEGITIMATE ACCESS")
         
@app.route('/BibleSearcher/<term>')
@limiter.limit("3 per minute")
def BibleSearcher(term):
   try:
      result = BibleLookup(term)
   except:
      result = render_template('error.html')
   return result

########################################################################

if __name__ == '__main__':
   app.run(debug = False)
