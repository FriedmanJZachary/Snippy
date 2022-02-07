#!/usr/bin/env python3

#In honor of 'Dave' Do Hyung Kwon, may the glory of his saintly presence remain an eternal blessing
#In honor of Allen Ravitsky, for every Saint needs a Satan

from bs4 import BeautifulSoup
import requests
import smtplib, ssl
from email.mime.text import MIMEText as text
from unidecode import unidecode
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
      

   </style>
</head>

<body>  

<div id = mainbody>
  <div class = base id = definition>
      <h2 id = beginDef>Definition:</h2>
      <div id = endDef></div>
  </div>

<div id = bottombar>
   <p class = understated>This email is part of a mailing list. If you would like to be removed from it or wish to subscribe another email address, please send a request to snippythelobster@gmail.com</p>

</div>
</body>
</html>
"""

outsoup = BeautifulSoup(html_doc, 'html.parser')

#OLD LINK _______________________________________________________________________

link = "https://www.nytimes.com/column/learning-word-of-the-day" #Get the link for today's word from the general WOTD page
data = requests.get(link).text
soup = BeautifulSoup(data, features="html.parser")
mydivs = soup.findAll("div", {"class": "css-1l4spti"})
 
for a in mydivs[0].find_all('a', href=True):
    ext = a['href']

#NEW LINK _______________________________________________________________________

newlink = "https://www.nytimes.com/" + ext
newdata = requests.get(newlink).text
newsoup = BeautifulSoup(newdata, features="html.parser")

div_container = newsoup.find('div', class_='css-1fanzo5 StoryBodyCompanionColumn')

for tag in div_container.find_all('h2'): #Line containing the word & part of speech
    ripped = tag.text

headLine = ripped.split("\\")
word = headLine[0].strip()
part = headLine[2].strip()


#Add in the word as a header
mainbody = outsoup.find("div", id ="mainbody")
tag = outsoup.new_tag("h1")
tag.string = word.capitalize()
mainbody.insert_before(tag)


#IPA Lookup __________________________________________________________________

msg = word.title() + "\n\nPart of Speech:\n" + part #The message that will eventaually be sent as the email body. This will be gradually added to as the program progresses

logfile = open('/home/pi/Desktop/WOTD/ipa.txt', 'r')
loglist = logfile.readlines()
logfile.close()

for line in loglist:
    if str(word) in line:
        pronunciation = line.split("/")[1].strip()

        #Add in pronunciation, if applicable
        proTag = BeautifulSoup("<div class = base ipa><h2 id = beginPro>Pronunciation:</h2></div>", 'html.parser')
        proPar = outsoup.new_tag("p")
        proPar.string = pronunciation
        proTag.find("h2").insert_after(proPar)
        outsoup.find("div", id = "bottombar").insert_before(proTag)
        break

#Definitions ___________________________________________________________________

for tag in div_container.find_all('p'):  
    if tag.text[0].isdigit() or ":" in tag.text[0:15]:
        defTag = outsoup.new_tag("p")
        defTag.string = tag.text
        outsoup.find("div", id = "endDef").insert_before(defTag)

#ETYMOLOGY _____________________________________________________________________

link = "https://www.etymonline.com/word/" + unidecode(word)
data = requests.get(link).text
soup = BeautifulSoup(data, features="html.parser")
div_container = soup.find_all("div", {"class": "word--C9UPa"})

if div_container:
    for container in div_container:  #For each block containing a word form and etymology
        for tag in container.find_all(attrs={"class": "word__name--TTbAA"}): #For all word form titles
            #msg = msg + "\n" + tag.text + "\n"
            break

        for body in container.find_all(attrs={"word__defination--2q7ZH"}): #Find all body sections (that contain the actual etymologies)
            #Add in etymology, if applicable
            etymTag = BeautifulSoup("<div class = base etymology><h2 id = beginEtym>Etymology:</h2><div class = etymEnd></div></div>", 'html.parser')
            etymEnd = etymTag.find("div", {"class": "etymEnd"})

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

#print(outsoup.prettify())

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

