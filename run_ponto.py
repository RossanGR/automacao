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
    except Exception as e:
        print(f"Erro ao enviar o e-mail: {e}")

def baterPonto():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--window-size=1920,1080')  # Definir tamanho da janela
    
    chrome = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    chrome.implicitly_wait(30)

    try:
        # Logando no sistema
        chrome.get("https://meurh.sinqia.com.br:8079/01/#/login")
        print("Página de login aberta")
        
        # Esperar a página carregar completamente
        WebDriverWait(chrome, 30).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='user']"))
        )
        
        # Login com explícita espera por cada elemento
        user_name_input = WebDriverWait(chrome, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='user']"))
        )
        user_name_input.clear()
        user_name_input.send_keys("50979862884")
        print("Usuário inserido")
        
        password_input = WebDriverWait(chrome, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='password']"))
        )
        password_input.clear()
        password_input.send_keys("013084")
        print("Senha inserida")
        
        # Clicar no botão de login e esperar
        login_button = WebDriverWait(chrome, 30).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "po-button button.po-button-primary"))
        )
        login_button.click()
        print("Botão de login clicado")
        
        # Aguardar carregamento da página inicial
        WebDriverWait(chrome, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, "po-font-subtitle"))
        )
        print("Página inicial carregada")
        
        # Fechar possíveis modais
        chrome.execute_script("localStorage.setItem('modalAlreadyDisplayed', 'true');")
        
        # Tirar um screenshot para debug
        chrome.save_screenshot("/tmp/pagina_inicial.png")
        
        # Navegar diretamente para a página de ponto
        chrome.get("https://meurh.sinqia.com.br:8079/01/#/timesheet/clockingsGeo/register")
        print("Navegando para página de registro de ponto")
        
        # Esperar a página de registro carregar completamente
        WebDriverWait(chrome, 60).until(
            lambda driver: driver.execute_script("return document.readyState") == "complete"
        )
        
        # Tirar screenshot da página de ponto
        chrome.save_screenshot("/tmp/pagina_ponto.png")
        
        # Esperar pelo botão de ponto e tentar diferentes abordagens
        try:
            # Primeira tentativa: ID direto
            botao_ponto = WebDriverWait(chrome, 30).until(
                EC.element_to_be_clickable((By.ID, "btn-app-swipe-clocking-register"))
            )
            print("Botão de ponto encontrado por ID", botao_ponto)
        except:
            try:
                # Segunda tentativa: seletor CSS mais genérico
                botao_ponto = WebDriverWait(chrome, 30).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "[id*='btn-app-swipe-clocking']"))
                )
                print("Botão de ponto encontrado por seletor CSS parcial")
            except:
                # Terceira tentativa: por texto
                botao_ponto = WebDriverWait(chrome, 30).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Registrar') or contains(text(), 'Ponto')]"))
                )
                print("Botão de ponto encontrado por texto")
        
        # Tentar diferentes interações com o botão
        try:
            # Primeiro: click simples
            botao_ponto.click()
            print("Tentando clicar no botão",botao_ponto)
        except:
            try:
                # Segundo: JavaScript click
                print("Tentando clicar via JavaScript")
                chrome.execute_script("arguments[0].click();", botao_ponto)
            except:
                # Terceiro: ActionChains
                print("Tentando clicar via ActionChains")
                ActionChains(chrome).move_to_element(botao_ponto).click().perform()
        
        # Tirar screenshot após clicar
        chrome.save_screenshot("/tmp/apos_clicar.png")
            
    except Exception as e:
        print(f"Erro ao bater ponto: {e}")
        # Tirar screenshot em caso de erro
        try:
            chrome.save_screenshot("/tmp/erro.png")
        except:
            pass
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
