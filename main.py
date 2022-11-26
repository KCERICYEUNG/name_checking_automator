import re
import nltk
nltk.download('punkt')
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize, word_tokenize
from pprint import pprint
from nltk.corpus import wordnet
from nltk.corpus import stopwords
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from bs4 import BeautifulSoup
import requests as r
from opencc import OpenCC
import streamlit as st
from IPython.display import HTML

st.set_page_config(layout="wide")
st.title('Name Checking Automator')
names = st.text_input('Please input the name')
numbers = st.text_input('Please input the number of result')

lemmatizer = WordNetLemmatizer()
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
name = names
number = numbers
time.sleep(2.5)
driver.get(f'https://www.google.com/search?q={name}' + f"&hl=en&biw=1148&bih=729&num={number}&lr=&ft=i&cr=&safe=images&tbs=&start=1")
cells = driver.find_elements(By.CSS_SELECTOR, ".MjjYud")

name_list = []
description_list = []
link_list = []

for cell in cells:
    names = cell.find_elements(By.CSS_SELECTOR,".yuRUbf h3")
    description = cell.find_elements(By.CSS_SELECTOR,".VwiC3b.yXK7lf.MUxGbd.yDYNvb.lyLwlc")
    link = cell.find_elements(By.CSS_SELECTOR,".yuRUbf a")

    if names == []:
        name_list.append("N/A")
    for n in names:
        true_name = n.get_attribute("textContent")
        name_list.append(true_name.strip())
    if description == []:
        description_list.append("N/A")
    for d in description:
        description_list.append(d.text.strip())
    if link == []:
        link_list.append("N/A")
    for l in link:
        url = l.get_attribute("href")
        if "translate.google.com" not in url:
            link_list.append(url)
driver.close()

df = pd.DataFrame({
    "Title": name_list,
    "Description": description_list,
    "Link": link_list,
})
def fetch_content(link):

    if link == "N/A":
        return "N/A"
    else:
        try:
            headers = r.utils.default_headers()
            headers.update({
                'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
            })
            res = r.get(link, headers=headers, timeout=5)
            html_page = res.content
            soup = BeautifulSoup(html_page, 'html.parser')
            text_obj = soup.find_all(text=True)

            output = ''
            blacklist = [
                '[document]',
                'noscript',
                'header',
                'html',
                'meta',
                'head',
                'input',
                'script',
                'style']

            for t in text_obj:
                if t.parent.name not in blacklist:
                    output += '{} '.format(t)

            return output
        except:
            return "N/A"

df['Content'] = df['Link'].apply(fetch_content)
identifiers = {}
new_key_word_list = []
key_word_list = ["dprk",
                 "sanctions",
                 "nacrotics",
                 "bribery",
                 "corruption",
                 "laundering",
                 "trafficking",
                 "drugs",
                 "politically exposed person",
                 "bribe",
                 "icac",
                 "independent commission against corruption",
                 "criminal",
                 "crime",
                 "terrorism"]
source_dict = {"news":["01icon.hk","hk01.com","scmp","bbc","globaltimes","hongkongfp","chinadailyhk","cnbc","thestandard","www.ft.com",".rthk","news","taipeitimes"],
               "social media":["facebook","linkedin","twitter","instagram"],
               "edu":["edu",".hku"],
               "regulator":["gov","ofac"],
               "encyclopedia":["wiki","britannica",".baidu"],
               "legal":["vlex"]}
tra_chi_key_word_list = ["恐怖主義",
                     "恐怖份子",
                     "制裁",
                     "毒品",
                     "受規管藥物",
                     "賄賂",
                     "貪污",
                     "洗錢",
                     "洗黑錢",
                     "走私",
                     "人口販賣",
                     "違禁品",
                     "政治人物",
                     "犯罪",
                     "逃稅",
                     "受賄",
                     "行賄",
                     "賄款",
                     "廉政公署"]

sim_chi_key_word_list = []

