#!/usr/bin/env python3
import csv
import sys
import unicodedata
from bs4 import BeautifulSoup
import requests
import json
import os
import config

def simplify(word):
    newword = unicodedata.normalize('NFKD', word).encode('ascii','ignore').decode("ascii")
    return newword

def AKlookup(word):
    html_doc = """
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, user-scalable=no, initial-scale=1, maximum-scale=1.0">
<link rel="shortcut icon" href="{{ url_for('static', filename='icon.ico') }}">
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
    
    div.entry {
    background-color: #eeeeee;
    border-radius: 5px;
    padding: 10px;
    margin: 40px;
    }
    
    .home{
    	text-align: center;
    }

    #homebutton{
    	background-color: #f04d99;
    }
    

    </style>
    </head>

    <body>  

    <form action = "/AKsearchTransition" method = "post">
        <p><input type = "text" name = "nm" required/></p>
        <p><input type = "submit" value = "submit" class = "button"/></p>
    </form>
    
    <form class = "home" action = "" method = "get">
	<p><input id = homebutton type = "submit" value = "return to home" class = "button home"/></p>
    </form>

    <div id = mainbody>

    <div id = bottombar>
    </div>

    </body>
    </html>
    """

    outsoup = BeautifulSoup(html_doc, 'html.parser')
    with open('vocab.csv', newline='') as csvfile:
          reader = csv.DictReader(csvfile, delimiter='	',  quotechar='⌾')
          for row in reader:
               if simplify(row['word']).startswith(simplify(word)):
                   print("\n")
                   print(row['word'], "|", row['part'], "\n", row['definition'].strip())

                   entryTag = outsoup.new_tag("div",attrs={"class": "entry"})
                   headTag = outsoup.new_tag("h2")
                   defTag = outsoup.new_tag("p")
                   headTag.string = row['word'] +  " | " + row['part'].replace("_", " ") + " (" + row['author'].capitalize() + ")"
                   defTag.string = row['definition'].strip()

                   entryTag.append(headTag)
                   entryTag.append(defTag)
                   outsoup.find("div", id = "bottombar").insert_before(entryTag)

    forms = outsoup.find_all("form")
    for form in forms:
        form['action'] = "http://" + config.site + form['action']

    return outsoup.prettify()
