# from pyrogram import Client
from selenium import webdriver
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from src.Telegram import Telegram
from time import sleep
import logging
import json
from screeninfo import get_monitors

logging.basicConfig(level=logging.INFO, filename='app.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')

class Main:

    def carregar_dados(self):
        self.telegram = Telegram()
        self.telegram.start()
        self.config = json.load(open('config.json'))
        with open('ultima_mensagem.txt', 'r') as file:
            self.ultima_mensagem = file.read()
            file.close()

    def start(self):
        self.options = uc.ChromeOptions()
        self.options.add_argument("--start-maximized")
        self.options.add_argument("--disable-infobars")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        self.driver = uc.Chrome(options=self.options)
        
        monitor = get_monitors()[0]
        screen_width = monitor.width
        screen_height = monitor.height
        width = int(screen_width * 0.7)
        height = int(screen_height * 1)
        self.driver.set_page_load_timeout(10)
        self.driver.implicitly_wait(10)
        self.driver.set_window_size(width, height)
        self.driver.set_window_position(int(screen_width * 0.3), 0)
        self.driver.get("https://donald.bet/")

    def login(self):
        try:
            logging.info(f'login') 
            sleep(5)
            self.driver.find_element(By.CSS_SELECTOR,'.btn.btn-login.default').click()
            sleep(3)
            self.driver.execute_script("window.open('https://donald.bet/', '_blank');")
            sleep(10)
            self.driver.switch_to.window(self.driver.window_handles[0])
            self.driver.close()
            sleep(1)
            self.driver.switch_to.window(self.driver.window_handles[0])
            sleep(1)
            remail = self.driver.find_element(By.CSS_SELECTOR,'input[name="email"]')
            email = self.driver.find_element(By.CSS_SELECTOR, 'span.label')
            email.click()
            remail.send_keys(self.config['username'])
            self.driver.execute_script(f"arguments[0].value = '{self.config['username']}'", remail)
            sleep(2)
            senha = self.driver.find_element(By.CSS_SELECTOR,'input#password')
            senha.click()
            senha.clear()
            senha.send_keys(self.config['password'])
            sleep(2)
            senha.send_keys(Keys.ENTER)
            sleep(2)
        except Exception as err:
                logging.error(f'login -> {err}')
                raise Exception('Parando bot')

    def pegar_ultimos_resultados(self):
        try:
            resultados = self.driver.find_elements(By.CSS_SELECTOR, '.result-history .payouts-block app-bubble-multiplier')[0:10]
            resultados = [float(resultado.text.strip().replace('x', '')) for resultado in resultados]
            return resultados[0:10]
        except: []
        
    def entrando_aviator(self):
        sleep(3)
        self.driver.get("https://donald.bet/casino/spribe/aviator")
        sleep(3)
        try: self.driver.find_elements(By.CSS_SELECTOR, 'div[role="dialog"] button')[0].click()
        except: pass
        sleep(5)
        iframe = self.driver.find_elements(By.CSS_SELECTOR, 'iframe#gameIframe')[0]
        self.driver.switch_to.frame(iframe)
        sleep(1)
        self.driver.find_elements(By.CSS_SELECTOR, '.navigation-switcher')[1].find_elements(By.CSS_SELECTOR, 'button')[1].click()
        sleep(2)
        self.driver.find_elements(By.CSS_SELECTOR, ".controls .controls .input-switch.off")[1].click()
        sleep(2)
    
    def verificar_resultados(self, odd):
        ultimos = self.pegar_ultimos_resultados()
        while self.ultimos == ultimos:
            sleep(1)
            ultimos = self.pegar_ultimos_resultados()
        self.ultimos = ultimos
        if self.ultimos[0] >= odd: return True
        sleep(5)
        return False

    def mudar_valor_input(self, control,indice, valor):
        control.find_elements(By.CSS_SELECTOR, 'input')[indice].click()
        control.find_elements(By.CSS_SELECTOR, 'input')[indice].send_keys(Keys.CONTROL + 'a' + Keys.BACKSPACE)
        control.find_elements(By.CSS_SELECTOR, 'input')[indice].send_keys(valor)

    def apostar(self, odd):
        control = self.driver.find_elements(By.CSS_SELECTOR,'.controls .controls')[0]
        self.mudar_valor_input(control, 1, float(odd))
        for gale in range(self.config['martingale']+1):
            valor_aposta = round(float(self.config['valor_aposta']) * (2**gale), 2)
            self.mudar_valor_input(control, 0, valor_aposta)            
            sleep(1)
            control.find_elements(By.CSS_SELECTOR, 'button.btn-success')[0].click()
            sleep(1)
            if self.verificar_resultados(odd):
                    break
       
    def iniciar_telas(self):
        try:
            logging.info(f'iniciar_telas') 
            self.start()
            self.login()
            self.entrando_aviator()
        except Exception as err:
            logging.error(f'iniciar_telas -> {err}')
            raise Exception('Erro ao iniciar telas')
                   
    def main(self):
        try:
            self.carregar_dados()
            self.iniciar_telas()
            sleep(5)
            while True:
                mensagem = self.telegram.buscar_ultima_mensagem()
                if mensagem:
                    self.ultimos = self.pegar_ultimos_resultados()
                    self.apostar(mensagem)
                
                sleep(1)
        except:
            self.driver.quit()
            self.telegram.driver.quit()
            exit()

if __name__ == '__main__':
    main = Main()
    main.main()