# coding=utf-8
import requests
import json
import re
import operator
from bs4 import BeautifulSoup

def getHTMLText(url):
    try:

        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return ""
#the total number of drugs that have been crawled
total=0

#the total number of drugs that have English name
count=0

# 高频无效词
def betterNone():
    HighFreq=['for','and','injection','capsules','tablets','solution','oral','suspension',
    'drops','sustained-release','compound','powder','inhalation','spray']
    return set(HighFreq)

def parseHtml(html):
    global total
    global count
    try:
        dict = json.loads(html)
        if (len(dict) > 0):
            total = total + 1
            product_name_ch = dict[1]['CONTENT']
            product_name_en = dict[2]['CONTENT']
            if (product_name_en != ''):
                count = count + 1
            print('药品名称：' + product_name_ch + ',英文名称： ' + product_name_en)
            print(str(count) + '/' + str(total))
    except:
        return

def parseImported(url,html):
    global total
    try:
        dict = json.loads(html)
        if (len(dict) > 0):
            total=total+1
            product_name_ch = dict[10]['CONTENT']
            product_name_en = dict[11]['CONTENT']
            print(str(total)+'  '+url)
            store(product_name_ch,product_name_en)
            print('药品名称：' + '%-20s' % product_name_ch + ',英文名称： ' + '%-30s' % product_name_en)

    except:
        return

def start():
    # id=25是国产   36是西药

    baseurl = 'http://mobile.cfda.gov.cn/datasearch/QueryRecord?tableId=36&searchF=ID&searchK='

    # 西药开始和结束的序号
    num_start = 11101
    num_end = 17556

    for i in range(num_start, num_end):
        url = baseurl + str(i)
        html = getHTMLText(url)
        parseImported(url, html)
def store(ch_name,en_name):
    with open('Products.txt','a+') as target:
        target.write('%s %s\n'%(ch_name,en_name))

def read():
    with open('Products.txt','r') as target:
        for i in target.readlines():
            if len(i)>5:
                print(i)

def createVocabList(dataSet):
    vocabSet=set([])
    for document in dataSet:
        # 集合的并集
        vocabSet=vocabSet|set(document)
    return list(vocabSet)
    
def MostFreq(vocabList,fullText):
    freqDict={}
    for token in vocabList:
        freqDict[token]=fullText.count(token)
    sortedFrq=sorted(freqDict.items(),key=operator.itemgetter(1),reverse=True)
    return sortedFrq[:100]  

def findMostFreqInList():
    with open('Products.txt','r') as target:
        EnglishNameList=[]
        fullText=[]
        for temp in target.readlines():
            en_name=re.match(r'.*',re.split(r' ',temp,maxsplit=1)[1]).group()
            if(len(en_name)>5):
                # print(en_name)
                EnglishNameList.append(en_name.split(' '))
                fullText.extend(en_name.split(' '))
        
        vocabList=createVocabList(EnglishNameList)
        for temp in MostFreq(vocabList,fullText):
            print(temp)

def getPageCount(soup):
    res=soup.select('body > main > div > div.general-content > div:nth-of-type(5) > nav > ul > li.page-item.last > a')
    if res!=[]:
        href=res[0]
        pattern=re.compile(r'page=\d+')
        x=pattern.search(str(href)).group()
        return int(x[5:])
    else:
        return int(1)
    #href=[0]
    # print(href)
    

# 没有直接匹配到结果，遍历该搜索下的所有条目  eg：Amoxicillin and Clavulanate Potassium
def searchInDrugBankByName(product_name,count):
    namelist=product_name.split(' ')
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
    print(str(count),'raw:',product_name,',result:',maxName,',url is ',maxHref)
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
# 建立映射
def startMapping():
    with open('Products.txt','r') as target:
        Count=0
        for temp in target.readlines():
            en_name=re.match(r'.*',re.split(r' ',temp,maxsplit=1)[1]).group()
            if(len(en_name)>5):
                res=testIsSuc(en_name)
                if len(res)>0:
                    Count+=1
                    print(str(Count),'raw:',en_name,',result:',en_name,',url is ',res)
                else:
                    Count+=1
                    searchInDrugBankByName(en_name,Count)

# 从直接匹配成功的样本中训练
def trainMapping():
    sucSet=set([])
    fullText=[]
    vocabList=set([])
    # 读出一次成功匹配的药瓶英文名称
    with open('suc.txt','r') as target:
        for line in target.readlines():
            sucSet.add(line.split(' ',maxsplit=1)[1][:-1])
    for drug in sucSet:
        namelist=drug.split(' ')
        lenth=len(namelist)
        toSerchStr=''
        for i in range(lenth):
            if i!=0:
                toSerchStr+='+'+namelist[i]
            else:
                toSerchStr=namelist[i]
        url='https://www.drugbank.ca/unearth/q?c=_score&d=down&query='+toSerchStr+'&searcher=drugs'
        html=getHTMLText(url)
        # 检索出该response中的同义词
        soup=BeautifulSoup(html,'html.parser')
        synonyms=[key.text for key in soup.select('ul.list-unstyled.table-list-break > li') if len(key)>0]
        fullText.extend(synonyms)
        vocabList=vocabList|set(synonyms)
    writeFile(fullText,'sucFullText.txt')
    writeFile(list(vocabList),'sucVocabList.txt')
                           
def writeFile(contentlist,filename):
    with open(filename,'a+') as target:
        for content in contentlist:
            target.write(content+' ')

trainMapping()


    # 是否可以通过训练能直接搜索到结果的557个样本得到一个模型
    # 来找到待搜索词条和搜索到的结果的key之间的关系
    # 找到关键词和无效关键词来提高剩余样本的匹配准确性
    # to be continued
    