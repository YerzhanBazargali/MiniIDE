"""Файловые операции для персональной папки ученика (чтение/запись/загрузка/удаление)."""
import os
import shutil

from auth import crypt_data

# Типы файлов, которые открываются напрямую (картинки/аудио через Qt) и поэтому
# никогда не шифруются. Всё остальное считается "текстовым" и шифруется XOR'ом,
# чтобы open_file() могло его безопасно расшифровать при открытии.
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif')
AUDIO_EXTENSIONS = ('.mp3', '.wav', '.ogg')

# Имя временного незашифрованного файла, который run_code() создаёт для запуска
# кода интерпретатором и безусловно удаляет после завершения процесса (main.py).
# Если ученик создаст/загрузит файл с этим именем, оно совпадёт с временным —
# и такой файл будет удалён вместе с временным. Поэтому это имя запрещено для
# создания/загрузки (см. resolve_new_file_path/resolve_upload_path).
RUN_TEMP_FILENAME = ".run_temp.py"


def _check_not_reserved(base, action_hint):
    """Запрещает создание/загрузку файла с именем RUN_TEMP_FILENAME (см. выше)."""
    if base.lower() == RUN_TEMP_FILENAME.lower():
        raise ValueError(
            f"Имя «{RUN_TEMP_FILENAME}» зарезервировано под служебный файл запуска. "
            f"{action_hint}"
        )


class FileStorage:
    """Обёртка над файловыми операциями внутри папки конкретного пользователя."""

    def __init__(self, user_name, user_folder):
        self.user_name = user_name
        self.user_folder = user_folder

    def read_text(self, path):
        """Читает файл с диска и расшифровывает его как UTF-8 текст (для редактора)."""
        with open(path, "rb") as f:
            raw = f.read()
        return crypt_data(raw, self.user_name).decode("utf-8", errors="replace")

    def write_text(self, path, text):
        """Шифрует текст и сохраняет его на диск."""
        with open(path, "wb") as f:
            f.write(crypt_data(text.encode("utf-8"), self.user_name))

    def write_plain(self, path, text):
        """Пишет обычный (незашифрованный) текст — используется для временного файла запуска."""
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)

    def resolve_new_file_path(self, name):
        """Вычисляет путь для нового файла (добавляет .py при необходимости), не создавая его.

        Отбрасывает любые компоненты пути (".." , "/", "\\") из введённого имени,
        чтобы новый файл гарантированно создавался внутри папки пользователя.
        """
        base = os.path.basename(name.strip())
        if not base or base in (".", ".."):
            raise ValueError("Недопустимое имя файла")
        if not base.endswith(".py"):
            base += ".py"
        _check_not_reserved(base, "Выберите другое имя.")
        return os.path.join(self.user_folder, base)

    def create_file(self, path):
        """Создаёт (или перезаписывает) пустой зашифрованный файл по заданному пути."""
        self.write_text(path, "")
        return path

    def resolve_upload_path(self, source_path):
        """Вычисляет путь назначения для загружаемого файла, не копируя его."""
        base = os.path.basename(source_path)
        _check_not_reserved(base, "Переименуйте файл перед загрузкой.")
        return os.path.join(self.user_folder, base)

    def upload_file(self, source_path):
        """Копирует внешний файл в папку пользователя (перезаписывает при совпадении имени).

        Картинки и аудио копируются как есть (их читают напрямую QPixmap/QMediaPlayer).
        Всё остальное (в первую очередь .py/текст) шифруется тем же XOR при загрузке —
        иначе open_file() попытается расшифровать незашифрованный файл и покажет/сохранит
        испорченные данные.
        """
        dest = self.resolve_upload_path(source_path)
        ext = os.path.splitext(source_path.lower())[1]

        if ext in IMAGE_EXTENSIONS or ext in AUDIO_EXTENSIONS:
            shutil.copy2(source_path, dest)
        else:
            with open(source_path, "rb") as f:
                raw = f.read()
            with open(dest, "wb") as f:
                f.write(crypt_data(raw, self.user_name))

        return dest

    def delete_path(self, path):
        """Удаляет файл или папку целиком."""
        if os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path)

    def remove_if_exists(self, path):
        """Удаляет файл, если он существует; ошибки удаления игнорируются."""
        if os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass
