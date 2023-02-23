import os
from bs4.element import NavigableString
from bs4 import BeautifulSoup
from lxml import html
import json
import boto3 
ct = None

F = []
Bin = ('.jpeg','.js','.css','.png','.jpg','.woff2','.svg','.xml','.py')
def main():
    for path,_,files in os.walk('.'):
        for file in files:
            abs_path = os.path.join(path,file)
            if os.path.splitext(abs_path)[1] in Bin:
                continue
            if '.git' in abs_path:
                continue
            f = None
            if not abs_path.endswith('.hi'):
                continue
            try:
                f = open(abs_path,'r')
                dt = f.read(20)
            except Exception as e:
               pass
            else:
                if "<!DOCTYPE html>".lower() in dt.lower() or "<html" in dt:
                    dt += f.read()
                    # fix_links(dt,abs_path)
                    F.append(abs_path)
                else:
                    print('doc type not find',abs_path)
            finally:
                if f:
                    f.close()

client = boto3.client("translate")
if os.path.exists('cache_ts.1.json'):
    Cache = json.loads(open('cache_ts.1.json','r').read())
else:
    Cache = {}
def save():
    d = json.dumps(Cache,indent=4,ensure_ascii=False)
    open('cache_ts.1.json','w').write(d)
def translate_text(text):
    # if text.isascii():
    #     import pdb
    #     pdb.set_trace()
    if text in Cache:
        # print('has ',text)
        return Cache[text]
    print('request')
    response = client.translate_text(
        Text=text, 
         SourceLanguageCode='en', 
        TargetLanguageCode='hi', Settings={
            'Formality': 'FORMAL', 
            'Profanity': 'MASK'
        })
    if response['ResponseMetadata']['HTTPStatusCode'] != 200:
        raise Exception("Got ",response['ResponseMetadata']['HTTPStatusCode'])
    try:
        Cache[text] = response['TranslatedText']
    except KeyError:
        print("KeyError")
        raise
    # print(response)
    return response['TranslatedText']

def get_input(file):
    # get_texts(file):
    with open(file) as f:
        bs = BeautifulSoup(f.read())
    ip = bs.find_all('input')
    print(len(ip))
    for i in ip:
        # print('for -lopp')
        t = i.get('placeholder')
        print(t)
        if t:
            pass
            ts = translate_text(t)
            i['placeholder'] = ts
            print(t,ts,' placeholder ')
    with open(file,'w') as dest:
        dest.write(bs.prettify())

def get_texts(file):
    with open(file) as f:
        bs = BeautifulSoup(f.read())
    Text = []
    tags = bs.find_all()
    for tag in tags:
        for el in tag.contents:
            if isinstance(el,NavigableString):
                text = el.text.strip()
                if text:
                    Text.append(el)
    c  = 0
    print(len(Text),' total')
    if len(Text) > 2000:
        print('huge')
        # return
    for t in Text:
        try:
            ts = translate_text(t.text.strip())
        except Exception:
          raise
        c += 1
        if c%50 == 0:
            print(c)
        # print(t.text,'  ',ts)
        t.replace_with(NavigableString(ts))
    with open(file+'.hi','w') as dest:
        dest.write(bs.prettify())

get_texts('./catalog-iframe.html')
