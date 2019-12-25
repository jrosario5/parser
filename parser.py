import spacy
import re
import os
import json
import pandas as pd

nlp = spacy.load("en_core_web_sm")

def init(contactId,webUrl, link):
    if webUrl:
        #resume = urllib2.urlopen(webUrl).read(200000)
        response = requests.get(webUrl)
        #resumeText = remove_html_tags(resume)
        #clean = re.compile('\{([^}]+)\}')
        #s= re.sub(clean, '', resumeText)
        #s = re.sub(r'\{([^}]+)\}', '', s)
        """paragraphs = justext.justext(response.content, justext.get_stoplist("English"))
        p=''
        for paragraph in paragraphs:
            print paragraph.text
            p+=paragraph.text
        print p
        print storage(contactId,str(p), link)"""

def remove_html_tags(text):
    """Remove html tags from a string"""
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)         
def storage(contactId, resume, link):
    resumeTable = db.api_resume
    data = {
        'contactId': contactId,
        'resumefulltext': str(resume),
        'url':link
        }
    result = resumeTable.insert_one(data)
    try:
        rid = str(result.inserted_id)
    except IndexError:
        rid = 0
    return rid

def salesforce_saving(ownerId, name, email, number, resumeText, skills, years_experience, title_experience, companies_experience, bio, home_address, url):
    try:
        nameSplit = name.split(' ')
        firstname = salesforce_clean(nameSplit[0])
        lastname = salesforce_clean(nameSplit[1])
    except:
        firstname = ''
        lastname = ''
        
    home_address = extract_home_address(resumeText)
    #print home_address+'st'
    try:
        split_address = home_address.split(',')
        city = split_address[0]
        state = split_address[1]
    except:
        city = ''
        state = ''
        #print 'no address'

    contact = {
        'type':'Contact',
        'lastname':str(lastname),
        'firstname':str(firstname),
        'TR1_LinkedIn_ProfileUrl__c':url,
        'GKR_Contact_Bio__c':bio,
        'AccountId':'0011I00000CuDnjQAF',
        'TR1__Skills__c':str(skills),
        'email':email,
        'phone':number,
        'OtherCity':city,
        'OtherState':state,
        'Title':str(title_experience[0])
        }
    #print contact
    res = salesforce.create(contact)
    try:
        cuid=res[0]['id']
    except IndexError:
        cuid=0
    """try:
        res = salesforce.create(contact)
    except:
        res = 0"""
        #print res
    """res still passing throu 
        and making call 
        for work history, 
        has to be FIX - Juan"""
    if cuid != 0:
        i=0
        while i < len(companies_experience):
            try:
                company= salesforce_clean(companies_experience[i])
            except IndexError:
                company=''
            try:
                title = salesforce_clean(title_experience[i])
            except IndexError:
                title = ''
            try:
                from_year=years_experience[i].split('-')
                f=re.sub(r"^\s+", "", from_year[0])
                t=re.sub(r"^\s+", "", from_year[1])
            except IndexError:
                from_year = ['','']
            work_experience ={
                'type':'TR1__EmploymentHistory__c',
                'GKR_Account__c':findAccount(company),
                'TR1__Contact__c':cuid,
                'TR1__EmployerName__c':company,
                'TR1__Title__c':title,
                'TR1__StartDate__c':f,
                'TR1__EndDate__c':t
            }
            wres = salesforce.create(work_experience)
            #print wres
            i+=1
    return res
    #return res
def salesforce_clean(val):
    try:
        c = val.replace("'", "\'")
    except:
        c = val
    return c

def findAccount(name):
    #query = salesforce.query("select Id, Name, AR_Approved__c From Account where Name like '%"+cName+"%' and Id!='"+cid+"' ")
    cname = salesforce_clean(name).replace("'", "")
    query = salesforce.query("SELECT Id FROM Account where Name like '%"+cname+"%' ")
    if not query['records']:
        return '0011I00000CuDnjQAF'
    else:
        return str(query[0]['Id'])

def salesforce_owner(email):
    res = salesforce.query("SELECT Id FROM user WHERE email='"+email+"' ")
    try:
        return res[0]['Id']
    except IndexError:
        return 'GKR SF ID'
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
def extract_experience(document):
    doc = n(document)
    exp = {
        'companies':[],
        'title':[],
        'exp_year':[]
    }
    for x in doc.ents:
        if x.label_=='COMPANIES':
            exp['companies'].append(x.text)
        if x.label_=='TITLE':
            exp['title'].append(x.text)
        if x.label_=='YEARS_OF_EXPERIENCE':
            #exp['exp_year'].append(experience(x.text))
            #s=x.text.split(" ")
            #print month_string_to_number(s[0])
            #print x.text
            try:
                s=x.text.split(" ")
                print month_string_to_number(str(s[0]))
            except:
                print "s"
            exp['exp_year'].append(x.text)

    return exp
def month_string_to_number(string):
    m = {
        'jan': 1,
        'feb': 2,
        'mar': 3,
        'apr':4,
        'may':5,
        'jun':6,
        'jul':7,
        'aug':8,
        'sep':9,
        'oct':10,
        'nov':11,
        'dec':12
        }
    s = string.strip()[:3].lower()
    try:
        out = m[s]
        return out
    except:
        raise ValueError('Not a month')

def experience(data):
    split = data.split('-')
    return split

def paragraphs(document):
    doc = n(document)
    p = ''
    for p in doc.ents:
        if p.label_=='PARAGRAPH':
            p = p.text
            break;
    if p==None:
        return ""
    return p

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

