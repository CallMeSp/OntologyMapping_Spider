# coding=utf-8
import requests
import json
import re
import operator
from bs4 import BeautifulSoup
import random

DrugSet=set([])
randomList=[]

def getPageCount(soup):
    res=soup.select('body > main > div > div.general-content > div:nth-of-type(5) > nav > ul > li.page-item.last > a')
    if res!=[]:
        href=res[0]
        pattern=re.compile(r'page=\d+')
        x=pattern.search(str(href)).group()
        return int(x[5:])
    else:
        return int(1)
# 高频无效词
def betterNone():
    HighFreq=['for','and','injection','capsules','tablets','solution','oral','suspension',
    'drops','sustained-release','compound','powder','inhalation','spray']
    return set(HighFreq)

def getHTMLText(url):
    try:

        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return ""

def findRandDrug():
    global DrugSet
    with open('Products.txt','r') as target:
        for temp in target.readlines():
            en_name=re.match(r'.*',re.split(r' ',temp,maxsplit=1)[1]).group()
            ch_name=re.match(r'.*',re.split(r' ',temp,maxsplit=1)[0]).group()
            if(len(en_name)>5):
                DrugSet.add(en_name)
    DurgList=list(DrugSet)
    for i in range(50):
        randIndex=random.randint(0,len(DurgList)-1)
        while(DurgList[randIndex] in randomList):
            randIndex=random.randint(0,len(DurgList)-1)
        randomList.append(DurgList[randIndex])
    
    
    with open('randomList.txt','w') as target:
       for temp in randomList:     
           target.write(temp+'\n')

def getRandDrug():
    randList=[]
    with open('randomList.txt','r') as target:
       for temp in target.readlines():
           randList.append(temp.replace('\n',''))
    return randList
# 辨别是否能直接返回结果 eg：True：Dimetotiazine，False：
def testIsSuc(product_name):
    namelist=product_name.split(' ')
    lenth=len(namelist)
    toSerchStr=''
    for i in range(lenth):
        if i!=0:
            toSerchStr+='+'+namelist[i]
        else:
            toSerchStr=namelist[i]
    url='https://www.drugbank.ca/unearth/q?c=_score&d=down&query='+toSerchStr+'&searcher=drugs'
    # print(url)
    try:
        r = requests.get(url, timeout=100)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        responseurl=str(r.url)
        if(responseurl[:30]=='https://www.drugbank.ca/drugs/'):
            return r.url
        else:
            return ''
    except:
        print('err')
        return ''
# 没有直接匹配到结果，遍历该搜索下的所有条目  eg：Amoxicillin and Clavulanate Potassium
def searchInDrugBankByName(en_name):
    global WholeOwlResult
    namelist=en_name.split(' ')
    lenth=len(namelist)
    toSerchStr=''
    for i in range(lenth):
        if i!=0:
            toSerchStr+='+'+namelist[i]
        else:
            toSerchStr=namelist[i]
    html=getHTMLText('https://www.drugbank.ca/unearth/q?c=_score&d=down&query='+toSerchStr+'&searcher=drugs')
    soup=BeautifulSoup(html,'html.parser')
    pageNum=getPageCount(soup)
    # print('The results have %d pages'%pageNum)

    # 原始页码太多现只取1页
    if pageNum>1:
        pageNum=1

    for i in range(1,pageNum+1):
        html=getHTMLText('https://www.drugbank.ca/unearth/q?c=_score&d=down&page='+str(i)+'&query='+toSerchStr+'&searcher=drugs')
        soup=BeautifulSoup(html,'html.parser')
        # 选出匹配到最多关键词的条目
        maxLength=0;maxHref='';maxName=''

        for temp in soup.find_all('div',class_='unearth-search-hit my-1'):
            
            # 得到形如 “/drugs/DB00359” 的url
            a_content=str(temp.select('div > h2 > a')[0])
            hreftemp=re.search(r'=\"/.*\"',a_content).group()
            href=hreftemp[2:-1]
            
            # 得到drugbank中搜索到的某条目的药品名称
            nameSerched=temp.select('div > h2 > a')[0].text
            
            # 搜索到的词条的关键词
            keywords=set([])
            for em in temp.select('div > div:nth-of-type(3) > small > em'):
                keywords.add(em.text.lower())
                
            # 除掉高频无效词
            keywords=keywords-betterNone()
            if(len(keywords)>maxLength):
                maxLength=len(keywords)
                maxHref='https://www.drugbank.ca'+href
                maxName=nameSerched
            # print(nameSerched,'  ',href)
            # print(keywords)
    maxUri=maxHref.split('/')[-1]
    return maxUri

def pricisionTest():
    with open('randomList_Result.txt','r') as target:
        count=0;total=50;iterK=0
        for temp in target.readlines():
            drugName=temp.split('*')[0]
            mathedUri=temp.split('*')[1][:7]
            if(len(mathedUri)==1):
                continue
            res=testIsSuc(drugName)
            if len(res)>0:#直接匹配成功的
                mappingresult=res.split('/')[-1]
                if(mappingresult==mathedUri):
                    count=count+1
                    print('suc',count)
                else:
                    print('err',count)
            else:#没有直接匹配成功的
                mappingresult=searchInDrugBankByName(drugName)
                if(mappingresult==mathedUri):
                    count=count+1
                    print('suc',count)
                else:
                    print('err',count)
        print(count)
        rate=float(count)/total
        print(rate)

pricisionTest()
#50条数据正确39条。0.78正确率