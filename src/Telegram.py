from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from time import sleep
import subprocess
import platform
from screeninfo import get_monitors


class Telegram:
    def start(self):
        os_name = platform.system()
        if os_name == "Windows":
            subprocess.run("taskkill /f /im chrome.exe", shell=True)
            subprocess.Popen(
                '"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --log-level=3 --remote-debugging-port=9222', shell=True)
        elif os_name == "Linux":
            subprocess.run("pkill chrome", shell=True)
            subprocess.Popen(
                'google-chrome --log-level=3 --remote-debugging-port=9222', shell=True)
        self.options = webdriver.ChromeOptions()
        self.options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        self.options.add_argument("--start-maximized")
        self.options.add_argument("disable-infobars")
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--no-sandbox")
        self.driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=self.options)
        monitor = get_monitors()[0]
        screen_width = monitor.width
        screen_height = monitor.height
        width = int(screen_width * 0.3)
        height = int(screen_height * 1)
        self.driver.set_window_size(width, height)
        self.driver.set_window_position(0, 0)
        self.driver.set_page_load_timeout(10)
        self.driver.implicitly_wait(10)
        self.driver.get("https://web.telegram.org/k/#-2062201126")        
        sleep(3)
    
    def buscar_ultima_mensagem(self):
        ultima_mensagem = self.driver.find_elements(By.CSS_SELECTOR, '.message')[-1] 
        if ultima_mensagem:
            ultima_mensagem_text = ultima_mensagem.text
            odd = ''
            if "AVIATOR CONFIRMADO" in ultima_mensagem_text.upper():
                for linha in ultima_mensagem_text.split('\n'):
                    if 'saia' in linha.lower(): odd = float(linha.split('Saia em')[-1].strip())
                return odd
        return None

    