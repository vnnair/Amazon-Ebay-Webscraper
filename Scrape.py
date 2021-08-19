import re
import os
import csv
import requests
import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk
from pandastable import Table
from bs4 import BeautifulSoup
from selenium import webdriver
from tkinter import filedialog, Text
from PIL import ImageTk, Image


def getEbayInfo(search_term, page_range):
    urls = []
    names = []
    prices = []
    ratings = []
    conditions = []
    shipping = []
    numratings = []
    remove_indices = []
    processed_ratings = []
    search_term = search_term.replace(' ', '+')
    driver = webdriver.Chrome(executable_path='/Users/vishnunair/Desktop/chromedriver')
    url = "https://www.ebay.com/sch/i.html?&_nkw=" + search_term + '&_sacat=0&_pgn={}'
    
    for page in range(1, page_range+1):
        driver.get(url.format(page))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        all_items = soup.find_all('li', attrs={'class': 's-item'})
        for index, item in enumerate(all_items):
            
            name = item.find_all('h3', attrs={'class':"s-item__title"})[0].text
            name2 = item.find('a', attrs={'class':"s-item__link"})
            names.append(name)
            price = item.find('span', attrs={'class':"s-item__price"})
            condition = item.find('span', 'SECONDARY_INFO')
            
            try:
                conditions.append(condition.text)
            except AttributeError:
                conditions.append('')
            
            try:
                prices.append(price.text)
            except AttributeError:
                prices.append('')

            rating = item.find('div', 'x-star-rating')
            shipping_cost = item.find('span', 's-item__shipping s-item__logisticsCost')
            rating_num = item.find('span', 's-item__reviews-count')              
            
            try:
                numratings.append(rating_num.text)
            except AttributeError:
                numratings.append('')
            

            try:
                ratings.append(rating.text)
            except AttributeError:
                ratings.append('')

            try:
                shipping.append(shipping_cost.text)
            except AttributeError:
                shipping.append('$0.00')
            
            
            prod_url = name2.get('href')
            urls.append(prod_url)
                
                
    for index, price in enumerate(prices):
        if price == '' or 'to' in price:
            remove_indices.append(index)
            
    names = [i for j, i in enumerate(names) if j not in remove_indices]
    prices = [i for j, i in enumerate(prices) if j not in remove_indices]
    ratings = [i for j, i in enumerate(ratings) if j not in remove_indices]
    shipping = [i for j, i in enumerate(shipping) if j not in remove_indices]
    numratings = [i for j, i in enumerate(numratings) if j not in remove_indices]
    conditions = [i for j, i in enumerate(conditions) if j not in remove_indices]
    urls = [i for j, i in enumerate(urls) if j not in remove_indices]
    
    
    for i in numratings:
        try: 
            value = i.split(' product')[0]
            processed_ratings.append(value)
        except AttributeError:
            processed_ratings.append(np.nan)
            
    
    result = pd.DataFrame({"Name":names, "Price": prices, "Rating": ratings, "Rating Count": processed_ratings,
                           "Shipping Cost": shipping, "Condition": conditions, "URL": urls})
    result = result.replace(r'^\s*$', np.nan, regex=True)
    result = result.replace({'Free shipping': '$0.00'})
    result['Shipping Cost'] = result['Shipping Cost'].str.replace('+','')
    result['Shipping Cost'] = result['Shipping Cost'].str.replace(' shipping','')
    
    driver.close()
            
    return result



def getAmazonInfo(search_term, page_range):
    global name2
    names = []
    prices = []
    ratings = []
    shipping = []
    numratings = []
    remove_indices = []
    urls = []
    search_term = search_term.replace(' ', '+')
    driver = webdriver.Chrome(executable_path='/Users/vishnunair/Desktop/chromedriver')
    url = 'https://www.amazon.com/s?k=' + search_term + '&page={}'
    
    for page in range(1, page_range+1):
        driver.get(url.format(page))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        all_items = soup.find_all('div', {'data-component-type': 's-search-result'})
        for index, item in enumerate(all_items):
            
            
            price = item.find('span', 'a-price')
            if type(price) == type(None):
                continue
            price = price.find('span', 'a-offscreen')
            
            
            name = item.find_all('a', attrs={'class':"a-link-normal a-text-normal"})[0].text
            name2 = item.find("a", attrs={'class': 'a-link-normal a-text-normal'})
            names.append(name)

            
            try:
                prices.append(price.text)
            except AttributeError:
                prices.append('')

            rating = item.find('i')
            rating_num = item.find('span', {'class': 'a-size-base'})            
            
            try:
                numratings.append(rating_num.text)
            except AttributeError:
                numratings.append('')
            

            try:
                ratings.append(rating.text)
            except AttributeError:
                ratings.append('')

            prod_url = 'https://www.amazon.com/' + name2.get('href')
            urls.append(prod_url)

                
    for index, price in enumerate(prices):
        if price == '':
            remove_indices.append(index)
            
    names = [i for j, i in enumerate(names) if j not in remove_indices]
    prices = [i for j, i in enumerate(prices) if j not in remove_indices]
    ratings = [i for j, i in enumerate(ratings) if j not in remove_indices]
    numratings = [i for j, i in enumerate(numratings) if j not in remove_indices]
    urls = [i for j, i in enumerate(urls) if j not in remove_indices]
    
    
    
    result = pd.DataFrame({"Name":names, "Price": prices, "Rating": ratings, "Rating Count": numratings,
                          "URL": urls})
    result = result.replace(r'^\s*$', np.nan, regex=True)

    driver.close()
            
    return result