# Convert TC to SC
cc = OpenCC('t2s')
for i in tra_chi_key_word_list:
    a = cc.convert(i)
    sim_chi_key_word_list.append(a)

# Find similar english words
for word in key_word_list:
    for syn in wordnet.synsets(word):
        for i in syn.lemmas():
            if i.name() in new_key_word_list:
                pass
            else:
                new_key_word_list.append(i.name())

# Fix unwanted similar english words
new_key_word_list.remove("O.K.")
new_key_word_list.remove("okay")
new_key_word_list.remove("authority")
new_key_word_list.remove("authorization")
new_key_word_list.remove("authorisation")
new_key_word_list.remove("approve")
new_key_word_list.remove("traffic")
new_key_word_list.remove("wash")
new_key_word_list.remove("warrant")
new_key_word_list.remove("graft")
new_key_word_list.remove("buy")
new_key_word_list.remove("launder")
def lemmitize(s):
    tokenized = nltk.word_tokenize(s)
    return [lemmatizer.lemmatize(tt).lower() for tt in tokenized]

def translate_tc_sc(tokens):
    return [cc.convert(t) for t in tokens]

def capture_keyword(tokens, wordlist):
    captured = []
    for word in wordlist:
        if word in tokens:
            captured.append(word)
    return captured

# Lemmitize
df['Title_lem'] = df['Title'].apply(lemmitize)
df['Description_lem'] = df['Description'].apply(lemmitize)
df['Content_lem'] = df['Content'].apply(lemmitize)

# Translate TC
df['Title_sc'] = df['Title'].apply(translate_tc_sc)
df['Description_sc'] = df['Description'].apply(translate_tc_sc)
df['Contentn_sc'] = df['Content'].apply(translate_tc_sc)

# Find hits
## Eng
df['Title_lem_hits'] = df['Title_lem'].apply(lambda tokens: capture_keyword(tokens, new_key_word_list))
df['Description_lem_hits'] = df['Description_lem'].apply(lambda tokens: capture_keyword(tokens, new_key_word_list))
df['Content_lem_hits'] = df['Content_lem'].apply(lambda tokens: capture_keyword(tokens, new_key_word_list))
## TC
df['Title_tc_hits']  = df['Title'].apply(lambda tokens: capture_keyword(tokens, tra_chi_key_word_list))
df['Description_tc_hits']  = df['Description'].apply(lambda tokens: capture_keyword(tokens, tra_chi_key_word_list))
df['Content_tc_hits']  = df['Content'].apply(lambda tokens: capture_keyword(tokens, tra_chi_key_word_list))
## SC
df['Title_sc_hits']  = df['Title'].apply(lambda tokens: capture_keyword(tokens, sim_chi_key_word_list))
df['Description_sc_hits']  = df['Description'].apply(lambda tokens: capture_keyword(tokens, sim_chi_key_word_list))
df['Content_sc_hits']  = df['Content'].apply(lambda tokens: capture_keyword(tokens, sim_chi_key_word_list))
## Source
def source(k):
    for key,value in source_dict.items():
        for v in value:
            if v.lower() in k:
               return key.lower()
df["Source"] = df["Link"].apply(source)
df['Summary_hits'] = (df['Title_lem_hits'] + df['Description_lem_hits'] + df['Content_lem_hits']   +\
        df['Title_tc_hits'] + df['Description_tc_hits'] + df['Content_tc_hits'] +\
        df['Title_sc_hits'] + df['Description_sc_hits'] + df['Content_sc_hits'] ).apply(set)
df['True_Hit'] = df['Summary_hits'].apply(len) > 0
df_new = df[['Title', 'Description','Link','Content','True_Hit','Summary_hits','Source']]
st.dataframe(df_new)

@st.cache
def convert_df(df):
    return df.to_csv(index = False, encoding = "utf-8")
csv = convert_df(df_new)
st.download_button(label = "Press to Download",
                   data = csv,
                   file_name = "result.csv",
                   mime = "text/csv")
