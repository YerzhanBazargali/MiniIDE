# 🖥️ MiniIDE

> 🇰🇿 [Қазақша](#қазақша) | 🇷🇺 [Русский](#русский) | 🇬🇧 [English](#english)

## ⬇️ Скачать / Жүктеу / Download

[![Download MiniIDE](https://img.shields.io/badge/⬇️%20Download%20MiniIDE%20v1.1.0-4285F4?style=for-the-badge&logo=googledrive&logoColor=white)](https://drive.google.com/drive/folders/14AxpIhI3Fu9XzbIhAeRQepFj9b667HSO?usp=sharing)

> Windows 10/11 · Установка не требуется · около 88 MB

> ⚠️ Бейдж показывает версию исходного кода в репозитории. Архив по ссылке нужно переупаковать и перезалить вручную после последних правок — если он ещё не обновлён, там может быть более старая сборка (v1.0.0). / Бейдж репозиторийдегі бастапқы код нұсқасын көрсетеді. Сілтемедегі мұрағатты соңғы түзетулерден кейін қолмен қайта жинап, қайта жүктеу керек. / The badge reflects the source code version in this repository. The linked archive must be manually repackaged and re-uploaded after the latest fixes — until then it may still be the older v1.0.0 build.

---

## Қазақша

### MiniIDE — мектептерге арналған Python оқу ортасы

**MiniIDE** — мектеп сыныбы үшін арнайы жасалған портативті Python даму ортасы. Оқушылар мен мұғалімдер Python немесе Pygame-ді **қолмен орнатпайды** — бәрі дайын, тек іске қосу жеткілікті.

### 🎯 Неге жасалды?

Мектеп сыныбында Python орнату — үлкен мәселе: әр компьютерге бөлек орнату, нұсқалар сәйкеспеуі, Pygame конфигурациясы, сабақ уақытының жоғалуы. **MiniIDE** осы мәселені толығымен шешеді:

- 📦 **Портативті Python** — `python_env/` қалтасында дайын, орнатуды қажет етпейді
- 🎮 **Pygame алдын ала орнатылған** — оқушы бірден ойын жазуды бастай алады
- 🔐 **Авторизация жүйесі** — әр оқушының жеке аккаунты, бір компьютерде бірнеше оқушы кезекпен жұмыс жасай алады
- 🔐 **Жеке жұмыс қалталары** — мәтіндік файлдар логинге байланысты XOR-обфускациямен сақталады; бұл толық қауіпсіздік немесе sandbox емес
- 💾 **EXE-файл ретінде жинақталған** — PyInstaller арқылы, ешқандай орнату қажет емес
- 👩‍🏫 **Мұғалім үшін ыңғайлы** — USB-флешкадан іске қосылады, баптаусыз жұмыс жасайды

### ✨ Мүмкіндіктер

- ▶️ Кодты тікелей IDE ішінде іске қосу (портативті Python арқылы)
- 📝 Python синтаксисін бөлектейтін код редакторы
- 🗂️ Жеке файлдар ағашы (әр оқушының өз жеке қалтасы)
- 🖼️ Суреттерді қарау (PNG, JPG, GIF)
- 🎵 Аудио файлдарды ойнату (MP3, WAV)
- 💾 Файлдарды шифрлап сақтау (XOR)
- ⌨️ F5 — іске қосу, Ctrl+S — сақтау

### 📸 Скриншоттар

![Авторизация және тіркелу](screenshots/authReg.png)
*Кіру және тіркелгі жасау терезесі. Әр оқушы өз логинімен кіреді — деректер шифрланады.*

![Басты бет](screenshots/mainPage.png)
*MiniIDE басты терезесі. Сол жақта файл ағашы, ортада код редакторы, төменде нәтиже шығатын консоль.*

![tkinter кодын іске қосу](screenshots/tkinter.png)
*tkinter кітапханасымен жазылған графикалық терезені іске қосу мысалы.*

![Pygame кодын іске қосу](screenshots/pygame.png)
*Pygame арқылы ойын кодын іске қосу. Портативті ортада дұрыс жұмыс істейді.*

![Суреттерді жүктеу](screenshots/imageViewer.png)
*MiniIDE ішінен PNG, JPG, GIF суреттерін ашу және қарау мүмкіндігі.*

### 🚀 Орнату және іске қосу

**1. Дайындық**
- Архивті жүктеп алып, қалыпты қалтаға шығарыңыз
- Қалта жолында кириллица болмауы керек: `C:\Tools\MiniIDE` ✅

**2. Қалта құрылымы**
```
MiniIDE/
├── MyMiniIDE.exe    ← негізгі файл
├── python_env/      ← портативті Python + Pygame
├── students/        ← оқушылардың жеке қалталары (автоматты жасалады)
└── _internal/       ← қызметтік компоненттер
```

**3. Бірінші іске қосу**
- `MyMiniIDE.exe` файлын іске қосыңыз
- Логин мен құпия сөзіңізді енгізіңіз
- Бірінші кіру кезінде аккаунт автоматты түрде жасалады — деректерді есте сақтаңыз!
- Логинде тек әріптер, сандар, `-` және `_` болуы мүмкін (бос орын мен нүктесіз)

**⚠️ Ақаулықтарды жою**

| Мәселе | Шешім |
|--------|-------|
| Консоль бос | `python_env/` қалтасы `MyMiniIDE.exe` қасында тұруы керек |
| Бағдарлама ашылмайды | Архивті қайта шығарып, `MyMiniIDE.exe` файлын `python_env/` және `_internal/` қалталарымен бірге іске қосыңыз |
| Антивирус бұғаттайды | Ерекшеліктерге қосыңыз (PyInstaller қолданбаларына жалған оң нәтиже) |

### 📁 Бастапқы код құрылымы

```
MiniIDE/
├── main.py            # IDE негізгі терезесі (UI)
├── auth.py            # Логин және деректерді XOR арқылы қорғау
├── storage.py         # Оқушы қалтасындағы файл операциялары
├── process_runner.py  # Кодты QProcess арқылы іске қосу
├── EditorPQT.py       # Синтаксисті бөлектейтін код редакторы
├── icon.ico           # Қолданба иконкасы
├── python_env/        # Портативті Python + Pygame (репозиторийде жоқ)
└── students/          # Бірінші іске қосқанда автоматты жасалады
```

> ⚠️ `python_env/` көлеміне байланысты репозиторийге жүктелмеген — жоғарыдағы батырма арқылы дайын архивті жүктеп алыңыз.

### 🛠️ Технологиялар

`Python` `PyQt6` `Pygame` `PyInstaller` `QProcess` `XOR Encryption`

### 🏗️ Жоба архитектурасы

- **GUI:** PyQt6 негізіндегі desktop интерфейс  
- **Code Execution:** QProcess арқылы бөлек процесс ретінде код орындау  
- **Python Runtime:** `python_env/` ішінде портативті интерпретатор  
- **Storage:** Жеке қалталар; мәтіндік файлдарға XOR-обфускация қолданылады, медиафайлдар өзгеріссіз сақталады  
- **Packaging:** PyInstaller арқылы EXE жинақтау  

### ⚠️ Шектеулері

- Windows-пен ғана жұмыс істейді (PyInstaller build)  
- Толық sandbox емес (QProcess арқылы базалық оқшаулау)  
- `python_env/` репозиторийде жоқ (көлеміне байланысты)  

### 🤔 Неге VS Code емес?

MiniIDE келесі жағдайлар үшін жасалған:

- Орнатуға рұқсат жоқ  
- Интернет шектеулі  
- Бір компьютерде бірнеше оқушы жұмыс істейді  

VS Code — қуатты құрал, бірақ орнатуды және баптауды талап етеді.  
MiniIDE — бірден іске қосылады, ешқандай дайындықсыз.

### 🚧 Болашақ жоспарлар (Roadmap)

- [ ] Linux жүйесін қолдау
- [ ] Қауіпсіз орындалу ортасын жақсарту (sandbox)
- [ ] Оқушы жобаларын бұлт арқылы сақтау
- [ ] Мұғалімге арналған басқару панелі
---

## Русский

### MiniIDE — учебная Python-среда для школьного класса

**MiniIDE** — портативная среда разработки, созданная специально для школьного урока программирования. Главная идея: **ни ученик, ни учитель ничего не устанавливают** — Python и Pygame уже включены, достаточно просто запустить программу.

### 🎯 Зачем это создано?

В школьном классе установка Python — настоящая головная боль: разные версии на разных компьютерах, проблемы с Pygame, потеря времени урока. MiniIDE решает это полностью:

- 📦 **Портативный Python** в папке `python_env/` — просто скопируй и запускай
- 🎮 **Pygame предустановлен** — ученик сразу пишет игры без дополнительных настроек
- 🔐 **Система авторизации** — у каждого ученика свой логин, несколько учеников работают на одном компьютере в разное время
- 🔐 **Отдельные рабочие папки** — текстовые файлы сохраняются с XOR-обфускацией по логину; это не полноценная защита от копирования или доступа к данным
- 💾 **Скомпилирован в EXE** через PyInstaller — установка не нужна
- 👩‍🏫 **Запускается с флешки** — принёс, запустил, работаешь

### ✨ Возможности

- ▶️ Запуск кода прямо в IDE через встроенный портативный Python
- 📝 Редактор кода с подсветкой синтаксиса Python
- 🗂️ Личная папка для каждого ученика (изолированные директории)
- 🖼️ Просмотр изображений (PNG, JPG, GIF)
- 🎵 Воспроизведение аудио (MP3, WAV)
- 💾 Шифрованное сохранение файлов (XOR по логину)
- ⌨️ Горячие клавиши: F5 — запуск, Ctrl+S — сохранение

### 📸 Скриншоты

![Авторизация и регистрация](screenshots/authReg.png)
*Окно входа и создания аккаунта. Каждый ученик входит под своим логином — данные шифруются.*

![Главное окно](screenshots/mainPage.png)
*Главное окно MiniIDE. Слева — дерево файлов, в центре — редактор кода, внизу — консоль вывода.*

![Запуск кода tkinter](screenshots/tkinter.png)
*Пример запуска графического окна на библиотеке tkinter.*

![Запуск кода Pygame](screenshots/pygame.png)
*Запуск игрового кода на Pygame. Работает в портативной среде без установки.*

![Просмотр изображений](screenshots/imageViewer.png)
*Открытие и просмотр изображений (PNG, JPG, GIF) прямо в MiniIDE.*

### 🚀 Установка и запуск

**1. Подготовка**
- Скачайте архив и **извлеките** все файлы в обычную папку
- В пути не должно быть кириллицы: `C:\Tools\MiniIDE` ✅, `C:\Рабочий стол\` ❌

**2. Структура папок**
```
MiniIDE/
├── MyMiniIDE.exe    ← запускать этот файл
├── python_env/      ← портативный Python + Pygame
├── students/        ← личные папки учеников (создаётся автоматически)
└── _internal/       ← служебные компоненты (не трогать)
```

> 💡 Для удобства: правая кнопка на `MyMiniIDE.exe` → «Отправить» → «Рабочий стол (создать ярлык)»

**3. Первый запуск**
- Запустите `MyMiniIDE.exe`
- Введите логин и пароль — при первом входе аккаунт создаётся автоматически
- Логин может содержать только буквы, цифры, `-` и `_` (без пробелов и точек)
- Запомните данные для следующих входов!

**4. Работа в редакторе**
- «📄 Создать файл» или «✚ Добавить файл» — создание/загрузка файлов
- **F5** или «▶ Запустить» — запуск кода
- Результат и ошибки — в нижней консоли
- Текстовые файлы сохраняются в обфусцированном виде; изображения и аудио хранятся без шифрования

**⚠️ Устранение неполадок**

| Проблема | Решение |
|----------|---------|
| Консоль пустая при запуске | Убедитесь, что `python_env/` лежит рядом с `MyMiniIDE.exe` |
| Программа не открывается | Повторно распакуйте архив и проверьте, что рядом с `MyMiniIDE.exe` находятся `python_env/` и `_internal/` |
| Антивирус блокирует | Добавьте в исключения (ложное срабатывание на PyInstaller) |

### 📁 Структура исходного кода

```
MiniIDE/
├── main.py            # Главное окно IDE (UI, связывание сигналов)
├── auth.py            # Логин и XOR-шифрование данных пользователя
├── storage.py         # Файловые операции в папке ученика (чтение/запись/загрузка)
├── process_runner.py  # Запуск кода через QProcess
├── EditorPQT.py       # Редактор кода с подсветкой синтаксиса
├── icon.ico           # Иконка приложения
├── python_env/        # Портативный Python + Pygame (не в репозитории)
└── students/          # Создаётся автоматически при первом запуске
```

> ⚠️ Папка `python_env/` не загружена в репозиторий из-за размера — скачайте готовый архив по кнопке выше.

### 🛠️ Стек технологий

`Python` `PyQt6` `Pygame` `PyInstaller` `QProcess` `QFileSystemModel` `XOR Encryption`

### 🏗️ Архитектура проекта

- **GUI**: PyQt6 — десктопный интерфейс с файловым деревом и редактором кода
- **Запуск кода**: запуск в дочернем процессе через QProcess; это не полноценная изоляция и остановка зависшего процесса может ненадолго блокировать интерфейс
- **Python Runtime**: встроенный портативный интерпретатор из папки `python_env/`
- **Хранение данных**: локальные папки учеников с XOR-шифрованием (по логину)
- **Сборка**: PyInstaller — папка приложения с EXE и служебными файлами

### ⚠️ Известные ограничения

- **Только Windows** — сборка под PyInstaller, Linux/macOS не поддерживаются
- **Базовая изоляция процессов** — не является полноценной песочницей (ученик с опытом может выйти за пределы)
- **python_env/ не в репозитории** — из-за размера, скачивается отдельно (см. кнопку выше)
- **XOR — обфускация, не настоящее шифрование**; изображения и аудио не шифруются

### 🤔 Почему не VS Code?

VS Code — мощный инструмент, но в школьном классе он требует:
- Установки на каждый компьютер
- Прав администратора
- Настройки Python окружения
- Интернета для расширений

**MiniIDE** создан для ограниченных условий:
- Компьютеры без прав администратора
- Медленный или отсутствующий интернет
- Один компьютер на несколько учеников в разное время

MiniIDE не заменяет VS Code. Он решает задачу, которую VS Code не решает — **zero-setup программирование в школьном классе**.

### 🚧 Планы развития (Roadmap)

- [ ] **Linux support** — упаковка в AppImage
- [ ] **Настоящая песочница** — ограничение доступа к файловой системе
- [ ] **Cloud sync** — чтобы ученик мог продолжить дома
- [ ] **Дашборд учителя** — просмотр работ всех учеников
- [ ] **Поддержка MicroPython** — для уроков с микроконтроллерами

### 💡 Применение в классе

Разработано и активно используется на уроках информатики в **PhysTech School Almaty**. Учитель один раз настраивает папку — ученики запускают `MyMiniIDE.exe`, вводят логин и начинают писать код. Никакой установки, никакого списывания, никакой потери времени урока.

### 👨‍💻 Автор

**Ержан Базаргали** — учитель информатики, PhysTech School Almaty
📧 eginsu86@gmail.com | [LinkedIn](https://linkedin.com/in/ebazargali) | [GitHub](https://github.com/YerzhanBazargali)

---

## English

### MiniIDE — Zero-Setup Python IDE for School Classrooms

**MiniIDE** is a portable, classroom-ready Python development environment. The core idea: **students and teachers install nothing**. Python and Pygame are supplied in the distribution folder — copy the complete folder to a Windows PC and run it without installation.

### 🎯 Why it was built

Installing Python in a school computer lab is a recurring problem: version mismatches, missing Pygame, wasted lesson time, IT department dependency. MiniIDE solves all of it:

- 📦 **Portable Python bundled** in `python_env/` — no system installation, works on any Windows PC
- 🎮 **Pygame pre-installed** — students write games from day one, zero extra setup
- 🔐 **Per-student login system** — each student has their own encrypted account; multiple students share one computer across sessions without conflict
- 🔐 **Separate work folders** — text files use username-based XOR obfuscation; this is not a full security boundary or sandbox
- 💾 **Compiled to EXE** via PyInstaller — just double-click and run
- 👩‍🏫 **Runs from a USB drive** — bring it to any classroom, plug in and teach

### ✨ Features

- ▶️ Run Python code inside the IDE via bundled portable Python (QProcess)
- 📝 Code editor with Python syntax highlighting
- 🗂️ Isolated personal file tree per student
- 🖼️ Image viewer (PNG, JPG, GIF)
- 🎵 Audio playback (MP3, WAV)
- 💾 Encrypted file storage (XOR keyed by username)
- ⌨️ Keyboard shortcuts: F5 to run, Ctrl+S to save

### 📸 Screenshots

![Login and Registration](screenshots/authReg.png)
*Login and account creation window. Each student logs in with their own credentials — data is encrypted.*

![Main Window](screenshots/mainPage.png)
*MiniIDE main window. Left: file tree, center: code editor, bottom: output console.*

![Running tkinter Code](screenshots/tkinter.png)
*Example of running a graphical window using the tkinter library.*

![Running Pygame Code](screenshots/pygame.png)
*Running game code with Pygame. Works in a portable environment with no installation required.*

![Viewing Images](screenshots/imageViewer.png)
*Opening and viewing images (PNG, JPG, GIF) directly inside MiniIDE.*

### 🚀 Installation & Setup

**1. Preparation**
- Download the archive and **extract all files** to a regular folder
- Avoid Cyrillic characters in the folder path: `C:\Tools\MiniIDE` ✅

**2. Folder Structure**
```
MiniIDE/
├── MyMiniIDE.exe    ← launch this file
├── python_env/      ← portable Python + Pygame
├── students/        ← per-student encrypted folders (auto-created)
└── _internal/       ← app internals (do not modify)
```

> 💡 Tip: right-click `MyMiniIDE.exe` → Send to → Desktop (create shortcut)

**3. First Launch**
- Run `MyMiniIDE.exe`
- Enter a login and password — account is created automatically on first login
- Login can only contain letters, digits, `-` and `_` (no spaces or dots)
- Remember your credentials for future sessions!

**4. Using the Editor**
- "📄 Create file" or "✚ Add file" — create or import files
- **F5** or "▶ Run" — execute the code
- Output and errors appear in the bottom console
- Text files are stored in obfuscated form; images and audio are not encrypted

**⚠️ Troubleshooting**

| Issue | Solution |
|-------|----------|
| Console is empty on run | Make sure `python_env/` is in the same folder as `MyMiniIDE.exe` |
| App won't open | Re-extract the archive and check that `python_env/` and `_internal/` are next to `MyMiniIDE.exe` |
| Antivirus blocks it | Add to exclusions (false positive — common with PyInstaller apps) |

### 📁 Source Structure

```
MiniIDE/
├── main.py            # Main IDE window (UI, signal wiring)
├── auth.py            # Login and XOR obfuscation of user data
├── storage.py         # File operations in the student's folder (read/write/upload)
├── process_runner.py  # Runs student code via QProcess
├── EditorPQT.py       # Code editor with syntax highlighting
├── icon.ico           # Application icon
├── python_env/        # Portable Python + Pygame (not in repo — too large)
└── students/          # Auto-created on first run
```

> ⚠️ `python_env/` is excluded from the repository. Download the full ready-to-use archive using the button at the top.

### 🛠️ Tech Stack

`Python` `PyQt6` `Pygame` `PyInstaller` `QProcess` `QFileSystemModel` `XOR Encryption`

### 🏗️ Architecture

- GUI: PyQt6-based desktop interface
- Code Execution: Child-process execution via QProcess; this is not a secure sandbox
- Python Runtime: Portable interpreter supplied in `python_env/`
- Storage: Per-user directories; text files use XOR obfuscation, while media files are stored unchanged
- Packaging: PyInstaller onedir distribution with the EXE and support files

### ⚠️ Limitations

- Windows-only (due to PyInstaller build)
- Not a secure sandbox; student code runs with the current user's OS permissions
- If `python_env/` is missing, the application may fall back to system Python, which may not have Pygame installed
> Note: XOR encryption is used as a lightweight obfuscation method, not as secure encryption.

### 🤔 Why not VS Code?

MiniIDE is designed for constrained classroom environments where:
- Installation is restricted
- Internet access is limited
- Students share computers

VS Code is powerful, but requires setup. MiniIDE works from its complete distribution folder without installing Python or Pygame.

### 🚧 Roadmap

- [ ] Linux support
- [ ] True sandboxing (restricted execution)
- [ ] Cloud sync for student projects
- [ ] Teacher dashboard

### 💡 Real Classroom Use

Built and actively used at **PhysTech School Almaty**. The teacher sets up the folder once. Students launch `MyMiniIDE.exe`, log in, and start coding — no installation, separate work folders, and less wasted class time.

### 👨‍💻 Author

**Yerzhan Bazargali** — Computer Science Teacher, PhysTech School Almaty
📧 eginsu86@gmail.com | [LinkedIn](https://linkedin.com/in/ebazargali) | [GitHub](https://github.com/YerzhanBazargali)

---

*Built for real classrooms. Solving real problems.* 🏫
