import os
from typing import Final

# Diretórios
ROOT_DIR: Final = os.path.dirname(os.path.abspath(__file__))
SCREENSHOTS_DIR: Final = os.path.join(ROOT_DIR, "screenshots")
CREDENTIALS_DIR: Final = os.path.join(ROOT_DIR, "key")

# Google Vision API
GOOGLE_CREDENTIALS: Final = os.path.join(CREDENTIALS_DIR, "quebra-captcha-b2266280152a.json")

# Chrome
CHROME_PATH: Final = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
USER_DATA_DIR: Final = r"C:\ChromeProfile"
CHROME_DEBUG_PORT: Final = 9222

# Timeouts e Tentativas
WAIT_TIMEOUT: Final = 10
MAX_RETRIES: Final = 5
CLICK_DELAY: Final = 0.3

# Captcha
CAPTCHA_CONFIDENCE: Final = 0.9
CAPTCHA_PANEL_ID: Final = "ctl00_cphContent_Panel2"
CAPTCHA_INPUT_ID: Final = "ctl00_cphContent_txtCaptcha"
CAPTCHA_BUTTON_ID: Final = "ctl00_cphContent_btnConfirmarCaptcha"
CAPTCHA_ERROR_ID: Final = "ctl00_cphContent_lblAviso"

# Elementos da página
EMAIL_INPUT_NAME: Final = "ctl00$aplExterna$txtEmailLogin"
ESTADO_SELECT_NAME: Final = "ctl00$aplExterna$ddlEstadoEmissao"
LOGIN_BUTTON_NAME: Final = "ctl00$aplExterna$btnEntrar" 