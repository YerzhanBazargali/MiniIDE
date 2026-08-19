"""Запуск пользовательского кода через QProcess с портативным Python."""
import codecs
import os
import sys

from PyQt6.QtCore import QObject, QProcess, QProcessEnvironment, pyqtSignal


class ProcessRunner(QObject):
    """Инкапсулирует поиск интерпретатора и управление QProcess."""

    output_received = pyqtSignal(str)
    error_received = pyqtSignal(str)
    finished = pyqtSignal()
    start_failed = pyqtSignal(str)

    def __init__(self, root_dir, parent=None):
        super().__init__(parent)
        self.root_dir = root_dir
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self._handle_out)
        self.process.readyReadStandardError.connect(self._handle_err)
        self.process.finished.connect(self.finished.emit)
        self.process.errorOccurred.connect(self._handle_error_occurred)

        # Отдельный инкрементальный декодер на каждый поток: readyRead может
        # отдать данные так, что многобайтовый UTF-8-символ (например,
        # кириллица) окажется разрезан ровно на границе двух чанков.
        # Инкрементальный декодер сам буферизует незавершённый хвост до
        # следующего чанка — обычный .decode() по чанкам на такой границе
        # падал бы и уходил в cp1251-фолбэк, портя вывод.
        self._out_decoder = codecs.getincrementaldecoder("utf-8")()
        self._err_decoder = codecs.getincrementaldecoder("utf-8")()

    def is_running(self):
        return self.process.state() != QProcess.ProcessState.NotRunning

    def ensure_stopped(self):
        """Останавливает предыдущий процесс перед новым запуском (например, по F5).

        Короткий таймаут на мягкое закрытие: чаще всего здесь перезапускается
        обычный консольный скрипт без окна, который terminate() всё равно
        проигнорирует — незачем морозить интерфейс на секунду ради этого на
        каждый F5. Программе с окном (tkinter/pygame) 300 мс обычно хватает,
        чтобы среагировать на закрытие.
        """
        if self.is_running():
            self._graceful_stop(soft_timeout_ms=300)

    def stop(self):
        """Останавливает процесс по явному нажатию «⏹ Остановить».

        Здесь, в отличие от ensure_stopped(), можно позволить себе более
        щедрый таймаут — это осознанное разовое действие пользователя, а не
        то, что срабатывает при каждом F5.
        """
        if self.is_running():
            self._graceful_stop(soft_timeout_ms=1000)

    def _graceful_stop(self, soft_timeout_ms):
        """Пробует terminate() (SIGTERM/WM_CLOSE), и только если процесс не
        среагировал за soft_timeout_ms — добивает kill()."""
        self.process.terminate()
        if not self.process.waitForFinished(soft_timeout_ms):
            self.process.kill()
            self.process.waitForFinished(1000)

    def resolve_python_exe(self):
        """Возвращает (путь_к_python, использован_ли_системный_fallback)."""
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
            path_root = os.path.join(base_dir, "python_env", "python.exe")
            path_internal = os.path.join(base_dir, "_internal", "python_env", "python.exe")
            py_exe = path_internal if os.path.exists(path_internal) else path_root
        else:
            py_exe = os.path.join(self.root_dir, "python_env", "python.exe")

        if not os.path.exists(py_exe):
            return "python", True
        return py_exe, False

    def run(self, script_path, working_dir):
        """Запускает script_path в working_dir. Возвращает True, если использован системный python."""
        py_exe, used_fallback = self.resolve_python_exe()
        # Сбрасываем декодеры на новый запуск — иначе незавершённый хвост
        # многобайтового символа, оставшийся от предыдущего процесса (мало
        # вероятно, но возможно при принудительном kill() посреди вывода),
        # склеился бы с первым чанком нового запуска.
        self._out_decoder.reset()
        self._err_decoder.reset()

        # На Windows дочерний python.exe по умолчанию кодирует stdout/stderr
        # кодовой страницей консоли (например, cp1251), а не UTF-8. В cp1251
        # нет специфических казахских букв (ә, қ, ғ, ң, ...) — print() с ними
        # валит скрипт ученика UnicodeEncodeError'ом ещё до того, как вывод
        # вообще доходит до наших декодеров. PYTHONIOENCODING заставляет сам
        # интерпретатор писать UTF-8 независимо от кодовой страницы консоли.
        # PYTHONUNBUFFERED отключает буферизацию stdout: без него stdout при
        # перенаправлении в канал (в отличие от stderr) буферизуется блоками,
        # и строки из stderr в логе могут "обгонять" более ранние по коду
        # строки из stdout, которые ещё сидят в буфере интерпретатора.
        env = QProcessEnvironment.systemEnvironment()
        env.insert("PYTHONIOENCODING", "utf-8")
        env.insert("PYTHONUNBUFFERED", "1")
        self.process.setProcessEnvironment(env)

        self.process.setWorkingDirectory(working_dir)
        self.process.start(py_exe, [script_path])
        return used_fallback

    def _handle_out(self):
        raw = self.process.readAllStandardOutput().data()
        self.output_received.emit(self._decode(raw, self._out_decoder))

    def _handle_err(self):
        raw = self.process.readAllStandardError().data()
        self.error_received.emit(self._decode(raw, self._err_decoder))

    def _handle_error_occurred(self, error):
        # finished-сигнал в этом случае не приходит, поэтому UI не узнает о сбое
        # без отдельного сигнала — например, если не найден ни портативный, ни
        # системный python.
        if error == QProcess.ProcessError.FailedToStart:
            self.start_failed.emit(
                "Не удалось запустить интерпретатор Python. "
                "Проверьте, что python_env/ лежит рядом с приложением."
            )

    @staticmethod
    def _decode(raw_data, decoder):
        try:
            return decoder.decode(raw_data)
        except UnicodeDecodeError:
            # Не просто разрезанный многобайтовый символ, а действительно
            # не-UTF8 вывод (например, консоль Windows отдаёт cp1251) —
            # сбрасываем накопленное состояние декодера и решифруем этот
            # кусок как cp1251, как и раньше.
            decoder.reset()
            return raw_data.decode("cp1251", "replace")
