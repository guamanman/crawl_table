#-*- coding:utf-8 -*-

import sys
import os
from lxml import etree
import requests
import dic_formate
import wri_mongo

# DATE_XPATH="//h2[@id=\"2016-07-01_details\"]/following-sibling：://h2[@id=\"2016-07-05_details\"]/preceding-sibling"

TABLE_XPATH = "//table"
TR_XPATH = "tr"
TD_XPATH = "td"


def get_tables(url, data_list):

    try:
        session = requests.session()
        session.proxies = {"http": "http://10.16.13.18:8080", "https": "http://10.16.13.18:8080"}
        respone = session.get(url, timeout=10)
        status_code = respone.status_code
        if 200 == status_code:
            dom_tree = etree.HTML(respone.content.replace("<br", ""))
            tables_dic = get_table_shot(dom_tree, data_list)

        else:
            print("response status_code is not 200: status_code: {0}".format(status_code))
    except Exception as e:
        print("Exception: {0}".format(e))

    return tables_dic

def get_table_shot(tree, data_list):
   tables_dic = {}

   for data_index, dat in enumerate(data_list):

       if data_index < len(data_list)-1:
           DS_SUMMARY_XPATH="//h3[@id=\"%s_summary\"]/following-sibling::table[1]" % dat
           DS_DETAIL_XPATH="//h2[@id=\"%s_details\"]/following-sibling::table" % dat
           DE_DETALE_XPATH = "//h2[@id=\"%s_details\"]/following-sibling::table" % data_list[data_index+1]
           tables_dic[dat] = list(set(tree.xpath(DS_DETAIL_XPATH))-set(tree.xpath(DE_DETALE_XPATH)))
           tables_dic[dat].append(tree.xpath(DS_SUMMARY_XPATH))
       else:
           DS_SUMMARY_XPATH="//h3[@id=\"%s_summary\"]/following-sibling::table[1]" % dat
           DS_DETAIL_XPATH="//h2[@id=\"%s_details\"]/following-sibling::table" % dat
           tables_dic[dat] = tree.xpath(DS_DETAIL_XPATH)
           tables_dic[dat].append(tree.xpath(DS_SUMMARY_XPATH))
   return tables_dic


def get_data(tables_dic):
    for key, value in tables_dic.items():
        tables_num = len(value)   #tables_num=23

        for index, table in enumerate(value):

            if index < tables_num-1:
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
                            date_1 = key.split('-')
                            dic['date']['year'] = int(date_1[0])
                            dic['date']['month'] = int(date_1[1])
                            dic['date']['day'] = int(date_1[2])

                            for index_tr, tr_pri in enumerate(value[tables_num-1][0].xpath(TR_XPATH)):

                                 if index_tr != 0:
                                    lst2 = []
                                    for index_td, td_pri in enumerate(tr_pri.xpath(TD_XPATH)):
                                        if None != td_pri.text:
                                           lst2.append(td_pri.text.strip().replace("\n", " "))

                                    lst3 = lst2[1].split(",")
                                    print lst3
                                    for item in lst3:

                                        if item.strip() == lst[0]:

                                            dic['summary'].append(lst2[0])
                                            dic['severity'].append(lst2[2])
                                            wri_mongo.insert_table(dic)

def get_data_or(tables):

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
                    dic_sm['summary']=lst2[0]
                    dic_sm['severity']=lst2[2]

                    wri_mongo.Add_item(item.strip(), dic_sm)




def get_html_en(date,dat_lst):

    url = "https://source.android.com/security/bulletin/%s.html" % date
    tables_dic = get_tables(url, dat_lst)
    get_data(tables_dic)


def get_html_or(date,dat_lst):
    LANGUAGE = ["/intl/zh-CN_ALL", "/intl/zh-TW_ALL", "/intl/ja_ALL", "/intl/ko_ALL", "/intl/ru_ALL"]
    for index, lan in enumerate(LANGUAGE):
        url = "https://source.android.com%s/security/bulletin/%s.html" % (lan, date)
        tables_dic = get_tables(url,dat_lst)
        get_data_or(tables_dic)



def main(argv):
    wri_mongo.connect()
    dat_lst = ['2016-07-01', '2016-07-05']
    get_html_en(argv, dat_lst)
    get_html_or(argv, dat_lst)

if __name__ == "__main__":
    # main(sys.argv)
    main('2016-07-01')


