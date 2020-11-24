#!/usr/bin/env python3

#In honor of 'Dave' Do Hyung Kwon, may the glory of his saintly presence remain an eternal blessing
#In honor of Allen Ravitsky, for every Saint needs a Satan

from bs4 import BeautifulSoup
import requests
import smtplib, ssl
from email.mime.text import MIMEText as text
from unidecode import unidecode
import json
import os
import re
import MySQLdb



def getQuote(definition):
    for d in definition:
        for e in d:
            for a in d[e]:
                for b in a:
                    for c in b:
                        if type(c) is dict:
                            if 'dt' in c:
                                for l in c['dt']:
                                    if 'vis' in l:
                                        line = l[1][0]['t']
                                        return "\"" + re.sub("({...|})", "", line) + "\""
    return

html_doc = """
<!DOCTYPE html>
<html>
<head>
   <style>
      
      h1 {
         color: #eeeeee;
         text-align: center;
         font-family: Helvetica;
         padding: 20px 0px;
         background-color: #112233;
         /*width: 100%;*/
      }
      

      h2 {
         color: #112233;
         text-align: left;
         font-family: Helvetica;
      }

      p {
         color: #112233;
         font-family: Helvetica;
         margin: 10px 0px;
         padding: 0px;
      }

      p.understated {
         color: #dddddd;
         font-family: Helvetica;
         font-size: 12px;
         margin: -10px 0px;
         padding: 0px;
         text-align: center;
      }

      a.understated {
         color: #dddddd;
         font-family: Helvetica;
         font-size: 14px;
         margin: -10px 0px;
         padding: 10px;
      }
      
      body {
         background-color: #eeeeee;
         min-width: fit-content;
      }
      
      div.base {
         margin: 40px 10px;
      }
      
      #bottombar {
         background-color: #112233;
         padding: 20px 10px 10px 10px;
     
      }

      #quote{
        margin: 30px 0px;
      }

      .nester {
        margin: 10px 10px;
        padding: 20px 5px 50px 5px;
		text-align: center;
      }
      

   </style>
</head>

<body>  

<div id = mainbody>
  <div class = base id = definition>
      <h2 id = beginDef>Definition:</h2>
      <div id = endDef></div>
  </div>

<div id = bottombar>
   <p class = understated>This email is part of a mailing list. If you would like to be removed from it or wish to utilize other Snippy services, please use the following links:</p>
   
   <div class = nester>
      <a class = understated href="http://snippythelobster.com/unsubscribePage">unsubscribe</a>
      <a class = understated href="http://snippythelobster.com/home">website</a>
   </div>
</div>

</body>
</html>
"""

outsoup = BeautifulSoup(html_doc, 'html.parser')

#Get Word ____________________________________________________________________

word = ''
with open("/home/pi/Desktop/WOTD/wordList.txt", "r") as f:
    word = f.readline()
    lines = f.readlines()
with open("/home/pi/Desktop/WOTD/wordList.txt", "w") as f:
    for line in lines:
          f.write(line)

word = word.strip().lower()

titleTag = outsoup.new_tag("h1")
titleTag.string = word.capitalize()
outsoup.find("div", id = "mainbody").insert_before(titleTag)

wordLog = "/home/pi/Desktop/WOTD/wordLog.txt"
if os.path.exists(wordLog):
    append_write = 'a' # append if already exists
else:
    append_write = 'w' # make a new file if not

log = open(wordLog, append_write)
log.write(word + "\n")
log.close()

#Definitions ___________________________________________________________________

key = "c51bab48-9a2e-4132-b5af-dbb82090c10a"

#Get word data from MW
urlfrmt = "https://dictionaryapi.com/api/v3/references/collegiate/json/" + word + "?key=" + key
response = requests.get(urlfrmt).text
jsStruct = json.loads(response)

#Get first definition listed
meaning = jsStruct[0]
definitions = meaning['shortdef']
part = meaning['fl']

#Make title bar display part of speech
outsoup.find("h2", id = "beginDef").string = "Definition " + "(" + meaning['fl'] + "):"

#Add definitions
for definition in definitions:
    defTag = outsoup.new_tag("p")
    defTag.string = "• " + definition
    outsoup.find("div", id = "endDef").insert_before(defTag)

#If present, insert quote
if getQuote(meaning['def']):
  quoteTag = outsoup.new_tag('p', id='quote')
  quoteTag.string = getQuote(meaning['def'])
  outsoup.find("div", id = "endDef").insert_before(quoteTag)

#IPA Lookup __________________________________________________________________

logfile = open('/home/pi/Desktop/WOTD/ipa.txt', 'r')
loglist = logfile.readlines()
logfile.close()

for line in loglist:
    if line.startswith(word + "\t"):
        pronunciation = line.split("/")[1].strip()

        #Add in pronunciation, if applicable
        proTag = BeautifulSoup("<div class = base ipa><h2 id = beginPro>Pronunciation:</h2></div>", 'html.parser')
        proPar = outsoup.new_tag("p")
        proPar.string = pronunciation
        proTag.find("h2").insert_after(proPar)
        outsoup.find("div", id = "bottombar").insert_before(proTag)
        break


#ETYMOLOGY _____________________________________________________________________

link = "https://www.etymonline.com/word/" + word
data = requests.get(link).text
soup = BeautifulSoup(data, features="html.parser")
div_container = soup.find_all("div", {"class": "word--C9UPa"})

if div_container:
    etymTag = BeautifulSoup("<div class = base etymology><h2 id = beginEtym>Etymology:</h2><div class = etymEnd></div></div>", 'html.parser')
    etymEnd = etymTag.find("div", {"class": "etymEnd"})
    for container in div_container:  #For each block containing a word form and etymology
        for body in container.find_all(attrs={"word__defination--2q7ZH"}): #Find all body sections (that contain the actual etymologies)
            #Add in etymology, if applicable

            for paragraph in body.find_all("p"):
                etymPar = soup.new_tag("p")
                etymPar.string = paragraph.text
                etymEnd.insert_before(etymPar)

            outsoup.find("div", id = "bottombar").insert_before(etymTag)


text_file = open("output.html", "w")
text_file.write(outsoup.prettify())
text_file.close()


# DATABASE USER RETRIEVAL ______________________________________________________

mydb = MySQLdb.connect(
  host="localhost",
  user="servermanager",
  passwd="potato",
  db="emailusers"
)

mycursor = mydb.cursor()
mycursor.execute("SELECT email FROM user")
myresult = mycursor.fetchall()

receiver_emails = []
for email in myresult:
	receiver_emails.append(str(email)[2:-3])



#EMAIL _________________________________________________________________________

port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "snippythelobster@gmail.com"
password = "beautifulsoup"


context = ssl.create_default_context()
with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)

    m = text(outsoup.prettify(), 'html')
    m['Subject'] = "Word of the Day | " + word.title()
    m['From'] = "Snippy The Lobster"
    m['To'] = "Snippy's Friends"
    server.sendmail(sender_email, receiver_emails, m.as_string())

