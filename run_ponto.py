from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import holidays
import yagmail
import datetime

# Defina os feriados do Brasil
br_holidays = holidays.Brazil()

def sendEmail(hour, message):
    # Configurações do Gmail
    email_origem = "guirossan@gmail.com"
    senha = "eskgvbgpeqpwddpq"  # Consider using environment variables for sensitive data

    # Destinatário e mensagem
    email_destino = "gr.rossan@gmail.com"
    assunto = "Aviso Importante - Ponto"
    corpo = f"Ponto Batido com {message} - {hour}"
    try:
        yag = yagmail.SMTP(email_origem, senha)
        yag.send(email_destino, assunto, corpo)
        print("E-mail enviado com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar o e-mail: {e}")

def baterPonto():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    
    chrome = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    chrome.implicitly_wait(30)  # Reduced from 1000 to a more reasonable value

    try:
        #  Logando no sistema
        chrome.get("https://meurh.sinqia.com.br:8079/01/#/login")

        user_name_input = chrome.find_element(By.CSS_SELECTOR, "input[name='user']")
        user_name_input.send_keys("50979862884")

        password_input = chrome.find_element(By.CSS_SELECTOR, "po-field-container input[name='password']")
        password_input.send_keys("013084")

        chrome.find_element(By.CSS_SELECTOR, "po-button button").click()

        # Batendo o ponto
        WebDriverWait(chrome, 30).until(lambda driver: driver.execute_script("return document.readyState") == "complete")

        # Espera aparecer o sub titulo EVENTO para navegar para pagina de bater ponto
        WebDriverWait(chrome, 30).until(EC.presence_of_element_located((By.CLASS_NAME, "po-font-subtitle")))
        chrome.execute_script("localStorage.setItem('modalAlreadyDisplayed', 'true');")

        # Entra na tela de bater o ponto
        chrome.get("https://meurh.sinqia.com.br:8079/01/#/timesheet/clockingsGeo/register")

        # Bate o ponto
        botao_ponto = WebDriverWait(chrome, 20).until(
            EC.element_to_be_clickable((By.ID, "btn-app-swipe-clocking-register"))
        )

        actions = ActionChains(chrome)
        actions.double_click(botao_ponto).perform()
        print("Ponto batido com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao bater ponto: {e}")
        return False
    finally:
        chrome.quit()

def job():
    hoje = datetime.date.today()
    if hoje in br_holidays:
        print(f"Hoje é feriado ({br_holidays[hoje]}), job não será executado.")
    else:
        print(f"Job executado em {datetime.datetime.now()}")
        success = baterPonto()
        if success:
            sendEmail(datetime.datetime.now(), "Sucesso")
        else:
            sendEmail(datetime.datetime.now(), "Erro")
        # Removed extra 'success' line that was causing syntax error

if __name__ == "__main__":
    job()
