#-*- coding:utf-8 -*-

import sys
from lxml import etree
import requests
import dic_formate
import wri_mongo


TABLE_XPATH = "//table"
TR_XPATH = "tr"
TD_XPATH = "td"


def get_tables(url):    #抓取网页中的表格
    tables = []
    try:
        session = requests.session()
        session.proxies = {"http": "http://10.16.13.18:8080", "https": "http://10.16.13.18:8080"}
        respone = session.get(url, timeout=10)
        status_code = respone.status_code
        if 200 == status_code:
            dom_tree = etree.HTML(respone.content.replace("<br", ""))
            tables = dom_tree.xpath(TABLE_XPATH)
        else:
            print("response status_code is not 200: status_code: {0}".format(status_code))
    except Exception as e:
        print("Exception: {0}".format(e))

    return tables


def get_data(tables, dat):    #解析英文版本表格内容
    for index, table in enumerate(tables):
        if index != 0:
            for index_2, tr in enumerate(table.xpath(TR_XPATH)):

                if index_2 != 0:
                    lst = []

                    for index_1, td in enumerate(tr.xpath(TD_XPATH)):
                        if index_1 != 1:
                            if None != td.text:
                                lst.append(td.text.replace("/>\n", " "))
                            for a in td.xpath("a"):
                                lst.append(a.text)

                    dic = dic_formate.get_formate()

                    if len(lst) == 5 and lst[2] == u'All Nexus':  #or u'所有 Nexus 设备'   'All Nexus'
                        dic['id'] = lst[0]
                        lst_3 = lst[3].split(',')
                        for mm in lst_3:
                            dic['affected_version'].append(mm.strip())
                        date_1 = dat.split('-')
                        dic['date']['year'] = int(date_1[0])
                        dic['date']['month'] = int(date_1[1])
                        dic['date']['day'] = int(date_1[2])


                        for index_tr, tr_pri in enumerate(tables[0].xpath(TR_XPATH)):
                             if index_tr != 0:
                                lst2 = []
                                for index_td, td_pri in enumerate(tr_pri.xpath(TD_XPATH)):
                                    if None != td_pri.text:
                                       lst2.append(td_pri.text.replace("/>\n", " "))
                                       # if lan == '':
                                       #     lst2.append(td_pri.text.replace("/>\n", " "))
                                       # elif lan == '/intl/zh-CN_ALL':
                                       #       lst2.append(td_pri.text.replace(">", " "))


                                lst3 = lst2[1].split(" ")

                                for item in lst3:
                                    if item.strip() == lst[0]:
                                        dic['summary'].append(lst2[0])
                                        dic['severity'].append(lst2[2])
                                        wri_mongo.insert_table(dic)

def get_data_or(tables):   #解析其它语言表格内容

    for index_tr, tr_pri in enumerate(tables[0].xpath(TR_XPATH)):
         if index_tr != 0:
            lst2 = []
            for index_td, td_pri in enumerate(tr_pri.xpath(TD_XPATH)):
                if None != td_pri.text:
                   lst2.append(td_pri.text.replace(">", " "))

            lst3 = lst2[1].split(" ")

            for item in lst3:
                if item and item != '\n' :

                    dic_sm = {}
                    dic_sm['summary'] = lst2[0]
                    dic_sm['severity'] = lst2[2]

                    wri_mongo.Add_item(item.strip(), dic_sm)




def get_html_en(date):   #获取英文网页内容

    URL = "https://source.android.com/security/bulletin/%s.html" % date
    tables = get_tables(URL)
    get_data(tables, date)


def get_html_or(date):     #获取其它语言网页内容
    LANGUAGE = ["/intl/zh-CN_ALL", "/intl/zh-TW_ALL", "/intl/ja_ALL", "/intl/ko_ALL", "/intl/ru_ALL"]
    for index, lan in enumerate(LANGUAGE):
        URL = "https://source.android.com%s/security/bulletin/%s.html" % (lan, date)

        tables = get_tables(URL)

        get_data_or(tables)



def main(argv):
    wri_mongo.connect()

    get_html_en(argv)
    get_html_or(argv)

if __name__ == "__main__":
    # main(sys.argv)
    main('2016-05-01')