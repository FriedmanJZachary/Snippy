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
import MySQLdb

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
         padding: 0px;
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
         padding: 20px 10px 50px 10px;
     
      }

      .nester {
        margin: 0px 30px;
         padding: 50px 5px 0px 5px;
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
   <p class = understated>This email is part of a mailing list. If you would like to be removed from it or wish to subscribe another email address, please use one of the following links:</p>
 

   <div class = nester>
      <a class = understated style="float: left;" href="http://snippy.hopto.org:54321/unsubscribePage">unsubscribe</a>
      <a class = understated style="float: right;" href="http://snippy.hopto.org:54321/subscribePage">subscribe new</a>
   </div>

</div>
</body>
</html>
"""

outsoup = BeautifulSoup(html_doc, 'html.parser')

#Get Word ____________________________________________________________________

word = 'orange'

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

for definition in definitions:
    defTag = outsoup.new_tag("p")
    defTag.string = "• " + definition
    outsoup.find("div", id = "endDef").insert_before(defTag)

#IPA Lookup __________________________________________________________________

logfile = open('/home/pi/Desktop/WOTD/ipa.txt', 'r')
loglist = logfile.readlines()
logfile.close()

for line in loglist:
    if line.startswith(word):
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

receiver_emails = []

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
