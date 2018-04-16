# coding=utf-8
import requests
import json
def getHTMLText(url):
    try:

        r = requests.get(url, timeout=30)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return ""

total=0
count=0
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
            print('药品名称：' +'%-20s'% product_name_ch + ',英文名称： ' + '%-30s'%product_name_en)
    except:
        return

#id=25是国产   36是西药

baseurl='http://mobile.cfda.gov.cn/datasearch/QueryRecord?tableId=36&searchF=ID&searchK='

#西药开始和结束的序号
num_start=11101
num_end=17556

for i in range(num_start,num_end):
    url=baseurl+str(i)
    html=getHTMLText(url)
    parseImported(url,html)





