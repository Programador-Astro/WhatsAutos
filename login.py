import requests

def verificar_login(usuario_digitado, senha_digitada):
    url = "https://raw.githubusercontent.com/Programador-Astro/WhatsAutos/main/usuarios.json"
    response = requests.get(url)

    if response.status_code == 200:
        dados = response.json()
        for user in dados["usuarios"]:
            if user["usuario"] == usuario_digitado and user["senha"] == senha_digitada:
                return True
        return False
    else:
        print("Erro ao carregar dados de login.")
        return False
