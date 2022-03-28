# encoding='utf-8'
import requests
from bs4 import BeautifulSoup
import time
import os
import random
import sys
import re

header='https://www.ncbi.nlm.nih.gov/pmc/articles/pmid/'
headers = {}
#headers = {'user-agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'}

user_agent_list = ["Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; …) Gecko/20100101 Firefox/61.0",
                    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36",
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36",
                    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
                    "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10.5; en-US; rv:1.9.2.15) Gecko/20110303 Firefox/3.6.15",
                    ]
headers['User-Agent'] = random.choice(user_agent_list)

# download html from PMC
def download_pmc(pmid):

    start_time=time.time()
    url = header+pmid
    print('Download %s from PMC url %s ...'%(pmid, url))
    time.sleep(2)
    url = url.encode("utf8").decode("latin1")
    resp = requests.get(url, headers=headers, timeout = 3)
    resp.encoding = 'utf8'
    #soup = BeautifulSoup(resp.text, 'html.parser')
    content=resp.text
    #print(content)
    with open('./data/'+pmid+'.html','w') as f:
        f.write(content)
    print(time.time()-start_time)

# parse download html file (all)
def parsehtml(html_file):
    #print('parse '+html_file)
    html_content = ''
    section = ['MATERIALS AND METHODS','Supplementary Material',
                   'Acknowledgments','Abbreviations used:','Footnotes','REFERENCES']
    section1 = ['Abstract']
    ipfirst=[]
    iplast=[]
    ipfirstlast=[]
    ipcaption=[]
    with open(html_file, 'r') as f:
        rows = f.readlines()
        for row in rows:
            html_content = html_content+row
    soup = BeautifulSoup(html_content,'html.parser')
    content = ''
    ip = soup.select('.tsec.sec')
    ip_caption = soup.select('div.caption p')
    
    reg = re.compile('{"type[^}]*}*')

    for j in ip:
        temp = j.find('h2')
        if temp != None:
            #print(temp.text)
            temp2 = j.select('p')
            for i in temp2:
                if i not in ip_caption and temp.text not in section:
                    c = i.text.replace('\xe2\x80\x8b','').replace('\u200b','').replace('\n','').strip()     
                    content = content+' '+c
                f = reg.findall(content)
                content = reg.sub('',content)
                content = content.strip()
    pmid = soup.find("meta", {"name":"citation_pmid"})['content']

    return pmid, content

# parse download html file (only Abstarct)
def parsehtml_abstract(html_file):
    html_content = ''
    section = ['MATERIALS AND METHODS','Supplementary Material',
                   'Acknowledgments','Abbreviations used:','Footnotes','REFERENCES']
    section1 = ['Abstract']
    ipfirst=[]
    iplast=[]
    ipfirstlast=[]
    ipcaption=[]
    with open(html_file, 'r') as f:
        rows = f.readlines()
        for row in rows:
            html_content = html_content+row
    soup = BeautifulSoup(html_content,'html.parser')
    content = ''
    ip = soup.select('.tsec.sec')
    ip_caption = soup.select('div.caption p')

    reg = re.compile('{"type[^}]*}*')

    for j in ip:
        temp = j.find('h2')
        if temp != None:
            #print(temp.text)
            temp2 = j.select('p')
            for i in temp2:
                if i not in ip_caption and temp.text in section1:
                    c = i.text.replace('\xe2\x80\x8b','').replace('\u200b','').replace('\n','').strip()
                    content = content+' '+c
                f = reg.findall(content)
                content = reg.sub('',content)
                content = content.strip()
    pmid = soup.find("meta", {"name":"citation_pmid"})['content']
    title = soup.find("meta", {"name":"DC.Title"})['content']
    return pmid, title, content

