import time
import subprocess
import pyautogui
import os
import io
import logging
import sys
from typing import Optional, Tuple
import psutil
from PIL import Image

# Set Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(os.path.dirname(__file__), "key", "quebra-captcha-b2266280152a.json")

from google.cloud import vision
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException

# Configurações
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
USER_DATA_DIR = r"C:\ChromeProfile"
CHROME_DEBUG_PORT = 9222
SCREENSHOTS_DIR = "screenshots"
WAIT_TIMEOUT = 10
MAX_RETRIES = 5
CLICK_DELAY = 0.3
CAPTCHA_CONFIDENCE = 0.9

# IDs dos elementos
CAPTCHA_PANEL_ID = "ctl00_cphContent_Panel2"
CAPTCHA_INPUT_ID = "ctl00_cphContent_txtCaptcha"
CAPTCHA_BUTTON_ID = "ctl00_cphContent_btnConfirmarCaptcha"
CAPTCHA_ERROR_ID = "ctl00_cphContent_lblAviso"
EMAIL_INPUT_NAME = "ctl00$aplExterna$txtEmailLogin"
ESTADO_SELECT_NAME = "ctl00$aplExterna$ddlEstadoEmissao"
LOGIN_BUTTON_NAME = "ctl00$aplExterna$btnEntrar"

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("automation.log")
    ]
)

