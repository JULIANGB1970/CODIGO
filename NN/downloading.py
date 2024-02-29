from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import re
import time
import pandas as pd
import os



driver = webdriver.Chrome()


url = ""  #Poner aqui la página de inicio de listado de las ofertas


driver.get(url)
driver.maximize_window()



aceptar_cookies = driver.find_element(By.ID,"cmplz-cookiebanner-container")




if aceptar_cookies :

   
    try:
        boton_cookies = driver.find_element(By.XPATH,"//*[@id='cmplz-cookiebanner-container']/div/div[6]/button[1]")
        boton_cookies.click()

    except:
        pass



driver.find_element(By.XPATH,"//*[@id='menu-item-84537']/a").click()


WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="row-unique-1"]/div/div/div/div/div/div/div/div/div/ul')))



driver.implicitly_wait(5)

lies = driver.find_elements(By.XPATH, "//*[contains(@class, 'job_listing type-job_listing status-publish has-post-thumbnail hentry')]")



df = pd.DataFrame(columns=['enlace','empleo','num_oferta','fecha','location', 'publication'])

lista_df=[]

for e in lies:

    enlace = e.find_element(By.TAG_NAME, "a").get_attribute("href")
    lista = e.text.splitlines()
    empleo = lista[0]
    num_oferta = re.findall('\d{4,5}', lista[1])[0]
    fecha = lista[1][-10:]
    location = lista[2]
    publication = lista[3]

    lista_df.extend([enlace,empleo, num_oferta, fecha, location, publication]) 

    
    df.loc[len(df)] = lista_df

    lista_df.clear()



print(df)
df.to_excel("principal.xlsx")

lista_df= []
df_detalle = pd.DataFrame(columns=['num_oferta','posicion', 'necesitas', 'valorable','informacion', 'ofrecemos', 'otros', 'contenido'])

for index, row in df.iterrows():

    enlace= row['enlace']
    num_oferta= row['num_oferta']
    driver.get(enlace)
    
    
    
    contenido = driver.find_element(By.CLASS_NAME, "job_description").text
    

    if re.search(r'^([\s\S]*?)¿QUE NECESITAS SABER\?', contenido):
        posicion = re.search(r'^([\s\S]*?)¿QUE NECESITAS SABER\?', contenido).group(1).strip()
    else :
        posicion = driver.find_element(By.CLASS_NAME, 'post-title').text

    
    if re.search(r'¿QUE NECESITAS SABER\?([\s\S]*?)VALORABLE:', contenido):
        necesitas= re.search(r'¿QUE NECESITAS SABER\?([\s\S]*?)VALORABLE:', contenido).group(1).strip()
    else:
        necesitas= "XXXX"

    if re.search(r'VALORABLE:([\s\S]*?)INFORMACION ADICIONAL:', contenido):
        valorable =re.search(r'VALORABLE:([\s\S]*?)INFORMACION ADICIONAL:', contenido).group(1).strip()
    else:
        valorable = "XXXX"
    

    if re.search(r'INFORMACION ADICIONAL:([\s\S]*?)¿QUÉ OFRECEMOS?', contenido):
        informacion=re.search(r'INFORMACION ADICIONAL:([\s\S]*?)¿QUÉ OFRECEMOS?', contenido).group(1).strip()
    else:
        informacion = "XXXX"
    
    if re.search(r'¿QUÉ OFRECEMOS\?([\s\S]*?)$', contenido):
        ofrecemos = re.search(r'¿QUÉ OFRECEMO\S?([\s\S]*?)$', contenido).group(1).strip()
    else:
        ofrecemos = "XXXX"
    
    if re.search(r'(.*)$', contenido):
        otros=re.search(r'(.*)$', contenido).group(1).strip()
    else:
        otros = "XXXX"
    
    
    ofrecemos= re.sub(otros, "", ofrecemos)
  
    

    lista_df.extend([num_oferta, posicion, necesitas, valorable, informacion, ofrecemos, otros, contenido])   
    
    df_detalle.loc[len(df_detalle)] = lista_df
    

    lista_df.clear()

driver.quit()


print(df_detalle)
df_detalle.to_excel("detalle_ofertas.xlsx")


merged = pd.merge(df, df_detalle, on='num_oferta')
merged.to_excel("union.xlsx")

os.system(r'start "" /max EXCEL.EXE union.xlsx')
    




















time.sleep(600)


