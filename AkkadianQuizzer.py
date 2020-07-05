#!/usr/bin/env python3
import csv
import sys
import unicodedata
from bs4 import BeautifulSoup
import requests
import json
import os
import random

html_doc = """
<!DOCTYPE html>
<html>
<head>
<link rel="shortcut icon" href="{{ url_for('static', filename='icon.ico') }}">
<meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1, maximum-scale=1.0">
<style>

input {
-webkit-appearance: none;
-moz-appearance: none;
appearance: none;
font-size: 20px;
}

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
background-color: #112233;
min-width: fit-content;
}

div.base {
margin: 40px 10px;
}

#bottombar {
background-color: #112233;
padding: 20px 10px 10px 10px;

}

.nester {
margin: 10px 10px;
padding: 20px 5px 50px 5px;
text-align: center;
}

.button {
background-color: #008CBA;
border: none;
color: white;
padding: 10px 15px;
text-align: center;
text-decoration: none;
display: inline-block;
font-size: 14px;
border-radius: 5px;
}

#answerButton {
background-color: #f04d99;
border: none;
color: white;
padding: 10px 15px;
text-align: center;
float: center;
text-decoration: none;
font-size: 14px;
border-radius: 5px;
width: 200px;
}

#newButton {
background-color: #3de03d;
border: none;
color: white;
padding: 10px 15px;
text-align: center;
float: center;
text-decoration: none;
font-size: 14px;
border-radius: 5px;
}

.container {
    text-align: center;  
    margin: 10px;  
}

div.entry {
background-color: #eeeeee;
border-radius: 5px;
padding: 10px;
margin: 50px;
}

</style>
</head>

<body>  
    <h1>Random Word</h1>

<!--This is an example text that won't be displayed in the browser
    <form class="range" action = "http://snippy.hopto.org:54321/AKQuizTransition" method = "post">
    <p>Enter Word:</p>
    <p><input type = "text" name = "chapter" value="1" required/></p>
    <p><input type = "submit" value = "submit" class = "button"/></p>
    </form>
-->

    <div id = mainbody>

        <div id=bottombar></div>

    </div>

    <div id="insertionPoint"></div>

    <form action = "http://snippy.hopto.org:54321/AKRandomTransition" method = "post" class = "container">
    <button id="newButton" style="margin: 10px;" type="submit">
        new word from chapter
    </button>
    <input max="35" min="1" name="chapter" type="number" id="nextChapter" required/>
    </form>

</body>
</html>
"""

numlines = 1560



def simplify(word):
    newword = unicodedata.normalize('NFKD', word).encode('ascii','ignore').decode("ascii")
    return newword

def AKRand(chapter):
    outsoup = BeautifulSoup(html_doc, 'html.parser')
    with open('huehnergard.csv', newline='') as csvfile:
          reader = list(csv.DictReader(csvfile, delimiter='\t',  quotechar='⌾'))

          gotOne = False
          while not gotOne:
            randVal = random.randrange(numlines)
            row = reader[randVal]
            try:
                chapterNumber = int(float(row['chapter'].strip())) 
            except:
                chapterNumber = 36 #Impossible chapter number, preventing this entry from baing used
            if chapterNumber == int(float(chapter.strip())):
                gotOne = True

                entryTag = outsoup.new_tag("div",attrs={"class": "entry"})
                headTag = outsoup.new_tag("h2")
                defTag = outsoup.new_tag("p")
                headTag.string = row['word'] +  " | " + row['part'].replace("_", " ")
                entryTag.append(headTag)
                outsoup.find("div", id = "bottombar").insert_before(entryTag)
                
                
                define_HTML = """<p>TESTTEST</p><form class = "container" action = "http://snippy.hopto.org:54321/AKRandomDefinedTransition" method = "post">
                <button type="submit" id="answerButton">define term</button>
                <input type="hidden" name="row" id="rowVal"></form>"""

                defineTag = BeautifulSoup(define_HTML, 'html.parser')
                defineTag.find("input", id = "rowVal")['value'] = randVal
                outsoup.find("div", id = "insertionPoint").insert_before(defineTag)

                outsoup.find("input", id = "nextChapter")['value'] =  int(float(chapter.strip()))



	        
    return outsoup.prettify()


def AKAnswer(rowNum):
    outsoup = BeautifulSoup(html_doc, 'html.parser')
    with open('vocab.csv', newline='') as csvfile:
        reader = list(csv.DictReader(csvfile, delimiter='\t',  quotechar='⌾'))
        
        row = reader[int(rowNum)]
        entryTag = outsoup.new_tag("div",attrs={"class": "entry"})
        headTag = outsoup.new_tag("h2")
        defTag = outsoup.new_tag("p")
        defTag.string = row['definition']
        headTag.string = row['word'] +  " | " + row['part'].replace("_", " ")
        entryTag.append(headTag)
        entryTag.append(defTag)
        outsoup.find("div", id = "bottombar").insert_before(entryTag)

        outsoup.find("input", id = "nextChapter")['value'] = int(row['chapter'])

    return (outsoup.prettify())