def fechar_browser_existente():
    """Fecha todas as instâncias existentes do Chrome"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'chrome.exe' in proc.info['name'].lower():
                logging.info(f"Fechando Chrome com PID {proc.info['pid']}")
                proc.terminate()
                proc.wait(timeout=5)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

def iniciar_chrome(url):
    """Inicia uma nova instância do Chrome"""
    fechar_browser_existente()
    logging.info("Iniciando Chrome...")

    comando = [
        CHROME_PATH,
        f"--remote-debugging-port={CHROME_DEBUG_PORT}",
        f"--user-data-dir={USER_DATA_DIR}",
        "--incognito",
        "--disable-session-crashed-bubble",
        "--no-first-run",
        url
    ]

    try:
        subprocess.Popen(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        time.sleep(5)  # Aguarda o Chrome iniciar
        return True
    except Exception as e:
        logging.error(f"Erro ao iniciar Chrome: {e}")
        return False

def conectar_chrome():
    """Conecta ao Chrome em modo de depuração"""
    chrome_options = webdriver.ChromeOptions()
    chrome_options.debugger_address = f"localhost:{CHROME_DEBUG_PORT}"
    
    try:
        return webdriver.Chrome(options=chrome_options)
    except WebDriverException as e:
        logging.error(f"Erro ao conectar ao Chrome: {e}")
        return None

def get_captcha_coordinates(driver, 
                          padding_top=5,
                          padding_right=10,
                          padding_bottom=5,
                          padding_left=10,
                          extra_width=0,
                          extra_height=0,
                          crop_top=0,
                          crop_left=0):
    """Obtém as coordenadas do elemento do captcha"""
    try:
        captcha_element = driver.find_element(By.ID, CAPTCHA_PANEL_ID)
        location = captcha_element.location
        size = captcha_element.size
        
        x = location['x'] - padding_left + crop_left
        y = location['y'] - padding_top + crop_top
        width = size['width'] + padding_left + padding_right + extra_width - crop_left
        height = size['height'] + padding_top + padding_bottom + extra_height - crop_top
        
        return (
            max(0, int(x)),
            max(0, int(y)),
            max(10, int(width)),
            max(10, int(height))
        )
    except Exception as e:
        logging.error(f"Erro ao obter coordenadas do captcha: {e}")
        return None

def extract_text_from_image(image_path):
    """Extrai texto de uma imagem usando Google Vision API"""
    try:
        client = vision.ImageAnnotatorClient()
        
        with io.open(image_path, 'rb') as image_file:
            content = image_file.read()
        
        image = vision.Image(content=content)
        response = client.text_detection(image=image)

        if response.error.message:
            raise Exception(f"Google Vision API Error: {response.error.message}")
        
        return response.text_annotations[0].description.strip() if response.text_annotations else ""
    except Exception as e:
        logging.error(f"Erro ao extrair texto da imagem: {e}")
        return ""

def capture_captcha_screenshot(driver, output_path="captcha.png", **kwargs):
    """Captura screenshot do captcha"""
    try:
        coords = get_captcha_coordinates(driver, **kwargs)
        if not coords:
            raise Exception("Não foi possível obter as coordenadas do captcha")
        
        x, y, width, height = coords
        screenshot = pyautogui.screenshot(region=(x, y, width, height))
        screenshot.save(output_path)
        
        logging.info(f"Captcha capturado - Arquivo: {output_path} | Posição: ({x}, {y}) | Tamanho: {width}x{height}")
        return output_path
    except Exception as e:
        logging.error(f"Erro ao capturar captcha: {e}")
        return None

def resolver_captcha(driver):
    """Resolve o captcha"""
    for tentativa in range(1, MAX_RETRIES + 1):
        try:
            WebDriverWait(driver, WAIT_TIMEOUT).until(
                EC.visibility_of_element_located((By.ID, CAPTCHA_PANEL_ID))
            )

            img_path = capture_captcha_screenshot(
                driver,
                output_path="screenshot.png",
                padding_top=5,
                padding_right=10,
                padding_bottom=5,
                padding_left=10,
                extra_width=-20,
                extra_height=10,
                crop_top=3,
                crop_left=2
            )

            if not img_path:
                raise Exception("Falha ao capturar captcha")

            captcha_text = extract_text_from_image(img_path)
            if not captcha_text:
                raise Exception("Texto do captcha não encontrado")

            password = captcha_text.split("\n")[0].replace(" ", "")
            logging.info(f"Senha extraída: {password}")

            captcha_input = driver.find_element(By.ID, CAPTCHA_INPUT_ID)
            captcha_input.clear()
            captcha_input.send_keys(password)

            driver.find_element(By.ID, CAPTCHA_BUTTON_ID).click()
            time.sleep(3)

            erro = driver.find_elements(By.ID, CAPTCHA_ERROR_ID)
            if erro and "Texto inválido" in erro[0].text:
                logging.warning(f"Captcha inválido. Tentativa {tentativa} de {MAX_RETRIES}")
                continue

            return True
        except Exception as e:
            logging.error(f"Erro ao resolver captcha (Tentativa {tentativa}): {e}")

    logging.error(f"Falha ao resolver captcha após {MAX_RETRIES} tentativas.")
    return False

def digitar_senha(senha):
    """Digita a senha usando reconhecimento de imagem"""
    try:
        for char in senha:
            pos = pyautogui.locateCenterOnScreen(
                f"{SCREENSHOTS_DIR}/{char}.png",
                confidence=CAPTCHA_CONFIDENCE
            )
            if pos:
                pyautogui.click(pos)
                time.sleep(CLICK_DELAY)
            else:
                logging.error(f"Tecla '{char}' não encontrada.")
                return False
        return True
    except Exception as e:
        logging.error(f"Erro ao digitar senha: {e}")
        return False

def confirmar_login():
    """Confirma o login clicando no botão entrar"""
    try:
        pos = pyautogui.locateCenterOnScreen(
            f"{SCREENSHOTS_DIR}/entrar.png",
            confidence=CAPTCHA_CONFIDENCE
        )
        if pos:
            pyautogui.click(pos)
            return True
        else:
            logging.error("Botão 'Entrar' não encontrado.")
            return False
    except Exception as e:
        logging.error(f"Erro ao confirmar login: {e}")
        return False

def main():
    """Função principal"""
    if len(sys.argv) != 5:
        print("Uso: python main.py <url> <email> <senha> <estado>")
        sys.exit(1)

    url = sys.argv[1]
    email = sys.argv[2]
    senha = sys.argv[3]
    estado = sys.argv[4]

    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

    try:
        logging.info("Tentativa 1 de 5")
        
        # Inicia e conecta ao Chrome
        if not iniciar_chrome(url):
            raise Exception("Falha ao iniciar o Chrome")
            
        driver = conectar_chrome()
        if not driver:
            raise Exception("Falha ao conectar ao Chrome")

        # Preenche o formulário inicial
        email_input = WebDriverWait(driver, WAIT_TIMEOUT).until(
            EC.presence_of_element_located((By.NAME, EMAIL_INPUT_NAME))
        )
        email_input.clear()
        email_input.send_keys(email)

        estado_select = Select(driver.find_element(By.NAME, ESTADO_SELECT_NAME))
        estado_select.select_by_visible_text(estado)

        driver.find_element(By.NAME, LOGIN_BUTTON_NAME).click()

        # Resolve o captcha
        if not resolver_captcha(driver):
            raise Exception("Falha ao resolver o captcha")

        # Digita a senha
        if not digitar_senha(senha):
            raise Exception("Falha ao digitar a senha")

        # Confirma o login
        if not confirmar_login():
            raise Exception("Falha ao confirmar o login")

        logging.info("Login realizado com sucesso!")
        sys.exit(0)

    except Exception as e:
        logging.error(f"Erro durante a execução: {e}")
        sys.exit(1)

    finally:
        if 'driver' in locals():
            driver.quit()

if __name__ == "__main__":
    main()