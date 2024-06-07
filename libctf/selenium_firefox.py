from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile
from webdriver_manager.firefox import GeckoDriverManager
import asyncio

options = webdriver.FirefoxOptions()
options.add_argument("--headless")
options.binary_location = "/usr/bin/firefox"
options.set_preference("javascript.enabled", True)
options.set_preference('network.dns.disableIPv6', True)
options.add_argument('--window-size=1920,1080')

async def take_screenshot(url):
    try:
        driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
        driver.get(url)
        print("Connected !")
        driver.implicitly_wait(10)
        driver.save_screenshot("team_score.png")
    
    except Exception as e:
        print(e)
        
    finally:    
        driver.quit()

