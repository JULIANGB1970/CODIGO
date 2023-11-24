from datetime import date, datetime, timedelta
import pandas as pd
from pandas import json_normalize 
import requests
import itertools
import pendulum
from itertools import chain
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
import time

driver = webdriver.Firefox()
driver.get('https://www.zaragoza.es/ciudad/ticketing/verNuevaQuejaAnonima_Ticketing')


drop= Select(driver.find_element(By.ID, 'service_code'))
options = drop.options

lista_servicios = []

for i in range(1,len(options) ):

    drop.select_by_index(i)

    try:
        
        cadena =  "[data-dependent-parent='" + drop.options[i].text +"']"
       
        subx= Select(driver.find_element(By. CSS_SELECTOR, cadena))
        optionx = subx.options
      
        for index in range(0, len(optionx)-1):
          
            if index == 0:
                codigo = optionx[index].get_attribute('value')
                subcodigo= optionx[index].get_attribute('value')
                categoria = drop.options[i].text
                subcategoria = categoria
            else:    
                codigo = codigo
                subcodigo= optionx[index].get_attribute('value')
                categoria = drop.options[i].text
                subcategoria = optionx[index].text

            print(codigo, subcodigo, categoria, subcategoria)
            list_tmp = [codigo, subcodigo, categoria, subcategoria]
            lista_servicios.append(list_tmp)



    except Exception as error:
       
        codigo = drop.options[i].get_attribute('value')
        subcodigo= codigo
        categoria = drop.options[i].text
        subcategoria = drop.options[i].text
        print("unicos", codigo, subcodigo, categoria, subcategoria)
        list_tmp = [codigo, subcodigo, categoria, subcategoria]
        lista_servicios.append(list_tmp)


        pass

    

service_ayto= pd.DataFrame(lista_servicios, columns = ['codigo', 'subcodigo', 'categoria', 'subcategoria'])
print(service_ayto.head)
service_ayto.to_csv("service_ayto.csv", index = False)
service_ayto.to_excel("service_ayto.xlsx", index = False)