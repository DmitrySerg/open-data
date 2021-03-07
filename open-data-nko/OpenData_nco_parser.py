# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 23:35:34 2017

@author: dmitrys
"""

####################
#### НКО парсер ####
####################


import sys
sys.path.append('/Users/dmitrys/anaconda2/lib/python2.7/site-packages')
import re
from bs4 import BeautifulSoup
import time
import pandas as pd
from urllib.request import Request, urlopen
import requests
from user_agent import generate_user_agent
import numpy as np


main_url = "http://ivsezaodnogo.ru/foundations?search_by=name&page={}"
sub_url = "http://ivsezaodnogo.ru/foundations/{}"
img_url = "http://ivsezaodnogo.ru/uploads/foundation/logo/{}/thumb_profilepic.jpg"


FINAL = pd.DataFrame(columns=["name",
                             "address",
                             "longtitude",
                             "latitude",
                             "telephone",
                             "email",
                             "website",
                             "problems_solving", 
                             "audience", 
                             "description"])



def html_stripper(text):
    return re.sub('<[^<]+?>', '', str(text))
    

def getUrls(page):
    req = Request(main_url.format(page), headers={'User-Agent': generate_user_agent()})
    webpage = urlopen(req).read()
    soup = BeautifulSoup(webpage, "lxml")
    urls_block = soup.find('div', attrs={'class':'js-lazy-loader b-foundations-list'}).findAll('a', attrs={'class':'link'})
    nko_urls = re.findall(r'\d+', str(urls_block))
    return nko_urls
    

def getPage(page):
    req = Request(sub_url.format(page), headers={'User-Agent': generate_user_agent()})
    webpage = urlopen(req).read()
    soup = BeautifulSoup(webpage, "lxml")
    return soup
                

def getInformation(page):
    #### Organization name
    organization_name = html_stripper(page.find("h1"))
    
    information = page.find("div", attrs={'class':'groups'})
    information = re.split("Решает проблемы|Кому оказывается помощь", str(information))
    
    #### Problems
    problems_solving = html_stripper(information[1]).split('\n')
    problems_solving = [x for x in problems_solving if x] # удаляем пустые значения
    problems_solving = list(set(problems_solving)) # удаляем дубликаты
    problems_solving.remove("показать все")
    problems_solving.remove('свернуть ↑')
    
    #### Target audience
    audience = html_stripper(information[2]).split('\n')
    audience = [x for x in audience if x]
    
    #### Description
    description = html_stripper(page.find("div", attrs={"class":"description"}))
    
    return {'name':organization_name, 
            'problems_solving':problems_solving, 
            'audience':audience, 
            'description':description}


def getCoordinatesFromYandex(yandex_url):
    try:
        req = Request(yandex_url, headers={'User-Agent': generate_user_agent()})
        webpage = urlopen(req).read()
        soup = BeautifulSoup(webpage, "lxml")
        soup.find("div", attrs={"class":"toponym-card-view__coordinates-deg"})
        coordinates = re.split("coordinates", str(soup))[-2]
        coordinates = re.findall(r'\d+[\.]?\d*', coordinates)[0:2]
    except:
        coordinates=[np.NaN, np.NaN]
    return coordinates


def getContacts(page):
    contacts = page.find("div", attrs={"class":"contacts js-donate-block"})
    yandex_url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', str(contacts))[0]
    
    longtitude, latitude = getCoordinatesFromYandex(yandex_url)
    
    address = html_stripper(contacts.find("a",attrs={'class':"info-line address"}))
    telephone = html_stripper(contacts.find("div", attrs={"class":"info-line phone"}))
    email = html_stripper(contacts.find("div", attrs={"class":"info-line email"}))
    website = html_stripper(contacts.find("div", attrs={"class":"info-line web"}))
    return {'longtitude':float(longtitude),
            "latitude":float(latitude), 
            'address':address, 
            'telephone':telephone, 
            'email':email, 
            'website':website}



def getImage(number):
    img_data = requests.get(img_url.format(number)).content
    if len(img_data)!=0:
        with open('/Users/dmitrys/Desktop/DataProjects/OpenDataNKO/images/nko_img_{}.jpg'.format(number), 'wb') as handler:
            handler.write(img_data)


def getAllUrls(last_page=50):
    nko_urls = set()
    
    for i in range(1,last_page):
        urls = getUrls(i)
        time.sleep(0.3)
        if len(urls)!=0:
            nko_urls.update(urls)
        else:
            break
    nko_urls = list(nko_urls)
    return nko_urls
    

print("Collecting all urls")
nko_urls = getAllUrls()


start = time.time()
for number in nko_urls:
    
    time.sleep(0.3)
    page = getPage(number)
    FINAL = FINAL.append({**getContacts(page), **getInformation(page)}, ignore_index=True)
    time.sleep(0.3)
    getImage(number)
    
    current_time = time.time()
    hours, rem = divmod(current_time-start, 3600)
    minutes, seconds = divmod(rem, 60)
    sys.stdout.write("Elapsed time: {:0>2}:{:0>2}\r".format(int(minutes),int(seconds)))
    sys.stdout.flush()


print("Finished")
FINAL.to_csv("/Users/dmitrys/Desktop/DataProjects/OpenDataNKO/FINAL.csv")
