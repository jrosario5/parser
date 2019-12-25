import spacy
import re
import os
import json
import pandas as pd

nlp = spacy.load("gp")

def extract_clean_resume(text):
    splitByline     = text.split('\n')
    i=0
    resumeText=''
    for line in splitByline:
        if not re.match(r'^\s*$', line):
            resumeText+=line +'\n'
    return resumeText
##---------------------------------------------------------------------->
def extract_phone_numbers(document):
    docSplit = document.split('\n')
    doc = ''
    ing = 0
    for newDoc in docSplit:
        doc += newDoc+'\n'
        ing += 1
        if(ing>=5):
            break;
    r = re.compile(r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})')
    phone_numbers = r.findall(doc)
    return [re.sub(r'\D', '', number) for number in phone_numbers]

def extract_email_addresses(string):
    r = re.compile(r'[\w\.-]+@[\w\.-]+')
    return r.findall(string)

def extract_name(document):
    docs = n(document)
    for entity in docs.ents:
        if(entity.label_=='NAME'):
            name = entity.text
            #break;
        return name
def extract_skills(document):
    doc = n(document)
    skills = ''
    #df = pd.DataFrame()
    items = []
    for skill in doc.ents:
        if(skill.label_=='SKILLS'):
            #skills.append(skill.text)
            items.append({'skills':skill.text})
            #skills +=str(skill.text)+';'
    df = pd.DataFrame(items, columns=['skills'])
    #print df.skills
    dfd=df.drop_duplicates()
    for ind in dfd.index:
        #print(dfd['skills'][ind])
        skills +=str(dfd['skills'][ind])+';'
    return str(skills)

def extract_home_address(document):
    doc = n(document)
    h = ''
    for ent in doc.ents:
        if ent.label_=='HOME_ADDRESS':
            h=ent.text
            break;
    return h
def extract_url(document):
    doc= n(document)
    u=''
    for uent in doc.ents:
        if uent.label_=='URL':
            u = uent.text
            break;
    return u

weburl = salesforce.query("select Id,TR1__Type__c,TR1__Contact__c,TR1__HTML_URL__c from TR1__ContactDocument__c where TR1__Type__c='Resume' limit 500 ")
for key in weburl:
    init(key['TR1__Contact__c'], key['TR1__HTML_URL__c'], key['TR1__HTML_URL__c'])
    print (key['TR1__HTML_URL__c'])
if __name__ == '__main__':
    pass

#init(weburl[0]['TR1__Contact__c'],weburl[0]['TR1__HTML_URL__c'], weburl[0]['TR1__HTML_URL__c'])

