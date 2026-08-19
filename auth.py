"""Аутентификация и XOR-обфускация данных пользователя MiniIDE."""
import os
import re
import time
from PyQt6.QtWidgets import QDialog, QLineEdit, QFormLayout, QDialogButtonBox, QMessageBox

# Логин используется как имя папки (students/<login>/) и как поле в auth_data.dat
# в формате "login:password". Поэтому запрещаем разделители пути (чтобы нельзя
# было выйти за пределы папки пользователя) и двоеточие (чтобы не сломать формат).
_LOGIN_PATTERN = re.compile(r'^[\w\-]+$', re.UNICODE)


def is_valid_login(login):
    """Проверяет, что логин безопасен для использования как имя папки и как ключ в auth_data.dat."""
    return bool(login) and login not in (".", "..") and bool(_LOGIN_PATTERN.match(login))


def crypt_data(data_bytes, login_str):
    """XOR-обфускация байтов ключом, вычисленным из логина.

    Это НЕ настоящее шифрование: пространство ключей — 256 значений,
    и ключ восстанавливается из логина по открытому алгоритму.
    См. раздел "Ограничения" в README.

    Реализовано через bytes.translate() с таблицей подстановки — тот же
    результат, что и побайтовый XOR-цикл, но выполняется на уровне C.
    Важно для upload_file(), который теперь шифрует произвольные (в том
    числе крупные) загружаемые файлы и не должен подвешивать интерфейс.
    """
    if not login_str:
        key = 123
    else:
        key = sum(ord(char) for char in login_str) % 256
    table = bytes(i ^ key for i in range(256))
    return data_bytes.translate(table)


def _auth_file_path(root_dir):
    """Путь к auth_data.dat; попутно создаёт папку students/, если её ещё нет."""
    auth_dir = os.path.join(root_dir, "students")
    os.makedirs(auth_dir, exist_ok=True)
    return os.path.join(auth_dir, "auth_data.dat")


def _load_auth_data(auth_file):
    """Читает и разбирает auth_data.dat.

    MiniIDE рассчитан на запуск с USB-флешки (см. README), а обрыв питания или
    отключение флешки посреди чтения/записи может испортить файл. Раньше любая
    ошибка разбора тихо приводила к пустому словарю — и следующая же регистрация
    перезаписывала файл, стирая данные всех учеников без следа. Теперь при
    повреждении файл переносится в резервную копию и пользователь видит
    предупреждение, а не теряет всё молча.
    """
    if not os.path.exists(auth_file):
        return {}

    try:
        with open(auth_file, "rb") as f:
            raw = f.read()
        decoded = crypt_data(raw, None).decode("utf-8")
        auth_data = {}
        for line in decoded.splitlines():
            if ":" in line:
                u, p = line.split(":", 1)
                auth_data[u] = p
        return auth_data
    except Exception:
        backup = f"{auth_file}.corrupted-{int(time.time())}"
        try:
            os.replace(auth_file, backup)
        except OSError:
            backup = None
        QMessageBox.warning(
            None, "Файл учётных записей повреждён",
            "Не удалось прочитать список логинов учеников — файл повреждён "
            "(возможно, из-за обрыва питания или отключения флешки во время записи).\n\n"
            + (f"Повреждённый файл сохранён как:\n{os.path.basename(backup)}\n\n" if backup else "")
            + "Список учётных записей будет начат заново."
        )
        return {}


def _save_auth_data(auth_file, auth_data):
    """Атомарно перезаписывает auth_data.dat: пишет во временный файл и переименовывает его.

    os.replace() на той же файловой системе — атомарная операция: обрыв
    питания/флешки посреди записи не может оставить auth_data.dat в
    наполовину записанном виде — либо новая версия применится целиком,
    либо останется прежний (нетронутый) файл.

    Имя временного файла включает PID процесса — если когда-нибудь MiniIDE
    запустят с общей сетевой папки в две руки одновременно, два процесса не
    затрут временный файл друг друга.
    """
    content = "\n".join(f"{u}:{p}" for u, p in auth_data.items())
    tmp_file = f"{auth_file}.{os.getpid()}.tmp"
    try:
        with open(tmp_file, "wb") as f:
            f.write(crypt_data(content.encode("utf-8"), None))
        os.replace(tmp_file, auth_file)
    except Exception:
        if os.path.exists(tmp_file):
            os.remove(tmp_file)
        raise


def check_auth(login, password, root_dir):
    """Проверяет логин/пароль по auth_data.dat, автоматически регистрируя новых пользователей."""
    auth_file = _auth_file_path(root_dir)
    auth_data = _load_auth_data(auth_file)

    if login not in auth_data:
        auth_data[login] = password
        _save_auth_data(auth_file, auth_data)
        return True

    return auth_data.get(login) == password


class LoginDialog(QDialog):
    """Окно входа: логин создаётся автоматически при первом успешном вводе."""

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

        self._login = None

    def validate_and_accept(self):
        # Приводим логин к нижнему регистру: он используется и как ключ в
        # auth_data.dat, и как имя папки students/<login>/, и как ключ XOR-
        # шифрования файлов. Windows-файловая система регистронезависима
        # (students/Ivan и students/ivan — одна и та же папка), а без
        # нормализации словарь и XOR-ключ считали бы их разными аккаунтами —
        # тот же ученик, войдя в другой раз с другим регистром, получал бы
        # нечитаемые (расшифрованные не тем ключом) старые файлы.
        user = self.login_input.text().strip().lower()
        password = self.pass_input.text().strip()
        if not user or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return
        if not is_valid_login(user):
            QMessageBox.warning(
                self, "Ошибка",
                "Логин может содержать только буквы, цифры, дефис и подчёркивание "
                "(без пробелов, точек и слэшей)."
            )
            return

        try:
            ok = check_auth(user, password, self.root_dir)
        except (OSError, UnicodeError) as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось получить доступ к данным учётных записей:\n{e}")
            return

        if ok:
            self._login = user
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка", "Неверный пароль!")

    def get_data(self):
        return self._login
