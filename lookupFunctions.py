#!/usr/bin/env python3

#In honor of 'Dave' Do Hyung Kwon, may the glory of his saintly presence remain an eternal blessing
#In honor of Allen Ravitsky, for every Saint needs a Satan

from bs4 import BeautifulSoup
import requests
import smtplib, ssl
from unidecode import unidecode
import json
import os
import re
import config

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

def lookup(word):

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
        
        .home{
    	    text-align: center;
        }

        #homebutton{
    	    background-color: #f04d99;
        }
        
    </style>
    </head>
    <body>  
        <form action = "/searchTransition" method = "post">
            <p>Enter Word:</p>
            <p><input type = "text" name = "nm" required/></p>
            <p><input type = "submit" value = "submit" class = "button"/></p>
        </form>
        
        <form class = "home" action = "" method = "get">
	    <p><input id = homebutton type = "submit" value = "return to home" class = "button home"/></p>
        </form>
    
        <div id = mainbody>
        <div class = base id = definition>
            <h2 id = beginDef>Definition:</h2>
            <div id = endDef></div>
        </div>
        <div id = bottombar>
        </div>
    </body>
    </html>
    """

    outsoup = BeautifulSoup(html_doc, 'html.parser')

    word = word.strip().lower()
    titleTag = outsoup.new_tag("h1")
    titleTag.string = word.capitalize()
    outsoup.find("div", id = "mainbody").insert_before(titleTag)


    #Definitions ___________________________________________________________________

    key = "c51bab48-9a2e-4132-b5af-dbb82090c10a"

    #Get word data from MW
    urlfrmt = "https://dictionaryapi.com/api/v3/references/collegiate/json/" + word + "?key=" + key
    response = requests.get(urlfrmt).text
    jsStruct = json.loads(response)

    #Get first definition listed
    meaning = jsStruct[0]
    definitions = meaning['shortdef']

    #Show part of speech in Definition title
    outsoup.find("h2", id = "beginDef").string = "Definition " + "(" + meaning['fl'] + "):"

    #Insert all definitions
    for definition in definitions:
        defTag = outsoup.new_tag('p')
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
    forms = outsoup.find_all("form")
    for form in forms:
        form['action'] = "http://" + config.site + form['action']

    return outsoup.prettify()
