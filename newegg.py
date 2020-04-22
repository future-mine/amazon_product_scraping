'''

This short program utilizes the tools of requests and beautiful soup in order to web scrape information from the
products page of Newegg and parses it into a useful CSV data file for analysis.

'''
import re
import secrets
import pymysql
import json
import pandas as pd
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup
from os.path  import basename
import PySimpleGUI as sg
import csv
import time
db = ''
def get_html(url):
    '''
        Accepts a single URL argument and makes an HTTP GET request to that URL. If nothing goes wrong and
        the content-type of the response is some kind of HTMl/XML, return the raw HTML content for the
        requested page. However, if there were problems with the request, return None.
    '''
    try:
        with closing(get(url, stream=True)) as resp:
            if quality_response(resp):
                return resp.content
            else:
                return None
    except RequestException as re:
        print(f"There was an error during requests to {url} : {str(re)}")
        return None


def quality_response(resp):
    '''
        Returns true if response seems to be HTML, false otherwise.
    '''
    content_type = resp.headers["Content-Type"].lower()
    return (resp.status_code == 200 and content_type is not None and content_type.find("html") > - 1)

def get_products_url_one(url):
    ''' 
        Downloads the webpage, iterates over <div> elements and picks out the brand, product name, product
        price and shipping costs into a list.
    '''

    base_url = "https://www.carrefouruae.com"
    # print(url)
    # url = "https://www.carrefouruae.com/mafuae/en/bio-organic-food/c/F1200000?&qsort=relevance&pg=1"
    response = get_html(url)
    # print(response)

    items_desc = []
    if response is not None:
        soup = BeautifulSoup(response, "html.parser")
        products = soup.find_all("div", {"class": "plp-list__item"})
        for product in products:

            product_url = product.find("a", {"class": "js-gtmProdData"}).get('href')
            items_desc.append(product_url)

            # print(product_url)

        return items_desc
    # else:
    #     return 
    raise Exception(f"There was an error retrieving contents at {url}")

def generate_unique_key(size=15):
    return secrets.token_urlsafe(size)[:size]

def get_item(url):
    if len(url) < 3:
        return False
    response = get_html(url)
    asin = url.split('/')[4]
    items = []
    items.append(asin)
    if response is not None:
        soup = BeautifulSoup(response, "html.parser")
        name_item = soup.find("h1", {"class": "a-size-large a-text-ellipsis"})
        if(name_item is None):
            name = 'NA'
        else:
            name = name_item.text
        items.append(name)
        print('name')

        rating_item = soup.find("span", {"class": "a-size-medium a-color-base"})
        if(rating_item is None):
            rating = 'NA'
        else:
            rating = rating_item.text.split(' ')[0]
        print("rating")
        items.append(rating)

        no_rating_item = soup.find("div", {"class": "a-row a-spacing-medium averageStarRatingNumerical"})
        if(no_rating_item is None):
            num_rating = "NA"
        else:
            ptr = no_rating_item.text
            num_rating = ptr.split(' ')[0]
            num_rating = num_rating.replace(',','')
        print('num_rating')
        items.append(num_rating)

        review_num_item = soup.find("div", {"id": "filter-info-section"})
        if(review_num_item is None):
            num_review = 'NA'
        else:
            ptr = review_num_item.text.split(' ')
            num_review = ptr[3]
            num_review = num_review.replace(',','')
        print('num_review')
        items.append(num_review)

        positive_num_item = soup.find_all("a", {"class": "a-size-base a-link-normal see-all"})
        if(len(positive_num_item) < 1):
            num_positive = 'NA'
        else:
            ptr = positive_num_item[0].text.split(' ')
            num_positive = ptr[2]
            num_positive = num_positive.replace(',','')

        print('num_positive')
        items.append(num_positive)

        critical_num_item = soup.find_all("a", {"class": "a-size-base a-link-normal see-all"})
        if(len(positive_num_item) < 1):
            num_critical = 'NA'
        else:
            ptr = critical_num_item[1].text.split(' ')
            num_critical = ptr[2]
            num_critical = num_critical.replace(',','')
        print('num_critical')
        items.append(num_critical)

        return items
    else:
        print('page error')
        return False
    #     return 
    # raise Exception(f"There was an error retrieving contents at {url}")






        

def read_products():
    ''' 
        Accepts a single item list as an argument, proceses through the list and writes all the products into
        a single CSV data file.
    '''
    headers = "itemurls\n"
    filename = "urls.csv"
    itemlll = []
    try: 
        f = open(filename, "r")
        items = f.read()
        itemlll = items.split('\n')
        f.close()

        return itemlll
    except:
        print("There was an error writing to the CSV data file.")
    
if __name__ == "__main__":

    url = 'https://www.amazon.in/product-reviews/B07FB4HBCR'
    item_desc = []
    item_desc = read_products()
    info_array = []
    id = 0
    for item_url in item_desc:
        print(id)
        print(item_url)
        item_info = get_item(item_url)
        # time.sleep(3)
        if item_info:
            print('item_info',item_info)
            info_array.append(item_info)
        id += 1
    col_asin = []
    col_num_review = []
    col_num_positive = []
    col_num_critical = []
    col_name = []
    col_rating = []
    col_rating_num = []
    for item_in in info_array:
        col_asin.append(item_in[0])
        col_num_review.append(item_in[4])
        col_num_positive.append(item_in[5])
        col_num_critical.append(item_in[6])
        col_name.append(item_in[1])
        col_rating.append(item_in[2])
        col_rating_num.append(item_in[3])
    # Create a Pandas dataframe from some data.

    df = pd.DataFrame({'ASIN': col_asin,'Product Name': col_name, 'No of Reviews':col_num_review,
    'Positive':col_num_positive, 'Critical':col_num_critical,
    'Customer rating':col_rating, 'No of ratings':col_rating_num})

    # Create a Pandas Excel writer using XlsxWriter as the engine.
    with pd.ExcelWriter('output.xlsx', engine='xlsxwriter') as writer:

    # Convert the dataframe to an XlsxWriter Excel object.
        df.to_excel(writer, sheet_name='Sheet')

