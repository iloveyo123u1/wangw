#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
some db interface 
"""
import pymongo
import pycurl
from BeautifulSoup import BeautifulSoup 
import StringIO
import time
from django.utils.encoding import smart_str, smart_unicode
import os 
import traceback
from datetime import datetime,timedelta
import  json
#from smallgfw import GFW
import os 
import os.path
from pymongo import ASCENDING,DESCENDING 
import requests 
from urlparse import urlparse
import sys
import urlparse
import re
import types 
import sys
import logging  
import urllib
from urllib import urlencode

import time, MySQLdb


# logging.basicConfig(filename = os.path.join(os.getcwd(), 'log.txt'),level = logging.WARN, filemode = 'w', format = '%(asctime)s - %(levelname)s: %(message)s')


mktime=lambda dt:time.mktime(dt.utctimetuple())
######################db.init######################
# connection = pymongo.Connection('localhost', 27017)
# 
# db=connection.x


conn=MySQLdb.connect(host="localhost",user="root",passwd="fubendong",db="wangwang",charset="utf8")  
cursor = conn.cursor()


def zp(data):
    """
    print dict list
    """
    for k in data:
        print '%s:'%k,data[k]

def get_html(url,referer ='',verbose=False,protocol='http'):
    if not url.startswith(protocol):
        url = protocol+'://'+url
    url = str(url)
    
    time.sleep(1)
    html=''
    headers = ['Cache-control: max-age=0',]
    try:
        crl = pycurl.Curl()
        crl.setopt(pycurl.VERBOSE,1)
        crl.setopt(pycurl.FOLLOWLOCATION, 1)
        crl.setopt(pycurl.MAXREDIRS, 5)
        crl.setopt(pycurl.CONNECTTIMEOUT, 8)
        crl.setopt(pycurl.TIMEOUT, 30)
        crl.setopt(pycurl.VERBOSE, verbose)
        crl.setopt(pycurl.MAXREDIRS,15)
        #crl.setopt(pycurl.PROXY, 'http://180.156.246.130:8080')
        crl.setopt(pycurl.USERAGENT,'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:9.0.1) Gecko/20100101 Firefox/9.0.1')
        #crl.setopt(pycurl.HTTPHEADER,headers)
        if referer:
            crl.setopt(pycurl.REFERER,referer)
        crl.fp = StringIO.StringIO()
        crl.setopt(pycurl.URL, url)
        crl.setopt(crl.WRITEFUNCTION, crl.fp.write)
        crl.perform()
        html=crl.fp.getvalue()
        crl.close()
    except Exception,e:
        print('\n'*9)
        traceback.print_exc()
        print('\n'*9)
        return None
    return html

    #r = requests.get(url)
    #return r.text

    #r = browser.get(url)
    #return r.content


def searchcrawler(url):
    
    html=get_html(url)
#     print url
    if html:
        soup = BeautifulSoup(html,fromEncoding='gbk')
        items_row = soup.findAll('div',{'class':'item-box st-itembox'})
        if items_row:
            print '=======================row search row=========================='
            for item in items_row:
#                 print item
                item_info = item.find('h3',{'class':'summary'}).a
                item_url = item_info['href']
#                 print item_url
                
                
                sid_info = item.find('div',{'class':'col seller feature-dsi-tgr'}).a
                print sid_info
                sid_item_url = sid_info['href']
                sid_url_info = urlparse.urlparse(sid_item_url)
                sid_id = urlparse.parse_qs(sid_url_info.query,True)['user_number_id'][0]
                print sid_id
                
                judge_site(item_url, sid_id)
                
#                 logging.warning(item_id)
#                 
#                 download_reply_by_id(item_id)
                
        items_col = soup.findAll('div',{'class':'product-item row icon-datalink'})       
        if items_col:
            
            print '=======================row search col=========================='
            #print items
            for item in items_col:
                item_info = item.find('div',{'class':'title'}).a
                item_url = item_info['href']
#                 url_info = urlparse.urlparse(item_url)
#                 item_id = urlparse.parse_qs(url_info.query,True)['id'][0]
                print item_url
#                 print item_id

                sid_info = item.find('div',{'class':'seller'}).a
                print sid_info
                sid_item_url = sid_info['href']
                sid_url_info = urlparse.urlparse(sid_item_url)
                sid_id = urlparse.parse_qs(sid_url_info.query,True)['user_number_id'][0]
                print sid_id
                
                judge_site(item_url, sid_id)
#                 judge_site(item_url)


def judge_site(url, sid_id):
    """
    判断物品是tb还是tm
    """
    url_info = urlparse.urlparse(url)
    urlkey = urlparse.parse_qs(url_info.query,True)
    iid = int(urlkey['id'][0])
    print iid
#     print 'url_info:',url_info[1]
    try:
        if url_info[1] == 'detail.tmall.com':
            print 'it is a tm item'
            
            data = download_tm_reply_by_id(iid)
        elif urlkey.get('cm_id'):
            print 'it is a tm item cm_id'
            
            data = download_tm_reply_by_id(iid)
        else:
            print 'it is a tb item'
            
            data = download_tb_reply_by_id(iid, sid_id)
    except Exception ,e:
        print traceback.print_exc()
        return
    
    
#下载淘宝物品信息
def download_tb_reply_by_id(iid, sid_id):
    i = 1;
    data = []
    
    #http://rate.tmall.com/list_detail_rate.htm?itemId=16862466992&order=1&currentPage=2&append=0&content=1&tagId=&posi=&picture=&_ksTS=1410515765306_2008&callback=jsonp2009
    userNumId = ''
    url = "http://rate.taobao.com/feedRateList.htm?callback=jsonp2009&userNumId=%s&auctionNumId=%s&siteID=1&currentPageNum=%s&rateType=&orderType=sort_weight&showContent=1&attribute="%(sid_id ,iid,i)
    print url
    res_json=get_html(url)
    #print res_json
#     logging.warning(url)
    e_num = 1
    save_e =1 
    annoy_res = 1
    b_res = 1
    while True:
        try:
            if e_num > 10:
                break;
            res_json = res_json[14:]
            res_json=res_json[:-3]
            #print res_json
            res_json = json.loads(res_json,encoding='gbk')
            if res_json["comments"] == "null":
                break;
            for info in res_json["comments"]:
                info_annoy = info["user"]["anony"]
                if  info_annoy == False  :

                    
                    data = {}
                    data['username'] = str(info["user"]["nick"].encode('utf-8'))
                    data['displayRateSum'] = info["user"]["rank"]
                    data['tamllSweetLevel'] = info["user"]["vipLevel"]
                    data['displayUserNumId'] = info["user"]["userId"]
#                     logging.warning(data) 
                    annoy_res = annoy_res +1
                    save_res = save_download_wangwang(data)
                    if save_res == 2:
                        save_e = save_e + 1
            
            if save_e == annoy_res:
                b_res = b_res + 1
                if b_res > 3:
                    break;
            
            lastPage = res_json["maxPage"]
            page     = res_json["currentPageNum"]
            if lastPage - page == 0 :
                print url
                break;
            i = i + 1
            url = "http://rate.taobao.com/feedRateList.htm?callback=jsonp2009&userNumId=%s&auctionNumId=%s&siteID=1&currentPageNum=%s&rateType=&orderType=sort_weight&showContent=1&attribute="%(sid_id ,iid,i)
            res_json=get_html(url)
            print url
            
        except Exception,e:
            print e
            i = i + 1
            e_num = e_num + 1
            url = "http://rate.taobao.com/feedRateList.htm?callback=jsonp2009&userNumId=%s&auctionNumId=%s&siteID=1&currentPageNum=%s&rateType=&orderType=sort_weight&showContent=1&attribute="%(sid_id ,iid,i)
            res_json=get_html(url)
           
def download_tm_reply_by_id(iid):
    i = 1;
    data = []
    #http://rate.tmall.com/list_detail_rate.htm?itemId=16862466992&order=1&currentPage=2&append=0&content=1&tagId=&posi=&picture=&_ksTS=1410515765306_2008&callback=jsonp2009
    url = "http://rate.tmall.com/list_detail_rate.htm?itemId=%s&order=1&currentPage=%s&append=0&content=1&tagId=&posi=&picture=&_ksTS=1410515765306_2008&callback=jsonp2009"%(iid,i)
#     print url
    res_json=get_html(url)
#     logging.warning(url)
    e_num = 1
    save_e =1 
    annoy_res = 1
    b_res = 1
    while True:
        try:
            if e_num > 10:
                break;
            res_json = res_json[13:]
            res_json=res_json[:-1]
            res_json = json.loads(res_json,encoding='gbk')
            for info in res_json["rateDetail"]["rateList"]:
                info_annoy = info["anony"]
                if  info_annoy == False  :
                    #info_buyer = json.dumps(info['buyer'],ensure_ascii=False)
    #                 logging.warning(info["displayUserNick"]) 
                    data = {}
                    data['username'] = str(info["displayUserNick"].encode('utf-8'))
                    data['displayRateSum'] = info["displayRateSum"]
                    data['tamllSweetLevel'] = info["tamllSweetLevel"]
                    data['displayUserNumId'] = info["displayUserNumId"]
                    logging.warning(data['username']) 
                    annoy_res = annoy_res +1
                    save_res = save_download_wangwang(data)
                    if save_res == 2:
                        save_e = save_e + 1
            if save_e == annoy_res:
                b_res = b_res + 1
                if b_res > 3:
                    break;
            
            lastPage = res_json["rateDetail"]["paginator"]["lastPage"]
            page     = res_json["rateDetail"]["paginator"]["page"]
            if lastPage - page <= 1 :
                print url
                break;
            i = i + 1
            url = "http://rate.tmall.com/list_detail_rate.htm?itemId=%s&order=1&currentPage=%s&append=0&content=1&tagId=&posi=&picture=&_ksTS=1410515765306_2008&callback=jsonp2009"%(iid,i)
            res_json=get_html(url)
            print url
            
        except Exception,e:
            print e
            i = i + 1
#             i = i + 1
            e_num = e_num + 1
            url = "http://rate.tmall.com/list_detail_rate.htm?itemId=%s&order=1&currentPage=%s&append=0&content=1&tagId=&posi=&picture=&_ksTS=1410515765306_2008&callback=jsonp2009"%(iid,i)
            res_json=get_html(url)
            
def save_download_wangwang(data): 
    try:
        type =1 
        sql = "insert into wangwang_tmall ( `username`, `displayRateSum`, `tamllSweetLevel`, `displayUserNumId`, `type`, `add_time`) values(%s,%s,%s,%s,%s,'%s')" 
        param = (data['username'], data['displayRateSum'],data['tamllSweetLevel'],data['displayUserNumId'],type,int(time.time()))
        
        n = cursor.execute(sql,param)
        logging.warning(n)
        return n
    
    except:
        a = 2
        logging.warning(a)
        return a
        
        
def executeNonQuery(sql):
    while cursor.nextset(): 
        pass
    cursor.execute(sql)
    
    
def runcrawler():
    j = 1
    num = ''
    url = "http://list.tmall.com/search_product.htm?&q=%s&sort=d"
#     sql = 'SELECT id, keyword FROM `keyword` where status = 1'
    
    while True:
        
        count=cursor.execute("SELECT id, keyword FROM `keyword` where status = 1 and type='nvzhuang' limit 1")
        print 'there has %s rows record' % count
        if count == 0 :
            print "end"
            break
    #     cursor.scroll(0,mode='absolute')
        row = cursor.fetchone() 
#         print row
        keyword = row[1]
        id = row[0]
        if keyword :
            j = 1
            try:
                print id
                logging.warning(id)
                logging.warning(keyword)
                sql1 = " update keyword set status = 0 where id = %s " % id 
#                 print sql1
                res = cursor.execute(sql1)
            except Exception,e:
                 print e
            while j < 4 :
                try:
                    name = keyword.encode('GBK').strip('\"')
                    name = urllib.quote(name)
                    url = "http://s.taobao.com/search?&sort=sale-desc&tab=all&q=%s&s=%s"%(name,num)
                    print url
                    logging.warning(url)
                    searchcrawler(url)
                    num = 22 * j
                    j = j +1
                except Exception,e:
                    print e
                    j = j +1
                    num = 22 * j
    #                     url = "http://s.taobao.com/search?%s&commend=all&search_type=item&sourceId=tb.index&sort=sale-desc&s=%s"%(name,num)

if __name__ == "__main__":
    
    runcrawler()