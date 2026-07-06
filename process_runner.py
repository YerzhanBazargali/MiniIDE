"""Запуск пользовательского кода через QProcess с портативным Python."""
import os
import sys

from PyQt6.QtCore import QObject, QProcess, pyqtSignal


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

        if not os.path.exists(py_exe) and py_exe != "python":
            return "python", True
        return py_exe, False

    def run(self, script_path, working_dir):
        """Запускает script_path в working_dir. Возвращает True, если использован системный python."""
        py_exe, used_fallback = self.resolve_python_exe()
        self.process.setWorkingDirectory(working_dir)
        self.process.start(py_exe, [script_path])
        return used_fallback

    def _handle_out(self):
        raw = self.process.readAllStandardOutput().data()
        self.output_received.emit(self._decode(raw))

    def _handle_err(self):
        raw = self.process.readAllStandardError().data()
        self.error_received.emit(self._decode(raw))

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
    def _decode(raw_data):
        try:
            return raw_data.decode("utf-8")
        except UnicodeDecodeError:
            return raw_data.decode("cp1251", "replace")
