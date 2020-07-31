#!/usr/bin/env python
# coding: utf-8

# In[25]:


# Libraries

from selenium import webdriver # exe to simulate browser
from selenium.webdriver.common.keys import Keys # to send data for website
from webdriver_manager.chrome import ChromeDriverManager # to install exe
from selenium.webdriver.chrome.options import Options # set options to broser
from selenium.webdriver.support.ui import WebDriverWait # wait conditions to scrap data
from selenium.webdriver.support import expected_conditions as EC # set conditions
from selenium.webdriver.common.by import By # way to scrap data
from os import remove
import pandas as pd # read and write excel
import datetime # set today
import time


# set Headless tab
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument("--window-size=1920,1080")

# set the day
hoje = datetime.datetime.now()
hoje =hoje.strftime("%d%m%Y")


# In[26]:


def connect_page():
    # set drive
    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(),options=chrome_options) # install driver
    # get the page
    driver.get("https://www.anbima.com.br/pt_br/informar/sistema-reune.htm") # select page REUNE
    return driver


# In[27]:


def connect_page_web():
    # set drive
    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install())
    # get the page
    driver.get("https://www.anbima.com.br/pt_br/informar/sistema-reune.htm")
    return driver


# In[28]:


def set_iframe(driver):
    # get the iframes
    frame = driver.find_elements_by_tag_name("iframe") 
    # choose iframe
    driver.switch_to.frame(frame[0])
    return driver


# In[29]:


def choose_date(data,driver):
    # Find date element
    wait = WebDriverWait(driver, 10)
    wait.until(EC.element_to_be_clickable((By.NAME, "Dt_Ref")))
    elem = driver.find_element_by_name('Dt_Ref')
    # Send keys to data element
    elem.clear()
    elem.send_keys(data)


# In[30]:


def choose_index(index,driver):
    # find index element
    wait = WebDriverWait(driver, 10)
    wait.until(EC.element_to_be_clickable((By.TAG_NAME, "option")))
    all_options = driver.find_elements_by_tag_name("option")
    # choose index element
    for option in all_options:
        #print("Value is: %s" % option.get_attribute("value"))
        if option.get_attribute("value") == index:
            option.click()


# In[31]:


def choose_visualization(driver):
    wait = WebDriverWait(driver, 10)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='escolha']")))
    radio = driver.find_elements_by_name("escolha")
    radio[1].click()


# In[32]:


def choose_ext(ext,driver):
    # choose to extension
    wait = WebDriverWait(driver, 10)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[value= '" + ext +  "']")))
    driver.find_element_by_css_selector("input[type='radio'][value= '" + ext +  "']").click()


# In[33]:


def donwload_file(driver):
    # Donwload the file
    wait = WebDriverWait(driver, 10)
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "img[name='Consultar']")))
    driver.find_element_by_css_selector("img[name='Consultar']").click()


# In[34]:


def read_clean_write(hj):
    # read data
    data = pd.read_csv('REUNE_Acumulada_%s.csv'%(hj),
                           skiprows=[i for i in range(0,3)],
                           encoding="Latin-1",sep = ";")
    # clean data
    data_clean = data[data.columns[~data.columns.isin(['Unnamed: 1'])]]
    #data_clean["data"] = datetime.date.today()
    data_clean["data"] = datetime.datetime.strptime(hj,"%d%m%Y")
    data_clean_filter = data_clean[['CETIP','Tipo','Taxa Média','Preço Médio','Faixa de Volume','data']]
    # write data
    data_old = pd.read_excel('base.xlsx')
    data_new = data_old.append(data_clean_filter)
    data_new.to_excel('base.xlsx',index=False)
    # removinda old data
    remove('REUNE_Acumulada_%s.csv'%(hj))


# In[130]:


def read_clean_write_loop(hj):
    data = pd.read_csv('REUNE_Acumulada_%s.csv'%(hj),
                           skiprows=[i for i in range(0,3)],
                           encoding="Latin-1",sep = ";")
    # clean data
    data_clean = data[data.columns[~data.columns.isin(['Unnamed: 1'])]]
    data_clean["data"] = datetime.datetime.strptime(hj,"%d%m%Y")
    data_clean_filter = data_clean[['CETIP','Tipo','Taxa Média','Preço Médio','Faixa de Volume','data']]
    # removinda old data
    remove('REUNE_Acumulada_%s.csv'%(hj))
    return data_clean_filter


# In[36]:


def get_index(data,index="CRA",ext = "csv"):
    # get page
    driver = connect_page()
    print("get page ok")
    # set iframe
    driver = set_iframe(driver)
    print("set frame ok")
    # choose data
    choose_date(data,driver)
    print("choose data ok")
    # choose index
    choose_index(index,driver)
    print("choose index ok")
    # choose visualization
    choose_visualization(driver)
    print("choose visu ok")
    # choose ext
    choose_ext(ext,driver)
    # download
    donwload_file(driver)
    # Sleep code
    time.sleep(5)
    # join the database
    try:
        read_clean_write(data)
    except:
        print("Nao ha dados para esse dia")


# In[131]:


def get_index_loop(data,index="CRA",ext = "csv"):
    # get page
    driver = connect_page()
    # set iframe
    driver = set_iframe(driver)
    # choose data
    choose_date(data,driver)
    # choose index
    choose_index(index,driver)
    # choose visualization
    choose_visualization(driver)
    # choose ext
    choose_ext(ext,driver)
    # download
    donwload_file(driver)
    # Sleep code
    time.sleep(5)
    # join the database
    try:
        data_clean = read_clean_write_loop(data)
        return data_clean
    except:
        print("Nao ha dados para esse dia")


# In[151]:


def loop_data(start_date,end_date,tipo):
    datas = pd.date_range(start=start_date,end=end_date)
    data_all = {'CETIP': [],
               'Tipo' : [],
                'Taxa Média': [],
               'Preço Médio': [],
               'Faixa de Volume':[],
               'data':[]}
    data_all = pd.DataFrame.from_dict(data_all)
    for data in datas:
        current_data = data.strftime("%d%m%Y")
        data_gen = get_index_loop(data = current_data, index = tipo)
        data_all = pd.concat([data_all,data_gen])
    data_all.to_excel('last_days.xlsx',index=False)

