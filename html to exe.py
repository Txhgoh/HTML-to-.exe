import sys
import os
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTextEdit, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QWidget, QLabel, QMessageBox)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt

class HTMLToEXEConstructor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HTML to EXE Builder | Powered by h63bro")
        self.setGeometry(100, 100, 1100, 650)

        # Главный виджет
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Главный вертикальный слой (чтобы внизу подпереть футером с ТГК)
        global_layout = QVBoxLayout(main_widget)

        # Рабочая зона (разделенная на лево и право)
        work_layout = QHBoxLayout()

        # --- ЛЕВАЯ ЧАСТЬ: Ввод и Кнопки ---
        left_layout = QVBoxLayout()
        
        # Поле ввода кода
        self.code_input = QTextEdit()
        self.code_input.setPlaceholderText("\n<h1>Привет, мир!</h1>")
        self.code_input.setStyleSheet("font-family: 'Courier New'; font-size: 14px;")
        
        # Кнопки управления
        self.btn_run = QPushButton("⚡ Запустить код в превью")
        self.btn_run.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; padding: 8px;")
        
        self.btn_build = QPushButton("📦 Скомпилировать в .EXE")
        self.btn_build.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; padding: 8px;")

        left_layout.addWidget(QLabel("<b>Исходный HTML код:</b>"))
        left_layout.addWidget(self.code_input)
        left_layout.addWidget(self.btn_run)
        left_layout.addWidget(self.btn_build)

        # --- ПРАВАЯ ЧАСТЬ: Живой просмотр ---
        right_layout = QVBoxLayout()
        self.preview = QWebEngineView()
        
        right_layout.addWidget(QLabel("<b>Предпросмотр приложения:</b>"))
        right_layout.addWidget(self.preview)

        # Соединяем левую и правую части в рабочую зону
        work_layout.addLayout(left_layout, 1)
        work_layout.addLayout(right_layout, 1)
        
        # Добавляем рабочую зону в глобальный слой
        global_layout.addLayout(work_layout)

        # --- ФУТЕР (Нижняя панель с твоим ТГК) ---
        footer = QLabel("Разработано в конструкторе приложений | Telegram-канал: <b>t.me/h63bro</b>")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("background-color: #2c3e50; color: #ecf0f1; padding: 5px; font-size: 12px; border-radius: 4px;")
        global_layout.addWidget(footer)

        # Логика кнопок
        self.btn_run.clicked.connect(self.run_html)
        self.btn_build.clicked.connect(self.build_exe)

    def run_html(self):
        """Отображает введенный код в правой панели"""
        html_code = self.code_input.toPlainText()
        if not html_code.strip():
            html_code = "<h1>Тут пока ничего нет... Напиши код слева!</h1>"
        self.preview.setHtml(html_code)

    def build_exe(self):
        """Логика автоматической компиляции HTML в EXE"""
        html_code = self.code_input.toPlainText()
        
        if not html_code.strip():
            QMessageBox.warning(self, "Ошибка", "Нельзя собрать пустое приложение! Напиши HTML-код.")
            return

        # Создаем рабочую директорию для сборки, если её нет
        build_dir = os.path.abspath("constructor_build")
        os.makedirs(build_dir, exist_ok=True)

        # 1. Сохраняем HTML-код пользователя
        html_file_path = os.path.join(build_dir, "index.html")
        with open(html_file_path, "w", encoding="utf-8") as f:
            f.write(html_code)

        # 2. Создаем Python-скрипт шаблон, который будет упакован в EXE
        # Этот шаблон открывает index.html, который лежит внутри самого EXE
        launcher_code = """import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtWebEngineWidgets import QWebEngineView

app = QApplication(sys.argv)
win = QMainWindow()
win.setWindowTitle("Приложение от h63bro")
win.setGeometry(100, 100, 900, 600)

view = QWebEngineView(win)
win.setCentralWidget(view)

# Функция для поиска файлов внутри скомпилированного PyInstaller пакета
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

html_path = resource_path("index.html")

if os.path.exists(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        view.setHtml(f.read())
else:
    view.setHtml("<h1>Ошибка: Файл интерфейса не найден!</h1>")

win.show()
sys.exit(app.exec())
"""
        launcher_file_path = os.path.join(build_dir, "launcher.py")
        with open(launcher_file_path, "w", encoding="utf-8") as f:
            f.write(launcher_code)

        # 3. Запуск PyInstaller для сборки
        QMessageBox.information(self, "Сборка начата", "Начался процесс компиляции. Это займет около 30-60 секунд. Пожалуйста, подожди.")
        
        # Формируем команду для терминала
        # --onefile (один файл), --noconsole (без черного окна консоли), --add-data (внедрить наш HTML внутрь exe)
        command = [
            "pyinstaller",
            "--onefile",
            "--noconsole",
            f"--add-data=index.html{os.pathsep}.",
            "launcher.py"
        ]

        try:
            # Запускаем сборку скрыто в фоне, чтобы интерфейс не намертво зависал
            result = subprocess.run(command, cwd=build_dir, shell=True, capture_output=True, text=True)
            
            # Проверяем, создался ли файл
            exe_path = os.path.join(build_dir, "dist", "launcher.exe")
            if os.path.exists(exe_path):
                QMessageBox.information(
                    self, 
                    "Успех!", 
                    f"Готово!\n\nТвой .EXE файл успешно создан и лежит тут:\n{exe_path}\n\nСделано в конструкторе h63bro!"
                )
                # Открываем папку с готовым файлом в проводнике
                os.system(f'explorer /select,"{exe_path}"')
            else:
                QMessageBox.critical(self, "Ошибка компиляции", f"Что-то пошло не так при сборке.\nЛог ошибки:\n{result.stderr}")
        
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось запустить сборщик: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HTMLToEXEConstructor()
    window.show()
    sys.exit(app.exec())