import sys
import os
import shutil
from PyQt6.QtCore import QProcess, Qt, QUrl
from PyQt6.QtGui import QFileSystemModel, QShortcut, QKeySequence, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QWidget, QTreeView, QPushButton, QPlainTextEdit, 
    QSplitter, QVBoxLayout, QHBoxLayout, QFileDialog, QFileIconProvider, 
    QStackedWidget, QLabel, QMenu, QMessageBox, QInputDialog, QDialog, QLineEdit, QFormLayout, QDialogButtonBox
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from EditorPQT import QCodeEditor

# --- ФУНКЦИИ ШИФРОВАНИЯ ---
def crypt_data(data_bytes, login_str):
    if not login_str:
        key = 123
    else:
        key = sum(ord(char) for char in login_str) % 256
    return bytes([b ^ key for b in data_bytes])

def check_auth(login, password, root_dir):
    auth_dir = os.path.join(root_dir, "students")
    os.makedirs(auth_dir, exist_ok=True)

    auth_file = os.path.join(auth_dir, "auth_data.dat")
    
    auth_data = {}
    if os.path.exists(auth_file):
        with open(auth_file, "rb") as f:
            try:
                decoded = crypt_data(f.read(), None).decode("utf-8", errors="replace")
                for line in decoded.splitlines():
                    if ":" in line:
                        u, p = line.split(":", 1)
                        auth_data[u] = p
            except Exception: pass

    if login not in auth_data:
        auth_data[login] = password
        content = "\n".join([f"{u}:{p}" for u, p in auth_data.items()])
        with open(auth_file, "wb") as f:
            f.write(crypt_data(content.encode("utf-8"), None))
        return True

    return auth_data.get(login) == password

# --- ОКНО ВХОДА ---
class LoginDialog(QDialog):
    def __init__(self, root_dir, parent=None):
        super().__init__(parent)
        self.root_dir = root_dir
        self.setWindowTitle("Вход в систему")
        self.setFixedSize(300, 150)
        layout = QFormLayout(self)
        self.login_input = QLineEdit()
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Логин:", self.login_input)
        layout.addRow("Пароль:", self.pass_input)
        self.buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.buttons.accepted.connect(self.validate_and_accept)
        self.buttons.rejected.connect(self.reject)
        layout.addWidget(self.buttons)

    def validate_and_accept(self):
        user = self.login_input.text().strip()
        password = self.pass_input.text().strip()
        if not user or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return
        if check_auth(user, password, self.root_dir):
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", "Неверный пароль!")

    def get_data(self):
        return self.login_input.text().strip()

