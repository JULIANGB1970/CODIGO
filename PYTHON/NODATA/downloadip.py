#este codigo renueva automaticamente la direccion ip, probaré a hacer scrapping
#Lo he sacado de aquí:
#https://infosecwriteups.com/configuring-tor-with-python-1a90fc1c246f
#y lo he ajustado con esto: hay que cambiar el servicio (controlport) en Windows
#https://stackoverflow.com/questions/45972637/getting-tor-controlport-to-work


import time
import requests
from fake_useragent import UserAgent
from stem import Signal
from stem.control import Controller
proxies = {
    'http': 'socks5://127.0.0.1:9150',
    'https': 'socks5://127.0.0.1:9150'
}
print("Changing IP Address in every 10 seconds....\n\n")
while True:
    headers = { 'User-Agent': UserAgent().random }
    time.sleep(10)
    
    with Controller.from_port(port = 9051) as c:
        
        c.authenticate()
        c.signal(Signal.NEWNYM)
        print(f"Your IP is : {requests.get('https://ident.me', proxies=proxies, headers=headers).text}  ||  User Agent is : {headers['User-Agent']}")