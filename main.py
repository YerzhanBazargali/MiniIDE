import sys
import os

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QFileSystemModel, QShortcut, QKeySequence, QPixmap
from PyQt6.QtWidgets import (
    QApplication, QWidget, QTreeView, QPushButton, QPlainTextEdit,
    QSplitter, QVBoxLayout, QHBoxLayout, QFileDialog, QFileIconProvider,
    QStackedWidget, QLabel, QMenu, QMessageBox, QInputDialog, QDialog
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput

from EditorPQT import QCodeEditor
from auth import LoginDialog
from storage import (
    FileStorage, IMAGE_EXTENSIONS, AUDIO_EXTENSIONS, UNSUPPORTED_EXTENSIONS,
    UPLOAD_ALLOWED_EXTENSIONS, RUN_TEMP_FILENAME
)
from process_runner import ProcessRunner


# --- ОСНОВНОЕ ОКНО ---
class MiniIDE(QWidget):
    """Главное окно IDE: файловое дерево, редактор кода и вывод процесса.

    Само окно отвечает только за UI и связывание сигналов. Шифрование/чтение
    файлов — в FileStorage (storage.py), запуск кода — в ProcessRunner
    (process_runner.py), логин — в auth.py.
    """

    def __init__(self, user_name, user_folder, root_dir):
        super().__init__()
        self.user_name = user_name
        self.user_folder = user_folder
        self.root_dir = root_dir
        self.storage = FileStorage(user_name, user_folder)
        self.runner = ProcessRunner(root_dir)

        self.setWindowTitle(f"IDE — Пользователь: {self.user_name}")
        self.resize(1100, 750)

        # 1. Главный макет
        main_layout = QVBoxLayout(self)

        # 2. Горизонтальный сплиттер
        self.main_splitter = QSplitter(Qt.Orientation.Horizontal)

        # 3. Панель кнопок
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
        # button_widget добавляется в content_splitter ниже — сюда, в main_layout,
        # его добавлять не нужно.

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
            QPushButton#btn_run { background-color: #2d7d46; } /* Всегда зелёная — выделяем кнопку запуска */
            QPushButton#btn_stop { background-color: #a1260d; } /* Всегда красная — выделяем кнопку остановки */
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
        self.player = QMediaPlayer()
        self.audio = QAudioOutput()
        self.player.setAudioOutput(self.audio)

        self.btn_run.clicked.connect(self.run_code)
        self.btn_stop.clicked.connect(self.stop_code)
        self.btn_save.clicked.connect(self.save_file)
        self.files.doubleClicked.connect(self.open_file)

        self.runner.output_received.connect(self.handle_out)
        self.runner.error_received.connect(self.handle_err)
        self.runner.finished.connect(self.on_finished)
        self.runner.start_failed.connect(self.handle_start_failed)

        QShortcut(QKeySequence("F5"), self).activated.connect(self.run_code)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self.save_file)

        self.log_area.appendPlainText("--- MiniIDE запущен ---")
        self.log_area.appendPlainText("Разработчик: Ержан Базарғали")
        self.log_area.appendPlainText("Для поддержки: +7 707 518 60 96")
        self.log_area.appendPlainText("-----------------------")

        self.current_file = None

    def _confirm_discard_changes(self):
        """Если в редакторе есть несохранённые изменения — спрашивает, что с ними
        делать, прежде чем их заменить (открыть другой файл/создать новый/закрыть
        окно). Возвращает True, если можно продолжать действие (сохранили или
        явно отказались), False — если пользователь передумал (Отмена)."""
        if not self.editor.document().isModified():
            return True

        reply = QMessageBox.question(
            self, "Несохранённые изменения",
            "В редакторе есть несохранённые изменения. Сохранить их?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Cancel
        )
        if reply == QMessageBox.StandardButton.Cancel:
            return False
        if reply == QMessageBox.StandardButton.Yes:
            return self.save_file()
        return True  # No — осознанно отбрасываем изменения

    def create_new_file(self):
        name, ok = QInputDialog.getText(self, "Новый файл", "Имя файла:", text="script.py")
        if not (ok and name.strip()):
            return

        try:
            path = self.storage.resolve_new_file_path(name.strip())
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
            return

        if os.path.exists(path):
            reply = QMessageBox.question(
                self, "Файл уже существует",
                f"Файл «{os.path.basename(path)}» уже существует и будет очищен. Перезаписать?"
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        if not self._confirm_discard_changes():
            return

        try:
            self.storage.create_file(path)
        except OSError as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось создать файл:\n{e}")
            return

        self.current_file = path
        self.editor.setPlainText("")
        self.editor.document().setModified(False)
        self.stack.setCurrentIndex(0)

    def open_file(self, index):
        path = self.file_model.filePath(index)
        ext = os.path.splitext(path.lower())[1]

        if ext in UNSUPPORTED_EXTENSIONS:
            # Не трогаем current_file/редактор вообще — иначе пришлось бы
            # решать те же вопросы (Ctrl+S, F5 поверх файла), что и для
            # картинок/аудио, ради формата, который IDE всё равно не умеет
            # показать.
            self.log_area.appendPlainText(f"⚠ Формат «{ext}» не поддерживается для просмотра в MiniIDE.")
            return

        is_text = ext not in IMAGE_EXTENSIONS and ext not in AUDIO_EXTENSIONS

        # Открытие картинки/аудио не трогает содержимое редактора — спрашивать
        # про несохранённые изменения нужно только когда мы реально собираемся
        # заменить текст в редакторе содержимым другого файла.
        if is_text and not self._confirm_discard_changes():
            return

        self.current_file = path
        self.setWindowTitle(f"IDE — {self.user_name} — {os.path.basename(path)}")

        # Останавливаем плеер и сбрасываем текст кнопки при открытии ЛЮБОГО
        # файла (не только другого аудио) — иначе кнопка "Пауза" останется,
        # даже когда воспроизведение уже остановлено.
        self.player.stop()
        self.btn_play.setText("▶ Воспроизвести")

        if ext in IMAGE_EXTENSIONS:
            self.img_view.setPixmap(
                QPixmap(path).scaled(
                    self.stack.size(),
                    Qt.AspectRatioMode.KeepAspectRatio
                )
            )
            self.stack.setCurrentIndex(1)

        elif ext in AUDIO_EXTENSIONS:
            self.music_label.setText(f"🎵 {os.path.basename(path)}")
            self.player.setSource(QUrl.fromLocalFile(path))
            self.stack.setCurrentIndex(2)

        else:
            try:
                text = self.storage.read_text(path)
            except Exception as e:
                # Файл не прочитан (например, временно заблокирован антивирусом
                # или сбой на флешке) — не оставляем current_file указывающим на
                # него: иначе Ctrl+S зашифрует и запишет этот текст ошибки прямо
                # поверх настоящего содержимого файла, безвозвратно его стерев.
                self.current_file = None
                self.editor.setPlainText(f"Ошибка чтения файла:\n{e}")
                self.editor.document().setModified(False)
                self.stack.setCurrentIndex(0)
                return

            self.editor.setPlainText(text)
            self.editor.document().setModified(False)
            self.stack.setCurrentIndex(0)

    def save_file(self):
        """Сохраняет редактор в файл. Возвращает True при успехе — используется
        в _confirm_discard_changes(), чтобы понять, можно ли продолжать действие,
        которое ждало ответа "сохранить перед тем как заменить/закрыть"."""
        path = self.current_file or os.path.join(self.user_folder, "unnamed.py")
        if not path.endswith(".py"):
            self.log_area.appendPlainText("⚠ Сохранение доступно только для .py файлов")
            return False
        try:
            self.storage.write_text(path, self.editor.toPlainText())
        except OSError as e:
            self.log_area.appendPlainText(f"⚠ Не удалось сохранить файл: {e}")
            return False
        self.editor.document().setModified(False)
        self.log_area.appendPlainText(f"Сохранено: {os.path.basename(path)}")
        return True

    def run_code(self):
        self.log_area.clear()

        if not self.editor.toPlainText().strip():
            self.log_area.appendPlainText("⚠ Нет кода для запуска")
            return

        # 1. Останавливаем предыдущий процесс, если он еще запущен
        # (после проверки на пустой редактор — иначе F5 с пустым полем
        # тихо убивал бы уже работающую программу ученика)
        self.runner.ensure_stopped()

        # 2. Определяем путь запуска. current_file используется и для открытых
        # картинок/аудио (для заголовка окна) — если сейчас "открыт" не .py
        # файл, писать в него нельзя, иначе F5 зашифрует и запишет код поверх
        # чужого изображения/аудио. В этом случае ведём себя как при
        # отсутствии открытого файла — создаём untitled_script.py.
        if self.current_file and self.current_file.endswith(".py"):
            run_path = self.current_file
        else:
            run_path = os.path.join(self.user_folder, "untitled_script.py")
            self.current_file = run_path

        # 3. Сохраняем актуальный код из редактора перед запуском (в зашифрованном виде)
        # 4. Создаем ЧИСТУЮ временную копию для интерпретатора (без шифрования!)
        # Чтобы Python мог выполнить этот файл, он должен быть обычным текстом
        temp_run_file = os.path.join(self.user_folder, RUN_TEMP_FILENAME)
        try:
            self.storage.write_text(run_path, self.editor.toPlainText())
            self.storage.write_plain(temp_run_file, self.editor.toPlainText())
        except OSError as e:
            self.log_area.appendPlainText(f"⚠ Не удалось подготовить файл для запуска: {e}")
            return
        self.editor.document().setModified(False)

        # 5. Запуск
        used_fallback = self.runner.run(temp_run_file, self.user_folder)
        if used_fallback:
            self.log_area.appendPlainText("⚠ Портативный Python не найден, использую системный...")

        self.btn_run.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.log_area.appendPlainText(f"--- Запуск: {os.path.basename(run_path)} ---")

    def stop_code(self): self.runner.stop()

    def _append_log(self, text):
        """Дописывает текст в лог и подтягивает прокрутку вниз, только если она
        и так была внизу — чтобы не сбивать того, кто прокрутил лог наверх
        почитать более ранний вывод."""
        bar = self.log_area.verticalScrollBar()
        at_bottom = bar.value() >= bar.maximum() - 4
        self.log_area.appendPlainText(text)
        if at_bottom:
            bar.setValue(bar.maximum())

    def handle_out(self, text):
        self._append_log(text)

    def handle_err(self, text):
        self._append_log(f"ОШИБКА: {text}")

    def handle_start_failed(self, message):
        self.btn_run.setEnabled(True)
        self.btn_stop.setEnabled(False)
        # errorOccurred (в отличие от finished) не сопровождается вызовом
        # on_finished, поэтому .run_temp.py нужно убрать явно и здесь.
        t = os.path.join(self.user_folder, RUN_TEMP_FILENAME)
        self.storage.remove_if_exists(t)
        self.log_area.appendPlainText(f"⚠ {message}")

    def on_finished(self):
        self.btn_run.setEnabled(True)
        self.btn_stop.setEnabled(False)
        # Удаляем временный файл для запуска
        t = os.path.join(self.user_folder, RUN_TEMP_FILENAME)
        self.storage.remove_if_exists(t)
        self.log_area.appendPlainText("\n--- Процесс завершен ---")

    def upload_file(self):
        patterns = " ".join(f"*{ext}" for ext in UPLOAD_ALLOWED_EXTENSIONS)
        f, _ = QFileDialog.getOpenFileName(
            self, "Загрузить", "", f"Поддерживаемые файлы ({patterns})"
        )
        if not f:
            return

        try:
            dest = self.storage.resolve_upload_path(f)
        except ValueError as e:
            QMessageBox.warning(self, "Ошибка", str(e))
            return

        if os.path.exists(dest):
            reply = QMessageBox.question(
                self, "Файл уже существует",
                f"Файл «{os.path.basename(dest)}» уже существует и будет заменён. Перезаписать?"
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        try:
            self.storage.upload_file(f)
        except OSError as e:
            QMessageBox.warning(self, "Ошибка", f"Не удалось загрузить файл:\n{e}")

    def toggle_music(self):
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                self.player.pause()
                self.btn_play.setText("▶ Воспроизвести")
        else:
                self.player.play()
                self.btn_play.setText("⏸ Пауза")

    def closeEvent(self, event):
        if not self._confirm_discard_changes():
            event.ignore()
            return

        # Без этого запущенный студентом процесс (особенно pygame-цикл) может
        # остаться висеть в фоне после закрытия окна IDE. stop() сам дожидается
        # завершения (мягко, потом жёстко при необходимости).
        self.runner.stop()
        self.storage.remove_if_exists(os.path.join(self.user_folder, RUN_TEMP_FILENAME))
        super().closeEvent(event)

    def show_context_menu(self, pos):
        index = self.files.indexAt(pos)
        if not index.isValid(): return
        menu = QMenu(); del_act = menu.addAction("🗑 Удалить")
        if menu.exec(self.files.viewport().mapToGlobal(pos)) == del_act:
            p = self.file_model.filePath(index)
            if QMessageBox.question(self, "Удаление", f"Удалить {os.path.basename(p)}?") == QMessageBox.StandardButton.Yes:
                try:
                    self.storage.delete_path(p)
                except OSError as e:
                    QMessageBox.warning(self, "Ошибка удаления", f"Не удалось удалить:\n{e}")


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
