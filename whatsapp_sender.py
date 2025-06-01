import os
import time
import csv
import openpyxl
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def send_whatsapp_messages_from_file(file_path, msg, delay=5):
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    CHROME_BINARY_PATH = os.path.join(BASE_DIR, "chrome_portable", "chrome-win64", "chrome.exe")
    CHROMEDRIVER_PATH = os.path.join(BASE_DIR, "chrome_portable", "chromedriver-win64", "chromedriver.exe")
    USER_DATA_DIR = os.path.join(BASE_DIR, "chrome_portable", "user_data")

    if not os.path.exists(USER_DATA_DIR):
        os.makedirs(USER_DATA_DIR)

    if not os.path.isfile(CHROME_BINARY_PATH):
        print(f"Chrome não encontrado em: {CHROME_BINARY_PATH}")
        return
    if not os.path.isfile(CHROMEDRIVER_PATH):
        print(f"ChromeDriver não encontrado em: {CHROMEDRIVER_PATH}")
        return
    if not os.path.isfile(file_path):
        print(f"Arquivo não encontrado: {file_path}")
        return

    # Leitura dos contatos (csv ou xlsx)
    contatos = []
    try:
        if file_path.endswith(".xlsx"):
            wb = openpyxl.load_workbook(file_path)
            sheet = wb.active
            for row in sheet.iter_rows(min_row=1):
                nome = row[0].value
                telefone = row[1].value
                if nome and telefone:
                    contatos.append((str(nome).strip(), str(telefone).strip()))
        elif file_path.endswith(".csv"):
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    if len(row) >= 2:
                        nome = row[0]
                        telefone = row[1]
                        if nome and telefone:
                            contatos.append((nome.strip(), telefone.strip()))
        else:
            print("Formato de arquivo não suportado. Use .csv ou .xlsx.")
            return
    except Exception as e:
        print(f"Erro ao ler o arquivo: {e}")
        return

    print(f"Lidos {len(contatos)} contatos do arquivo {file_path}")

    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={USER_DATA_DIR}")
    options.add_argument("--profile-directory=Default")
    options.add_experimental_option("detach", True)
    options.binary_location = CHROME_BINARY_PATH

    try:
        service = Service(executable_path=CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print("❌ Erro ao iniciar o Chrome:", e)
        return

    try:
        driver.get("https://web.whatsapp.com/")
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.ID, "side"))
        )
        print("✅ WhatsApp Web carregado com sucesso.")
    except Exception as e:
        print("❌ Erro ao carregar o WhatsApp Web:", e)
        return

    for i, (nome, telefone) in enumerate(contatos, 1):
        numero = ''.join(filter(str.isdigit, telefone))
        if not numero:
            print(f"[{i}] ❌ Telefone inválido para {nome}: {telefone}")
            continue

        mensagem = msg.replace("{nome}", nome)
        url = f"https://web.whatsapp.com/send?phone={numero}&text={mensagem}"
        driver.get(url)

        try:
            send_btn = WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@data-icon="send"]'))
            )
            send_btn.click()
            print(f"[{i}] ✅ Mensagem enviada para {nome} - {telefone}")
            time.sleep(delay)
        except Exception as e:
            print(f"[{i}] ❌ Erro ao enviar para {nome} - {telefone}: {e}")
            time.sleep(2)

    print("✅ Envio concluído.")