def main(search_term, pages):
    
    adrop_rows = []
    edrop_rows = []
    ebay = getEbayInfo(search_term, pages)
    amazon = getAmazonInfo(search_term, pages)
    
    amazon = amazon.fillna('0')
    ebay = ebay.fillna('0')
    
    amazon['Price'] = amazon['Price'].str.replace(',', '')
    amazon['Price'] = amazon['Price'].str.replace(',', '')
    amazon['Price'] = amazon['Price'].str.replace('$', '')
    ebay['Price'] = ebay['Price'].str.replace(',', '')
    ebay['Price'] = ebay['Price'].str.replace(',', '')
    ebay['Price'] = ebay['Price'].str.replace('$', '')
    
    
    amazon['Price'] = pd.to_numeric(amazon['Price'])
    ebay['Price'] = pd.to_numeric(ebay['Price'])

    
    
    
    amazon['Rating Count'] = amazon['Rating Count'].str.replace(',', '')
    for rating in amazon['Rating Count']:
        try:
            float(rating)
        except ValueError:
            ind = amazon[amazon['Rating Count'] == rating].index[0]
            amazon.iloc[ind, 3] = 0
            
    amazon['Rating Count'] = pd.to_numeric(amazon['Rating Count'])
    
    
    ebay['Rating Count'] = ebay['Rating Count'].str.replace(',', '')
    for rating2 in ebay['Rating Count']:
        try:
            float(rating2)
        except ValueError:
            ind = ebay[ebay['Rating Count'] == rating2].index[0]
            ebay.iloc[ind, 3] = 0
    
    
    ebay['Rating Count'] = pd.to_numeric(ebay['Rating Count'])

    amazon['Rating'] = amazon['Rating'].str.replace('out of 5 stars', '')
    ebay['Rating'] = ebay['Rating'].str.replace('out of 5 stars.', '')
    amazon['Rating'] = pd.to_numeric(amazon['Rating'])
    ebay['Rating'] = pd.to_numeric(ebay['Rating'])
    
    
    for item in amazon['Name']:
        for word in search_term.split(' '):
            if word not in item:
                drop_index = amazon[amazon['Name'] == item].index[0]
    adrop_rows.append(drop_index)
    adrop_rows = list(set(adrop_rows))
    
    for item in ebay['Name']:
        for word in search_term.split(' '):
            if word not in item:
                drop_index = ebay[ebay['Name'] == item].index[0]
    edrop_rows.append(drop_index)
    edrop_rows = list(set(edrop_rows))
    
    
    amazon = amazon.drop(adrop_rows)
    amazon = amazon.sort_values(['Rating Count'], ascending = False)
    ebay = ebay.drop(edrop_rows)
    ebay = ebay.sort_values(['Rating Count'], ascending = False)
    
    if (ebay['Rating'] == 0).all() == True:
        ebay = ebay.sort_values(['Price'], ascending = False)
    if (amazon['Rating'] == 0).all() == True:
        amazon = amazon.sort_values(['Price'], ascending = False)
    
    ebay = ebay.head(10)
    amazon = amazon.head(10)
    
    ebay['Price'] = ebay['Price'].map('${:,.2f}'.format)
    amazon['Price'] = amazon['Price'].map('${:,.2f}'.format)
    
    pt1 = Table(lower_frame1, dataframe=amazon)
    pt1.show()
    
    pt2 = Table(lower_frame2, dataframe=ebay)
    pt2.show()

    return ebay, amazon

    
    





root = tk.Tk()
root.config(bg = "white")
root.iconbitmap('investment_grow_money_increase_dollar_business_icon_188469.ico')

canvas = tk.Canvas(root, height=350, width=600)
canvas.pack()



f = tk.Frame(root, bg='#e3b9b3', bd=10)
f.place(relx=.5, rely=0.0, relwidth=1.0, relheight=1.0, anchor='n')

g = tk.Frame(root, bg='#97a989', bd=10)
g.place(relx=.5, rely=0.5, relwidth=1.0, relheight=1.0, anchor='n')


frame = tk.Frame(root, bg='#eee3d6', bd=5)
frame.place(relwidth=0.75, relheight=0.1, relx=0.5, rely=0.1, anchor= 'n')


search_entry = tk.Entry(frame, font=40)
search_entry.place(relwidth=0.325, relheight=1)

page_entry = tk.Entry(frame, font=40)
page_entry.place(relx=.4, relwidth=0.1, relheight=1)

button = tk.Button(frame, text="Compare", padx=10, pady=5, fg='black', bg='#36384c', command = lambda: main(search_entry.get(), int(page_entry.get())))
button.place(relx=0.7, relheight=1, relwidth=0.3)

lower_mainframe = tk.Frame(root, bg='#eee3d6', bd=10)
lower_mainframe.place(relwidth=0.75, relheight=0.7, relx=0.5, rely=0.25, anchor='n')

lower_frame1 = tk.Frame(lower_mainframe, bg='#36384c', width=150, height=200)
lower_frame1.place(relx=0.50, rely=0.02, relwidth=1.0, relheight=0.45, anchor='n')


lower_frame2 = tk.Frame(lower_mainframe, bg='#36384c', width=150, height=200)
lower_frame2.place(relx=0.50, rely=0.52, relwidth=1.0, relheight=0.45, anchor='n')


root.mainloop()