# --- ОСНОВНОЕ ОКНО ---
class MiniIDE(QWidget):
    def __init__(self, user_name, user_folder, root_dir):
        super().__init__()
        self.user_name = user_name
        self.user_folder = user_folder
        self.root_dir = root_dir
        
        self.setWindowTitle(f"IDE — Пользователь: {self.user_name}")
        self.resize(1100, 750)

        # 1. Главный макет
        main_layout = QVBoxLayout(self)

        # 2. Горизонтальный сплиттер
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # 2. Панель кнопок
        self.button_widget = QWidget()
        button_layout = QHBoxLayout(self.button_widget)
        self.btn_run = QPushButton("▶ Запустить (F5)")
        self.btn_run.setObjectName("btn_run")
        self.btn_stop = QPushButton("⏹ Остановить")
        self.btn_stop.setObjectName("btn_stop")
        self.btn_save = QPushButton("💾 Сохранить")
        self.btn_stop.setEnabled(False)
        button_layout.addWidget(self.btn_run)
        button_layout.addWidget(self.btn_stop)
        button_layout.addWidget(self.btn_save)
        button_layout.addStretch()
        self.button_widget.setFixedHeight(45)
        #main_layout.addLayout(button_layout)

        self.setStyleSheet("""
            /* Основное окно */
            QWidget {
                background-color: #1e1e1e;
                color: #d4d4d4;
            }
            /* Сплиттер (разделитель) */
            QSplitter::handle {
                background-color: #333333;
            }
            /* Дерево файлов */
            QTreeView {
                border: none;
                background-color: #252526;
            }
            /* Кнопки */
            QPushButton {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                padding: 4px 10px;
            }
            QPushButton:hover {
                background-color: #444444;
            }
            QPushButton:pressed {
                background-color: #222222;
            }
            QPushButton#btn_run:disabled {
                color: #EEEEEE;
                background-color: #777777;
            }
            QPushButton#btn_stop:disabled {
                color: #EEEEEE;
                background-color: #777777;
            }
            QPushButton#btn_run { background-color: #2d7d46; } /* Зеленый при наведении */
            QPushButton#btn_stop { background-color: #a1260d; } /* Красный при наведении */
        """)
        
        

        # --- ЛЕВАЯ ПАНЕЛЬ ---
        left_panel = QWidget()
        lp_layout = QVBoxLayout(left_panel)
        lp_layout.setContentsMargins(0,0,0,0)
        
        self.btn_upload = QPushButton("✚ Добавить файл")
        self.btn_upload.clicked.connect(self.upload_file)
        
        self.btn_new_file = QPushButton("📄 Создать файл")
        self.btn_new_file.clicked.connect(self.create_new_file)
        
        self.files = QTreeView()
        self.file_model = QFileSystemModel()
        self.file_model.setIconProvider(QFileIconProvider())
        self.file_model.setRootPath(self.user_folder)
        self.files.setModel(self.file_model)
        self.files.setRootIndex(self.file_model.index(self.user_folder))
        for i in range(1, 4): self.files.hideColumn(i)

        # ВКЛЮЧАЕМ МЕНЮ ПРАВОЙ КНОПКИ
        self.files.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.files.customContextMenuRequested.connect(self.show_context_menu)

        lp_layout.addWidget(self.btn_upload)
        lp_layout.addWidget(self.btn_new_file)
        lp_layout.addWidget(self.files)
        
        self.main_splitter.addWidget(left_panel)

        # --- 4. КОНТЕНТ (Редактор / Фото / Музыка) ---
        self.content_splitter = QSplitter(Qt.Orientation.Vertical)
        self.content_splitter.addWidget(self.button_widget)
        
        self.stack = QStackedWidget()
        
        self.editor = QCodeEditor()
        self.stack.addWidget(self.editor)
        
        self.img_view = QLabel()
        self.img_view.setScaledContents(False)
        self.img_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_view.setStyleSheet("background-color: #1a1a1a;")
        self.stack.addWidget(self.img_view)
        
        self.music_view = QWidget()
        self.music_view.setStyleSheet("background-color: #1a1a1a;")

        mv_layout = QVBoxLayout(self.music_view)
        
        self.music_label = QLabel("🎵 Музыка")
        self.music_label.setStyleSheet("color: white;")
        self.btn_play = QPushButton("▶ Воспроизвести")
        self.btn_play.clicked.connect(self.toggle_music)

        mv_layout.addStretch()
        mv_layout.addWidget(self.music_label)
        mv_layout.addWidget(self.btn_play)
        mv_layout.addStretch()
        
        self.stack.addWidget(self.music_view)
        
        self.content_splitter.addWidget(self.stack)

        self.log_area = QPlainTextEdit()
        self.log_area.setReadOnly(True)
        self.log_area.setStyleSheet("background-color: #1e1e1e; color: #d4d4d4;")
        self.content_splitter.addWidget(self.log_area)
        
        self.main_splitter.addWidget(self.content_splitter)
        main_layout.addWidget(self.main_splitter)
        self.main_splitter.setSizes([200, 800])

        # 5. Логика
        self.process = QProcess()
        
        self.player = QMediaPlayer()
        self.audio = QAudioOutput()
        self.player.setAudioOutput(self.audio)
        
        self.btn_run.clicked.connect(self.run_code)
        self.btn_stop.clicked.connect(self.stop_code)
        self.btn_save.clicked.connect(self.save_file)
        self.files.doubleClicked.connect(self.open_file)
        
        self.process.readyReadStandardOutput.connect(self.handle_out)
        self.process.readyReadStandardError.connect(self.handle_err)
        
        self.process.finished.connect(self.on_finished) 
        
        QShortcut(QKeySequence("F5"), self).activated.connect(self.run_code)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.save_file)

        self.log_area.appendPlainText("--- MiniIDE запущен ---")
        self.log_area.appendPlainText("Разработчик: Ержан Базарғали")
        self.log_area.appendPlainText("Для поддержки: +7 707 518 60 96")
        self.log_area.appendPlainText("-----------------------")
        
        self.current_file = None

    def create_new_file(self):
        name, ok = QInputDialog.getText(self, "Новый файл", "Имя файла:", text="script.py")
        if ok and name.strip():
            if not name.endswith(".py"): name += ".py"
            path = os.path.join(self.user_folder, name)
            self.current_file = path
            with open(path, "wb") as f: f.write(crypt_data("".encode("utf-8"), self.user_name))
            self.editor.setPlainText(""); self.stack.setCurrentIndex(0)

    def open_file(self, index):
        path = self.file_model.filePath(index)
        self.current_file = path
        self.setWindowTitle(f"IDE — {self.user_name} — {os.path.basename(path)}")
        ext = os.path.splitext(path.lower())[1]

        self.player.stop()

        if ext in ['.png', '.jpg', '.jpeg', '.gif']:
            self.img_view.setPixmap(
                QPixmap(path).scaled(
                    self.stack.size(),
                    Qt.AspectRatioMode.KeepAspectRatio
                )
            )
            self.stack.setCurrentIndex(1)

        elif ext in ['.mp3', '.wav', '.ogg']:
            self.music_label.setText(f"🎵 {os.path.basename(path)}")
            self.player.setSource(QUrl.fromLocalFile(path))
            self.stack.setCurrentIndex(2)

        else:
            try:
                with open(path, "rb") as f:
                    decrypted = crypt_data(f.read(), self.user_name).decode("utf-8", errors="replace")
                self.editor.setPlainText(decrypted)
            except Exception as e:
                self.editor.setPlainText(f"Ошибка чтения файла:\n{e}")

            self.stack.setCurrentIndex(0)

    def save_file(self):
        index = self.files.currentIndex()
        path = self.current_file or os.path.join(self.user_folder, "unnamed.py")
        if not path.endswith(".py"): return
        with open(path, "wb") as f:
            f.write(crypt_data(self.editor.toPlainText().encode("utf-8"), self.user_name))
        self.log_area.appendPlainText(f"Сохранено: {os.path.basename(path)}")

    def run_code(self):
            self.log_area.clear()

            # 1. Останавливаем предыдущий процесс, если он еще запущен
            if self.process.state() != QProcess.ProcessState.NotRunning:
                self.process.kill()
                self.process.waitForFinished(1000) # Ждем завершения 1 сек

            if not self.editor.toPlainText().strip():
                self.log_area.appendPlainText("⚠ Нет кода для запуска")
                return
            
            # 2. Определяем путь запуска. Если файл не открыт, создаем untitled.py
            if self.current_file:
                run_path = self.current_file
            else:
                run_path = os.path.join(self.user_folder, "untitled_script.py")
                self.current_file = run_path

            # 3. Сохраняем актуальный код из редактора перед запуском (в зашифрованном виде)
            with open(run_path, "wb") as f:
                f.write(crypt_data(self.editor.toPlainText().encode("utf-8"), self.user_name))
            
            # 4. Создаем ЧИСТУЮ временную копию для интерпретатора (без шифрования!)
            # Чтобы Python мог выполнить этот файл, он должен быть обычным текстом
            temp_run_file = os.path.join(self.user_folder, ".run_temp.py")
            with open(temp_run_file, "w", encoding="utf-8") as f:
                f.write(self.editor.toPlainText())

            # Поиск python.exe
            if getattr(sys, 'frozen', False):
                # Мы запущены как скомпилированный EXE
                base_dir = os.path.dirname(sys.executable)
                
                # Вариант А: папка в корне (рядом с exe)
                path_root = os.path.join(base_dir, "python_env", "python.exe")
                # Вариант Б: папка внутри _internal (стандарт для новых версий PyInstaller)
                path_internal = os.path.join(base_dir, "_internal", "python_env", "python.exe")
                
                if os.path.exists(path_internal):
                    self.py_exe = path_internal
                else:
                    self.py_exe = path_root
            else:
                # Мы запущены как обычный .py скрипт
                self.py_exe = os.path.join(self.root_dir, "python_env", "python.exe")

            # Проверка на случай, если папка вообще отсутствует
            if not os.path.exists(self.py_exe) and self.py_exe != "python":
                self.log_area.appendPlainText("⚠ Портативный Python не найден, использую системный...")
                self.py_exe = "python"

            # 5. Запуск
            self.process.setWorkingDirectory(self.user_folder)
            self.process.start(self.py_exe, [temp_run_file])
            
            self.btn_run.setEnabled(False)
            self.btn_stop.setEnabled(True)
            self.log_area.appendPlainText(f"--- Запуск: {os.path.basename(run_path)} ---")

    def stop_code(self): self.process.kill()
    
    def handle_out(self):
        raw_data = self.process.readAllStandardOutput().data()
        try:
            text = raw_data.decode("utf-8")
        except UnicodeDecodeError:
            text = raw_data.decode("cp1251", "replace")
        self.log_area.appendPlainText(text)

    def handle_err(self):
        raw_data = self.process.readAllStandardError().data()
        try:
            text = raw_data.decode("utf-8")
        except UnicodeDecodeError:
            text = raw_data.decode("cp1251", "replace")
        self.log_area.appendPlainText(f"ОШИБКА: {text}")

    def on_finished(self):
            self.btn_run.setEnabled(True)
            self.btn_stop.setEnabled(False)
            # Удаляем временный файл для запуска
            t = os.path.join(self.user_folder, ".run_temp.py")
            if os.path.exists(t):
                try:
                    os.remove(t)
                except:
                    pass
            self.log_area.appendPlainText("\n--- Процесс завершен ---")
    
    def upload_file(self):
        f, _ = QFileDialog.getOpenFileName(self, "Загрузить")
        if f: shutil.copy2(f, os.path.join(self.user_folder, os.path.basename(f)))

    def toggle_music(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                self.player.pause()
                self.btn_play.setText("▶ Воспроизвести")
        else:
                self.player.play()
                self.btn_play.setText("⏸ Пауза")

    def show_context_menu(self, pos):
        index = self.files.indexAt(pos)
        if not index.isValid(): return
        menu = QMenu(); del_act = menu.addAction("🗑 Удалить")
        if menu.exec(self.files.viewport().mapToGlobal(pos)) == del_act:
            p = self.file_model.filePath(index)
            if QMessageBox.question(self, "Удаление", f"Удалить {os.path.basename(p)}?") == QMessageBox.StandardButton.Yes:
                if os.path.isfile(p): os.remove(p)
                else: shutil.rmtree(p)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Определяем ROOT корректно для EXE и скрипта
    if getattr(sys, 'frozen', False):
        ROOT = os.path.dirname(sys.executable)
    else:
        ROOT = os.path.dirname(os.path.abspath(__file__))

    dial = LoginDialog(ROOT)
    if dial.exec() == QDialog.DialogCode.Accepted:
        user = dial.get_data()
        U_DIR = os.path.join(ROOT, "students", user)
        os.makedirs(U_DIR, exist_ok=True)
        win = MiniIDE(user, U_DIR, ROOT); win.show()
        sys.exit(app.exec())
