from multiprocessing import Pool, Process, Manager
import xml.etree.ElementTree as et
import requests
import read_xmls  
import pandas as pd
import numpy as np  
import argparse
import re
import timeit

a = "C:/Users/Jacob/990s_2020/202000069349200000_public.xml"
b = "C:/Users/Jacob/990s_2020/202000069349200005_public.xml"
c = "C:/Users/Jacob/990s_2020/202000069349200010_public.xml"

def read_form(document=None, download=True):
    '''
    Reads in IRS 990 form from download or link, if download True.
    Input: link or file name, boolean for download
    Output: Element object
    '''
    #Get data and transform to tree object
    if download:
        r = requests.get(document)
        root = et.fromstring(r.content)
    else:
        tree = et.parse(document)
        root = tree.getroot()

    #remove namespace prefixes
    read_xmls.clean_xml(root)

    return root

def get_form_version(tree):
    '''
    Checks IRS Form 990 version
    Input: tree
    Output: Form number
    '''
    return tree.attrib['returnVersion']

def f(file):
    x = read_form(file, False)
    print(get_form_version(x))


if __name__ == '__main__':

    def seq():
        for i in [a,b,c]:
            s = read_form(i, False)
            print(get_form_version(s))
        return None
        
    with Pool(5) as p:
        print(timeit.timeit('p.map(f, [a,b,c])', number= 10))

    print(timeit.timeit(seq, number=10))