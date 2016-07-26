# -*- coding: utf-8 -*-
# !/usr/bin/python

import os
import sys
import json
import re
import urllib2
from bs4 import BeautifulSoup

def get_app_info(pname):
    SHOUZHU_URL = "https://source.android.com/security/bulletin/%s.html"
    try:
        response = urllib2.urlopen(SHOUZHU_URL % pname, timeout=120)
        source_json_data = response.read()

    except urllib2.URLError:
        print "[{pn}] sz url time out".format(pn=pname)
    except KeyError:
        print "[{pn}] sz url no matched data".format(pn=pname)
    return source_json_data


def BuiLd_first(TABLE):
   FIRST_TAG = TABLE.find('tr')

   LEFTOVER_TAG = FIRST_TAG.find_next_sibling()
   CVEs = LEFTOVER_TAG.find('td').find_next_sibling()
   CVEs.contents


def main(argv):
    url_doc = get_app_info( "2016-05-01")
    soup = BeautifulSoup(url_doc)
    First_tab = soup.find('table')
    dic = BuiLd_first(First_tab)

if __name__ == '__main__':
   main(sys.argv)

