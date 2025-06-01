from login import verificar_login
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton,
    QFileDialog, QListWidget, QMessageBox, QStackedWidget, QTextEdit
)
from PySide6.QtGui import QIcon
from qt_material import apply_stylesheet
import sys
import os
import pandas as pd
import requests

from whatsapp_sender import send_whatsapp_messages_from_file  # sua função personalizada
import sys
import os

def resource_path(relative_path):
    """Resolve o caminho relativo tanto em execução normal quanto no .exe do PyInstaller."""
    if getattr(sys, 'frozen', False):  # Estamos dentro de um executável
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
class LoginScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget

        layout = QVBoxLayout()

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        layout.addWidget(self.email_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Senha")
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton("Entrar")
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def login(self):
        email = self.email_input.text()
        senha = self.password_input.text()

        if not email or not senha:
            QMessageBox.warning(self, "Erro", "Preencha todos os campos.")
            return

        try:
            response = requests.post("http://127.0.0.1:5000/auth/", json={
                "email": email,
                "pwd": senha
            })
            if response.status_code == 200 and response.json().get("success"):
                QMessageBox.information(self, "Sucesso", "Login bem-sucedido!")
                self.stacked_widget.setCurrentIndex(1)
            else:
                QMessageBox.warning(self, "Erro", "Login inválido.")
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao fazer login:\n{e}")

class MainScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.file_path = None

        layout = QVBoxLayout()

        self.select_button = QPushButton("Selecionar Arquivo Excel")
        self.select_button.clicked.connect(self.select_file)
        layout.addWidget(self.select_button)

        self.preview_list = QListWidget()
        layout.addWidget(self.preview_list)

        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Digite sua mensagem aqui")
        layout.addWidget(self.message_input)

        self.send_button = QPushButton("Enviar Mensagens")
        self.send_button.clicked.connect(self.send_messages)
        layout.addWidget(self.send_button)

        self.setLayout(layout)

    def select_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Selecionar arquivo", "", "Arquivos Excel (*.xlsx)")
        if file_name:
            if not file_name.lower().endswith('.xlsx'):
                QMessageBox.warning(self, "Erro", "Selecione um arquivo .xlsx")
                return
            self.file_path = file_name
            self.preview_list.clear()
            try:
                df = pd.read_excel(file_name)
                for i in range(min(5, len(df))):
                    nome, tel = df.iloc[i, 0], df.iloc[i, 1]
                    self.preview_list.addItem(f"{nome} — {tel}")
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Não foi possível ler o arquivo:\n{e}")

    def send_messages(self):
        if not self.file_path or not self.message_input.toPlainText().strip():
            QMessageBox.warning(self, "Erro", "Selecione um arquivo e digite a mensagem.")
            return
        try:
            send_whatsapp_messages_from_file(self.file_path, self.message_input.toPlainText().strip())
            QMessageBox.information(self, "Sucesso", "Mensagens enviadas com sucesso!")
        except Exception as e:
            QMessageBox.critical(self, "Erro", str(e))

class ZenWapApp(QApplication):
    def __init__(self, sys_argv):
        super().__init__(sys_argv)

        from PySide6.QtGui import QIcon

        self.stacked_widget = QStackedWidget()

        self.stacked_widget.addWidget(LoginScreen(self.stacked_widget))
        self.stacked_widget.addWidget(MainScreen())

        # ✅ Agora é seguro definir título e ícone
        icon_path = resource_path("assets/logo.png")
        self.stacked_widget.setWindowTitle("ZenWap")
        self.stacked_widget.setWindowIcon(QIcon(icon_path))

        self.stacked_widget.setFixedSize(400, 600)
        self.stacked_widget.show()
if __name__ == "__main__":
    app = ZenWapApp(sys.argv)
    apply_stylesheet(app, theme='dark_teal.xml')  # ou light_blue.xml, dark_amber.xml etc.
    sys.exit(app.exec())
