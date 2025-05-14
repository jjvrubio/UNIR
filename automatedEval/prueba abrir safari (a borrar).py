from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Iniciar Safari
driver = webdriver.Safari()

# Abrir una página
driver.get("https://www.google.com")
time.sleep(3)

print("Safari abierto correctamente.")
