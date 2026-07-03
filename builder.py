import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import subprocess
import base64
import shutil
import json
import tempfile
import locale
import re
from pathlib import Path

try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

def get_system_language():
    try:
        lang, _ = locale.getdefaultlocale()
        if lang:
            if lang.startswith('ru'):
                return 'ru'
            elif lang.startswith('uk'):
                return 'uk'
        return 'en'
    except:
        return 'en'

def translit(text):
    cyrillic = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"
    latin = ("abvgdeejzijklmnoprstufhcchssyyeua"
             "ABVGDEEJZIJKLMNOPRSTUFHCCHSSYYEUA")
    trans = str.maketrans(cyrillic, latin)
    result = text.translate(trans)
    result = re.sub(r'[^\w\s\-]', '', result)
    result = re.sub(r'\s+', '_', result)
    return result

# -------------------- ПЕРЕВОДЫ ДЛЯ КОНСТРУКТОРА --------------------
TR = {
    'ru': {
        'title': 'Конструктор установщиков',
        'subtitle': 'После нажатие на кнопку надо подождать! (Ют: Faze4ik)',
        'type_label': 'Тип файла:',
        'type_exe': 'EXE файл',
        'type_zip': 'ZIP архив',
        'file_label': 'Файл программы:',
        'browse': 'Обзор...',
        'logo_label': 'Логотип (PNG)',
        'icon_label': 'Иконка установщика (ICO)',
        'name_label': 'Название программы',
        'path_label': 'Папка установки по умолчанию (авто)',
        'shortcuts_label': 'Создать ярлыки в меню Пуск и на рабочем столе',
        'build_btn': '🚀 Собрать установщик',
        'log_label': 'Лог сборки',
        'status_ready': 'Готов к сборке',
        'status_generating': 'Генерация скрипта установщика...',
        'status_checking': 'Проверка синтаксиса...',
        'status_building': 'Сборка установщика...',
        'status_done': 'Готово!',
        'status_error': 'Ошибка сборки',
        'error_no_file': 'Выберите существующий файл программы.',
        'error_no_name': 'Введите название программы.',
        'error_pyinstaller': 'Не удалось установить PyInstaller:',
        'error_build': 'Не удалось создать установщик:',
        'log_pyinstaller_not_found': 'PyInstaller не найден. Устанавливаю...',
        'log_pyinstaller_installed': 'PyInstaller успешно установлен.',
        'log_preparing': 'Подготовка файлов...',
        'log_script_created': 'Скрипт установщика сохранён:',
        'log_icon_from_logo': 'Иконка окна создана из логотипа.',
        'log_icon_from_png_fail': 'Не удалось создать иконку из PNG:',
        'log_icon_for_exe': 'Иконка для EXE создана из логотипа.',
        'log_icon_for_exe_fail': 'Не удалось создать иконку для EXE:',
        'log_icon_not_specified': 'Иконка для EXE не указана, будет стандартная.',
        'log_building': 'Сборка установщика в',
        'log_cmd': 'Команда:',
        'log_success': '✅ Установщик успешно создан:',
        'log_renamed': '✅ Установщик переименован и сохранён:',
        'log_error': '❌ Ошибка:',
        'lang_label': '🌖:',
        'check_syntax': 'Проверка синтаксиса...',
        'syntax_ok': 'Синтаксис скрипта верен.',
        'syntax_error': 'Ошибка синтаксиса:',
        'step_reading': 'Чтение файла программы...',
        'step_logo': 'Обработка логотипа...',
        'step_icon': 'Обработка иконки...',
        'step_embedded': 'Подготовка встраиваемых данных...',
        'step_script': 'Генерация скрипта установщика...',
        'step_syntax': 'Проверка синтаксиса скрипта...',
        'step_pyinstaller': 'Запуск PyInstaller...',
        'step_finish': 'Сборка завершена.',
        'path_auto': 'Путь будет сгенерирован автоматически из названия программы.',
    },
    'en': {
        'title': 'Installer Builder',
        'subtitle': 'Create a professional installer in a few clicks',
        'type_label': 'File type:',
        'type_exe': 'EXE file',
        'type_zip': 'ZIP archive',
        'file_label': 'Program file:',
        'browse': 'Browse...',
        'logo_label': 'Logo (PNG)',
        'icon_label': 'Installer icon (ICO)',
        'name_label': 'Program name',
        'path_label': 'Default installation folder (auto)',
        'shortcuts_label': 'Create shortcuts in Start menu and on Desktop',
        'build_btn': '🚀 Build installer',
        'log_label': 'Build log',
        'status_ready': 'Ready to build',
        'status_generating': 'Generating installer script...',
        'status_checking': 'Checking syntax...',
        'status_building': 'Building installer...',
        'status_done': 'Done!',
        'status_error': 'Build error',
        'error_no_file': 'Select an existing program file.',
        'error_no_name': 'Enter the program name.',
        'error_pyinstaller': 'Failed to install PyInstaller:',
        'error_build': 'Failed to build installer:',
        'log_pyinstaller_not_found': 'PyInstaller not found. Installing...',
        'log_pyinstaller_installed': 'PyInstaller successfully installed.',
        'log_preparing': 'Preparing files...',
        'log_script_created': 'Installer script saved:',
        'log_icon_from_logo': 'Window icon created from logo.',
        'log_icon_from_png_fail': 'Failed to create icon from PNG:',
        'log_icon_for_exe': 'EXE icon created from logo.',
        'log_icon_for_exe_fail': 'Failed to create EXE icon:',
        'log_icon_not_specified': 'EXE icon not specified, using default.',
        'log_building': 'Building installer to',
        'log_cmd': 'Command:',
        'log_success': '✅ Installer successfully created:',
        'log_renamed': '✅ Installer renamed and saved:',
        'log_error': '❌ Error:',
        'lang_label': '🌖:',
        'check_syntax': 'Checking syntax...',
        'syntax_ok': 'Script syntax is valid.',
        'syntax_error': 'Syntax error:',
        'step_reading': 'Reading program file...',
        'step_logo': 'Processing logo...',
        'step_icon': 'Processing icon...',
        'step_embedded': 'Preparing embedded data...',
        'step_script': 'Generating installer script...',
        'step_syntax': 'Checking script syntax...',
        'step_pyinstaller': 'Running PyInstaller...',
        'step_finish': 'Build completed.',
        'path_auto': 'Path will be generated automatically from program name.',
    },
    'uk': {
        'title': 'Конструктор інсталяторів',
        'subtitle': 'Створіть професійний інсталятор за кілька кліків',
        'type_label': 'Тип файлу:',
        'type_exe': 'EXE файл',
        'type_zip': 'ZIP архів',
        'file_label': 'Файл програми:',
        'browse': 'Огляд...',
        'logo_label': 'Логотип (PNG)',
        'icon_label': 'Іконка інсталятора (ICO)',
        'name_label': 'Назва програми',
        'path_label': 'Папка встановлення за замовчуванням (авто)',
        'shortcuts_label': 'Створити ярлики в меню Пуск та на робочому столі',
        'build_btn': '🚀 Зібрати інсталятор',
        'log_label': 'Журнал збірки',
        'status_ready': 'Готовий до збірки',
        'status_generating': 'Генерація скрипту інсталятора...',
        'status_checking': 'Перевірка синтаксису...',
        'status_building': 'Збірка інсталятора...',
        'status_done': 'Готово!',
        'status_error': 'Помилка збірки',
        'error_no_file': 'Виберіть існуючий файл програми.',
        'error_no_name': 'Введіть назву програми.',
        'error_pyinstaller': 'Не вдалося встановити PyInstaller:',
        'error_build': 'Не вдалося створити інсталятор:',
        'log_pyinstaller_not_found': 'PyInstaller не знайдено. Встановлюю...',
        'log_pyinstaller_installed': 'PyInstaller успішно встановлено.',
        'log_preparing': 'Підготовка файлів...',
        'log_script_created': 'Скрипт інсталятора збережено:',
        'log_icon_from_logo': 'Іконку вікна створено з логотипу.',
        'log_icon_from_png_fail': 'Не вдалося створити іконку з PNG:',
        'log_icon_for_exe': 'Іконку для EXE створено з логотипу.',
        'log_icon_for_exe_fail': 'Не вдалося створити іконку для EXE:',
        'log_icon_not_specified': 'Іконку для EXE не вказано, буде стандартна.',
        'log_building': 'Збірка інсталятора в',
        'log_cmd': 'Команда:',
        'log_success': '✅ Інсталятор успішно створено:',
        'log_renamed': '✅ Інсталятор перейменовано та збережено:',
        'log_error': '❌ Помилка:',
        'lang_label': '🌖:',
        'check_syntax': 'Перевірка синтаксису...',
        'syntax_ok': 'Синтаксис скрипту правильний.',
        'syntax_error': 'Помилка синтаксису:',
        'step_reading': 'Читання файлу програми...',
        'step_logo': 'Обробка логотипу...',
        'step_icon': 'Обробка іконки...',
        'step_embedded': 'Підготовка вбудованих даних...',
        'step_script': 'Генерація скрипту інсталятора...',
        'step_syntax': 'Перевірка синтаксису скрипту...',
        'step_pyinstaller': 'Запуск PyInstaller...',
        'step_finish': 'Збірка завершена.',
        'path_auto': 'Шлях буде створено автоматично з назви програми.',
    }
}

# ------------------------------------------------------------
# ШАБЛОН УСТАНОВЩИКА (с автозакрытием и запуском программы)
# ------------------------------------------------------------
INSTALLER_TEMPLATE = '''import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import base64
import shutil
import zipfile
import threading
import tempfile
import json
import subprocess
import ctypes

EMBEDDED_DATA = {embedded_data}
LANG_CODE = {lang_code!r}
CREATE_SHORTCUTS = {create_shortcuts!r}

# -------------------- ПРОВЕРКА ПРАВ --------------------
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def run_as_admin():
    try:
        args = [sys.executable] + sys.argv
        cmd = ' '.join('"' + arg + '"' if ' ' in arg else arg for arg in args)
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, cmd, None, 1)
        return True
    except:
        return False

# -------------------- ПЕРЕВОДЫ --------------------
TR = {{
    'ru': {{
        'window_title': 'Установка {{program_name}}',
        'folder_label': 'Папка установки:',
        'browse_btn': 'Обзор...',
        'install_btn': 'Установить',
        'launch_after': 'Запустить программу после установки',
        'progress_percent': '{{percent}}%',
        'status_ready': 'Готов к установке',
        'status_installing': 'Установка...',
        'status_success': 'Установка завершена!',
        'status_error': 'Ошибка установки',
        'msg_success_title': 'Успех',
        'msg_success_text': '{{program_name}} успешно установлен!',
        'msg_error_title': 'Ошибка',
        'msg_error_text': 'Не удалось установить программу:\\n{{error}}',
        'error_folder_empty': 'Укажите папку установки.',
        'error_create_folder': 'Не удалось создать папку:\\n{{error}}',
        'error_access_denied': 'Нет прав на запись в выбранную папку.\\nПопробуйте выбрать другую папку или запустите установщик от имени администратора.',
        'error_access_title': 'Недостаточно прав',
        'admin_required': 'Для установки в системную папку требуются права администратора.',
        'need_admin': 'Установщик требует прав администратора.\\nНажмите "Да", чтобы перезапустить с правами администратора.',
        'launch_failed': 'Не удалось запустить программу.\\nПопробуйте запустить вручную из папки установки.',
    }},
    'en': {{
        'window_title': 'Installing {{program_name}}',
        'folder_label': 'Installation folder:',
        'browse_btn': 'Browse...',
        'install_btn': 'Install',
        'launch_after': 'Launch program after installation',
        'progress_percent': '{{percent}}%',
        'status_ready': 'Ready to install',
        'status_installing': 'Installing...',
        'status_success': 'Installation completed!',
        'status_error': 'Installation error',
        'msg_success_title': 'Success',
        'msg_success_text': '{{program_name}} has been installed successfully!',
        'msg_error_title': 'Error',
        'msg_error_text': 'Failed to install program:\\n{{error}}',
        'error_folder_empty': 'Specify installation folder.',
        'error_create_folder': 'Could not create folder:\\n{{error}}',
        'error_access_denied': 'No write permission to the selected folder.\\nTry choosing another folder or run the installer as administrator.',
        'error_access_title': 'Insufficient rights',
        'admin_required': 'Administrator rights are required to install to system folder.',
        'need_admin': 'Installer requires administrator rights.\\nClick "Yes" to restart with administrator rights.',
        'launch_failed': 'Failed to launch the program.\\nPlease try running it manually from the installation folder.',
    }},
    'uk': {{
        'window_title': 'Встановлення {{program_name}}',
        'folder_label': 'Папка встановлення:',
        'browse_btn': 'Огляд...',
        'install_btn': 'Встановити',
        'launch_after': 'Запустити програму після встановлення',
        'progress_percent': '{{percent}}%',
        'status_ready': 'Готовий до встановлення',
        'status_installing': 'Встановлення...',
        'status_success': 'Встановлення завершено!',
        'status_error': 'Помилка встановлення',
        'msg_success_title': 'Успіх',
        'msg_success_text': '{{program_name}} успішно встановлено!',
        'msg_error_title': 'Помилка',
        'msg_error_text': 'Не вдалося встановити програму:\\n{{error}}',
        'error_folder_empty': 'Вкажіть папку встановлення.',
        'error_create_folder': 'Не вдалося створити папку:\\n{{error}}',
        'error_access_denied': 'Немає прав на запис у вибрану папку.\\nСпробуйте вибрати іншу папку або запустіть інсталятор від імені адміністратора.',
        'error_access_title': 'Недостатньо прав',
        'admin_required': 'Для встановлення в системну папку потрібні права адміністратора.',
        'need_admin': 'Інсталятор потребує прав адміністратора.\\nНатисніть "Так", щоб перезапустити з правами адміністратора.',
        'launch_failed': 'Не вдалося запустити програму.\\nСпробуйте запустити вручну з папки встановлення.',
    }}
}}

def _(key, **kwargs):
    lang = LANG_CODE if LANG_CODE in TR else 'en'
    text = TR.get(lang, {{}}).get(key, key)
    if kwargs:
        text = text.format(**kwargs)
    return text

class InstallerApp:
    def __init__(self, root):
        if not is_admin():
            result = messagebox.askyesno(
                _('error_access_title'),
                _('need_admin')
            )
            if result:
                run_as_admin()
            root.quit()
            return

        self.root = root
        self.root.title(_('window_title', program_name=EMBEDDED_DATA['program_name']))
        self.root.geometry("520x460")
        self.root.resizable(False, False)
        self.root.configure(bg="#ffffff")

        self.set_window_icon()

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background="#ffffff")
        self.style.configure('TLabel', background="#ffffff", font=('Segoe UI', 10), foreground="#2d3436")
        self.style.configure('Header.TLabel', font=('Segoe UI', 18, 'bold'), foreground="#2d3436")
        self.style.configure('Card.TFrame', background="#ffffff", relief='flat', borderwidth=0)
        self.style.configure('Accent.TButton', font=('Segoe UI', 10, 'bold'), foreground='white', background="#27ae60")
        self.style.map('Accent.TButton', background=[('active', '#2ecc71')])

        header_frame = ttk.Frame(root)
        header_frame.pack(fill=tk.X, pady=(20,10))
        self.create_logo(header_frame)
        ttk.Label(header_frame, text=EMBEDDED_DATA['program_name'], style='Header.TLabel').pack()

        card = ttk.Frame(root, style='Card.TFrame')
        card.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)

        target_frame = ttk.Frame(card)
        target_frame.pack(fill=tk.X, pady=10)
        self.target_path = tk.StringVar(value=os.path.expanduser(EMBEDDED_DATA['default_path']))
        ttk.Label(target_frame, text=_('folder_label'), foreground="#2d3436").pack(anchor=tk.W)
        entry_frame = ttk.Frame(target_frame)
        entry_frame.pack(fill=tk.X, pady=5)
        ttk.Entry(entry_frame, textvariable=self.target_path, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        ttk.Button(entry_frame, text=_('browse_btn'), command=self.browse_folder).pack(side=tk.RIGHT)

        self.launch_var = tk.BooleanVar(value=True)
        launch_check = ttk.Checkbutton(
            card,
            text=_('launch_after'),
            variable=self.launch_var,
            style='TCheckbutton'
        )
        launch_check.pack(pady=(5, 0), anchor=tk.W)

        self.install_btn = ttk.Button(card, text=_('install_btn'), command=self.start_install, style='Accent.TButton')
        self.install_btn.pack(pady=10)

        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(card, orient=tk.HORIZONTAL, length=400, mode='determinate', variable=self.progress_var)
        self.progress.pack(pady=5)
        self.progress_label = ttk.Label(card, text=_('progress_percent', percent=0), foreground="#2d3436", background="white", font=('Segoe UI', 9))
        self.progress_label.pack()

        self.status_label = ttk.Label(card, text=_('status_ready'), foreground="#636e72", background="white")
        self.status_label.pack(pady=5)

        if hasattr(self, '_ico_path'):
            self.root.after(2000, lambda: os.unlink(self._ico_path) if os.path.exists(self._ico_path) else None)

    def set_window_icon(self):
        icon_b64 = EMBEDDED_DATA.get('icon_data', '')
        if not icon_b64:
            return
        try:
            ico_data = base64.b64decode(icon_b64)
            with tempfile.NamedTemporaryFile(suffix='.ico', delete=False) as f:
                f.write(ico_data)
                self._ico_path = f.name
            self.root.iconbitmap(self._ico_path)
        except Exception as e:
            pass

    def create_logo(self, parent):
        logo_frame = ttk.Frame(parent)
        logo_frame.pack(pady=5)
        try:
            logo_data = base64.b64decode(EMBEDDED_DATA['logo_data'])
            import io
            from PIL import Image, ImageTk
            img = Image.open(io.BytesIO(logo_data))
            img = img.resize((80, 80), Image.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(img)
            ttk.Label(logo_frame, image=self.logo_img, background="#ffffff").pack()
        except:
            canvas = tk.Canvas(logo_frame, width=80, height=80, bg="#ffffff", highlightthickness=0)
            canvas.pack()
            canvas.create_oval(20, 20, 60, 60, outline="#27ae60", width=3)
            canvas.create_text(40, 40, text="⚙", fill="#2d3436", font=('Segoe UI', 30))

    def browse_folder(self):
        folder = filedialog.askdirectory(title=_('folder_label'))
        if folder:
            self.target_path.set(folder)

    def update_progress(self, value, max_val=100):
        percent = int((value / max_val) * 100)
        self.progress_var.set(percent)
        self.progress_label.config(text=_('progress_percent', percent=percent))
        self.root.update()

    def start_install(self):
        target = self.target_path.get().strip()
        if not target:
            messagebox.showerror(_('msg_error_title'), _('error_folder_empty'))
            return

        try:
            os.makedirs(target, exist_ok=True)
        except Exception as e:
            messagebox.showerror(_('error_access_title'), _('error_create_folder', error=str(e)))
            return

        try:
            test_file = os.path.join(target, '.write_test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
        except Exception as e:
            messagebox.showerror(_('error_access_title'), _('error_access_denied'))
            return

        self.install_btn.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self.progress_label.config(text=_('progress_percent', percent=0))
        self.status_label.config(text=_('status_installing'), foreground="#2980b9")
        threading.Thread(target=self.install, daemon=True).start()

    def install(self):
        try:
            dst = self.target_path.get()
            file_data = base64.b64decode(EMBEDDED_DATA['file_data'])
            temp_dir = tempfile.mkdtemp(prefix="installer_")
            temp_file_path = os.path.join(temp_dir, EMBEDDED_DATA['filename'])
            with open(temp_file_path, 'wb') as f:
                f.write(file_data)

            total_steps = 3
            step = 1
            main_exe = None

            if EMBEDDED_DATA['install_type'] == 'exe':
                dest = os.path.join(dst, EMBEDDED_DATA['filename'])
                shutil.copy2(temp_file_path, dest)
                self.update_progress(step, total_steps)
                step += 1
                main_exe = dest
            else:
                with zipfile.ZipFile(temp_file_path, 'r') as zf:
                    members = zf.infolist()
                    total_files = len(members)
                    for i, member in enumerate(members, 1):
                        zf.extract(member, dst)
                        if i % 5 == 0 or i == total_files:
                            self.update_progress(i, total_files)
                self.update_progress(total_steps, total_steps)
                for f in os.listdir(dst):
                    if f.lower().endswith('.exe'):
                        main_exe = os.path.join(dst, f)
                        break

            if CREATE_SHORTCUTS and main_exe and os.path.exists(main_exe):
                self.create_shortcuts(main_exe)

            shutil.rmtree(temp_dir, ignore_errors=True)

            # Запуск программы после установки, если галочка включена
            launch = self.launch_var.get()
            if launch and main_exe and os.path.exists(main_exe):
                try:
                    subprocess.Popen([main_exe], cwd=os.path.dirname(main_exe))
                except Exception as e:
                    self.root.after(0, lambda: messagebox.showwarning(
                        _('msg_error_title'),
                        _('launch_failed')
                    ))

            self.root.after(0, self.install_success)
        except Exception as e:
            self.root.after(0, self.install_error, str(e))

    def create_shortcuts(self, target_exe):
        program_name = EMBEDDED_DATA['program_name']
        start_menu = os.path.join(os.environ.get('PROGRAMDATA', 'C:'), 'Microsoft', 'Windows', 'Start Menu', 'Programs', program_name)
        desktop = os.path.join(os.environ.get('PUBLIC', os.environ.get('USERPROFILE')), 'Desktop')
        if not os.path.exists(desktop):
            desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
        os.makedirs(start_menu, exist_ok=True)

        def create_lnk(folder, name, target):
            folder_esc = folder.replace('\\\\', '\\\\\\\\')
            target_esc = target.replace('\\\\', '\\\\\\\\')
            vbs = 'Set oWS = WScript.CreateObject("WScript.Shell")\\n' + \\
                  'Set oLink = oWS.CreateShortcut("' + folder_esc + '\\\\' + name + '.lnk")\\n' + \\
                  'oLink.TargetPath = "' + target_esc + '"\\n' + \\
                  'oLink.Save'
            with tempfile.NamedTemporaryFile(mode='w', suffix='.vbs', delete=False, encoding='utf-8') as f:
                f.write(vbs)
                vbs_file = f.name
            subprocess.run(['cscript', '//Nologo', vbs_file], check=False, capture_output=True)
            os.unlink(vbs_file)

        create_lnk(start_menu, program_name, target_exe)
        create_lnk(desktop, program_name, target_exe)

    def install_success(self):
        self.progress_var.set(100)
        self.progress_label.config(text=_('progress_percent', percent=100))
        self.status_label.config(text=_('status_success'), foreground="#27ae60")
        self.install_btn.config(state=tk.DISABLED)
        # Показываем сообщение об успехе и закрываем окно через 500 мс
        self.root.after(500, self.close_installer)

    def close_installer(self):
        messagebox.showinfo(_('msg_success_title'), _('msg_success_text', program_name=EMBEDDED_DATA['program_name']))
        self.root.destroy()  # окно закрывается

    def install_error(self, err):
        self.status_label.config(text=_('status_error'), foreground="#e17055")
        self.install_btn.config(state=tk.NORMAL)
        messagebox.showerror(_('msg_error_title'), _('msg_error_text', error=err))
        # при ошибке окно не закрывается, чтобы пользователь мог исправить

if __name__ == "__main__":
    root = tk.Tk()
    app = InstallerApp(root)
    root.mainloop()
'''

# ------------------------------------------------------------
# КЛАСС КОНСТРУКТОРА (без изменений)
# ------------------------------------------------------------
class BuilderApp:
    def __init__(self, root):
        self.root = root
        sys_lang = get_system_language()
        self.ui_lang = sys_lang if sys_lang in ['ru', 'uk'] else 'en'
        self.root.title(self.tr('title'))
        self.root.geometry("780x730")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f4f8")

        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.colors = {
            'bg': '#f0f4f8',
            'card': '#ffffff',
            'accent': '#6c5ce7',
            'accent_light': '#a29bfe',
            'accent_dark': '#4a3db8',
            'text': '#2d3436',
            'text_light': '#636e72',
            'success': '#00b894',
            'error': '#e17055',
        }
        self.style.configure('TFrame', background=self.colors['bg'])
        self.style.configure('TLabel', background=self.colors['bg'], font=('Segoe UI', 10), foreground=self.colors['text'])
        self.style.configure('TButton', font=('Segoe UI', 10), padding=8, relief='flat')
        self.style.configure('Header.TLabel', font=('Segoe UI', 24, 'bold'), foreground=self.colors['accent'])
        self.style.configure('Subtitle.TLabel', font=('Segoe UI', 11), foreground=self.colors['text_light'])
        self.style.configure('Card.TFrame', background=self.colors['card'], relief='flat', borderwidth=2)
        self.style.configure('Accent.TButton', font=('Segoe UI', 11, 'bold'), foreground='white', background=self.colors['accent'])
        self.style.map('Accent.TButton',
                       background=[('active', self.colors['accent_dark']), ('disabled', '#bdc3c7')],
                       foreground=[('disabled', '#7f8c8d')])

        self.install_type = tk.StringVar(value="exe")
        self.file_path = tk.StringVar()
        self.logo_path = tk.StringVar()
        self.icon_path = tk.StringVar()
        self.program_name = tk.StringVar(value="Моя программа")
        self.default_path = tk.StringVar(value=self.generate_default_path("Моя программа"))
        self.installer_lang = tk.StringVar(value="auto")
        self.create_shortcuts = tk.BooleanVar(value=True)

        self.program_name.trace('w', self.on_name_changed)

        main_container = tk.Frame(root, bg=self.colors['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        header = tk.Frame(main_container, bg=self.colors['bg'])
        header.pack(fill=tk.X, pady=(0, 15))
        ttk.Label(header, text=self.tr('title'), style='Header.TLabel').pack()
        ttk.Label(header, text=self.tr('subtitle'), style='Subtitle.TLabel').pack()

        card = ttk.Frame(main_container, style='Card.TFrame')
        card.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        inner = tk.Frame(card, bg=self.colors['card'])
        inner.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)

        row = 0
        ttk.Label(inner, text=self.tr('type_label'), font=('Segoe UI', 10, 'bold'), background=self.colors['card']).grid(row=row, column=0, sticky='w', pady=(0,5))
        row += 1
        type_frame = ttk.Frame(inner)
        type_frame.grid(row=row, column=0, columnspan=2, sticky='ew', pady=(0,15))
        ttk.Radiobutton(type_frame, text=self.tr('type_exe'), variable=self.install_type, value="exe").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_frame, text=self.tr('type_zip'), variable=self.install_type, value="zip").pack(side=tk.LEFT, padx=5)

        row += 1
        ttk.Label(inner, text=self.tr('file_label'), font=('Segoe UI', 10, 'bold'), background=self.colors['card']).grid(row=row, column=0, sticky='w', pady=(0,5))
        row += 1
        file_frame = ttk.Frame(inner)
        file_frame.grid(row=row, column=0, columnspan=2, sticky='ew', pady=(0,15))
        ttk.Entry(file_frame, textvariable=self.file_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        ttk.Button(file_frame, text=self.tr('browse'), command=self.browse_file).pack(side=tk.RIGHT)

        row += 1
        ttk.Label(inner, text=self.tr('logo_label'), font=('Segoe UI', 10, 'bold'), background=self.colors['card']).grid(row=row, column=0, sticky='w', pady=(0,5))
        row += 1
        logo_frame = ttk.Frame(inner)
        logo_frame.grid(row=row, column=0, columnspan=2, sticky='ew', pady=(0,15))
        ttk.Entry(logo_frame, textvariable=self.logo_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        ttk.Button(logo_frame, text=self.tr('browse'), command=self.browse_logo).pack(side=tk.RIGHT)

        row += 1
        ttk.Label(inner, text=self.tr('icon_label'), font=('Segoe UI', 10, 'bold'), background=self.colors['card']).grid(row=row, column=0, sticky='w', pady=(0,5))
        row += 1
        icon_frame = ttk.Frame(inner)
        icon_frame.grid(row=row, column=0, columnspan=2, sticky='ew', pady=(0,15))
        ttk.Entry(icon_frame, textvariable=self.icon_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        ttk.Button(icon_frame, text=self.tr('browse'), command=self.browse_icon).pack(side=tk.RIGHT)

        row += 1
        ttk.Label(inner, text=self.tr('name_label'), font=('Segoe UI', 10, 'bold'), background=self.colors['card']).grid(row=row, column=0, sticky='w', pady=(0,5))
        row += 1
        name_entry = ttk.Entry(inner, textvariable=self.program_name, width=50)
        name_entry.grid(row=row, column=0, columnspan=2, sticky='ew', pady=(0,5))

        row += 1
        path_hint = ttk.Label(inner, text=self.tr('path_auto'), font=('Segoe UI', 9), foreground='#636e72', background=self.colors['card'])
        path_hint.grid(row=row, column=0, columnspan=2, sticky='w', pady=(0,5))

        row += 1
        ttk.Label(inner, text=self.tr('path_label'), font=('Segoe UI', 10, 'bold'), background=self.colors['card']).grid(row=row, column=0, sticky='w', pady=(0,5))
        row += 1
        def_path_entry = ttk.Entry(inner, textvariable=self.default_path, width=50)
        def_path_entry.grid(row=row, column=0, columnspan=2, sticky='ew', pady=(0,15))

        row += 1
        shortcuts_check = ttk.Checkbutton(inner, text=self.tr('shortcuts_label'), variable=self.create_shortcuts)
        shortcuts_check.grid(row=row, column=0, sticky='w', pady=(0,10))

        lang_label = ttk.Label(inner, text=self.tr('lang_label') + ':', font=('Segoe UI', 10), background=self.colors['card'])
        lang_label.grid(row=row, column=1, sticky='e', pady=(0,10))
        lang_combo = ttk.Combobox(inner, textvariable=self.installer_lang,
                                  values=['auto', 'ru', 'en', 'uk'], state='readonly', width=12)
        lang_combo.grid(row=row, column=1, sticky='e', padx=(5,0), pady=(0,10))
        lang_combo.set('auto')

        row += 1
        self.build_btn = ttk.Button(inner, text=self.tr('build_btn'), command=self.build_installer, style='Accent.TButton')
        self.build_btn.grid(row=row, column=0, columnspan=2, pady=20)

        row += 1
        ttk.Label(inner, text=self.tr('log_label'), font=('Segoe UI', 10, 'bold'), background=self.colors['card']).grid(row=row, column=0, sticky='w', pady=(0,5))
        row += 1
        self.log_text = tk.Text(inner, height=8, state=tk.DISABLED, bg='#fafafa', fg=self.colors['text'],
                                font=('Consolas', 9), relief='flat', borderwidth=1, highlightthickness=1, highlightcolor='#dfe6e9')
        self.log_text.grid(row=row, column=0, columnspan=2, sticky='ew', pady=(0,10))

        self.status_label = ttk.Label(inner, text=self.tr('status_ready'), foreground="#7f8c8d", background=self.colors['card'])
        self.status_label.grid(row=row+1, column=0, columnspan=2, sticky='w')

        inner.columnconfigure(0, weight=1)
        inner.columnconfigure(1, weight=1)

    def tr(self, key, **kwargs):
        text = TR.get(self.ui_lang, TR['en']).get(key, key)
        if kwargs:
            text = text.format(**kwargs)
        return text

    def generate_default_path(self, name):
        translit_name = translit(name)
        if not translit_name:
            translit_name = "MyApp"
        return f"C:\\Program Files\\{translit_name}"

    def on_name_changed(self, *args):
        name = self.program_name.get().strip()
        if name:
            self.default_path.set(self.generate_default_path(name))

    def update_builder_icon(self, logo_path):
        if not logo_path or not os.path.exists(logo_path) or not HAS_PIL:
            return
        try:
            img = Image.open(logo_path)
            with tempfile.NamedTemporaryFile(suffix='.ico', delete=False) as f:
                ico_path = f.name
            img.save(ico_path, format='ICO', sizes=[(256,256), (128,128), (64,64), (32,32), (16,16)])
            self.root.iconbitmap(ico_path)
            self.root.after(2000, lambda: os.unlink(ico_path))
        except:
            pass

    def browse_logo(self):
        fname = filedialog.askopenfilename(title=self.tr('logo_label'), filetypes=[("PNG images", "*.png")])
        if fname:
            self.logo_path.set(fname)
            self.update_builder_icon(fname)

    def browse_file(self):
        ext = "*.exe" if self.install_type.get() == "exe" else "*.zip"
        fname = filedialog.askopenfilename(title=self.tr('file_label'), filetypes=[(ext.upper(), ext), ("All files", "*.*")])
        if fname:
            self.file_path.set(fname)

    def browse_icon(self):
        fname = filedialog.askopenfilename(title=self.tr('icon_label'), filetypes=[("ICO files", "*.ico")])
        if fname:
            self.icon_path.set(fname)

    def log(self, msg):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)
        self.root.update()

    def set_status(self, text_key, color="#7f8c8d"):
        self.status_label.config(text=self.tr(text_key), foreground=color)
        self.root.update()

    def build_installer(self):
        if not self.file_path.get() or not os.path.exists(self.file_path.get()):
            messagebox.showerror(self.tr('error_build'), self.tr('error_no_file'))
            return
        if not self.program_name.get().strip():
            messagebox.showerror(self.tr('error_build'), self.tr('error_no_name'))
            return

        lang_code = self.installer_lang.get()
        if lang_code == 'auto':
            lang_code = get_system_language()
            if lang_code not in ['ru', 'uk']:
                lang_code = 'en'

        save_filename = filedialog.asksaveasfilename(
            title=self.tr('build_btn'),
            defaultextension=".exe",
            filetypes=[("Executable", "*.exe"), ("All files", "*.*")],
            initialfile="Setup.exe"
        )
        if not save_filename:
            return
        save_path = Path(save_filename)
        if save_path.suffix.lower() != '.exe':
            save_path = save_path.with_suffix('.exe')

        try:
            subprocess.run([sys.executable, "-m", "PyInstaller", "--version"], capture_output=True, check=True)
        except:
            self.log(self.tr('log_pyinstaller_not_found'))
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
                self.log(self.tr('log_pyinstaller_installed'))
            except Exception as e:
                messagebox.showerror(self.tr('error_build'), f"{self.tr('error_pyinstaller')}\n{e}")
                return

        self.log("")
        self.log("="*50)
        self.log(self.tr('log_preparing'))
        self.set_status('status_generating', "#2980b9")

        try:
            self.log(self.tr('step_reading'))
            with open(self.file_path.get(), "rb") as f:
                file_data = base64.b64encode(f.read()).decode('ascii')
            filename = os.path.basename(self.file_path.get())
            self.log(f"  Файл: {filename} ({len(file_data)} символов base64)")

            self.log(self.tr('step_logo'))
            logo_data = ""
            if self.logo_path.get() and os.path.exists(self.logo_path.get()):
                with open(self.logo_path.get(), "rb") as f:
                    logo_data = base64.b64encode(f.read()).decode('ascii')
                self.log(f"  Логотип загружен: {os.path.basename(self.logo_path.get())}")
            else:
                logo_data = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
                self.log("  Логотип не указан, используется заглушка.")

            self.log(self.tr('step_icon'))
            icon_data = ""
            if self.icon_path.get() and os.path.exists(self.icon_path.get()):
                with open(self.icon_path.get(), "rb") as f:
                    icon_data = base64.b64encode(f.read()).decode('ascii')
                self.log(f"  Иконка загружена: {os.path.basename(self.icon_path.get())}")
            elif self.logo_path.get() and HAS_PIL:
                try:
                    img = Image.open(self.logo_path.get())
                    with tempfile.NamedTemporaryFile(suffix='.ico', delete=False) as f:
                        ico_temp = f.name
                    img.save(ico_temp, format='ICO', sizes=[(256,256), (128,128), (64,64), (32,32), (16,16)])
                    with open(ico_temp, 'rb') as f:
                        icon_data = base64.b64encode(f.read()).decode('ascii')
                    os.unlink(ico_temp)
                    self.log(self.tr('log_icon_from_logo'))
                except Exception as e:
                    self.log(f"{self.tr('log_icon_from_png_fail')} {e}")
            else:
                self.log("  Иконка не указана, будет использована стандартная.")

            self.log(self.tr('step_embedded'))
            embedded = {
                "program_name": self.program_name.get(),
                "install_type": self.install_type.get(),
                "default_path": self.default_path.get(),
                "file_data": file_data,
                "filename": filename,
                "logo_data": logo_data,
                "icon_data": icon_data
            }
            embedded_json = json.dumps(embedded, ensure_ascii=False)
            self.log(f"  Данные подготовлены для встраивания (размер: {len(embedded_json)} символов)")

            self.log(self.tr('step_script'))
            script_content = INSTALLER_TEMPLATE.format(
                embedded_data=embedded_json,
                lang_code=lang_code,
                create_shortcuts=self.create_shortcuts.get()
            )
            script_path = Path("installer_script.py")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script_content)
            self.log(f"{self.tr('log_script_created')} {script_path.absolute()}")
            self.set_status('status_checking', "#f39c12")

            self.log(self.tr('step_syntax'))
            result = subprocess.run([sys.executable, "-m", "py_compile", str(script_path)],
                                    capture_output=True, text=True)
            if result.returncode != 0:
                self.log(self.tr('syntax_error'))
                self.log(result.stderr)
                messagebox.showerror(self.tr('error_build'), f"{self.tr('syntax_error')}\n{result.stderr}")
                return
            self.log(self.tr('syntax_ok'))

            icon_arg = []
            if self.icon_path.get() and os.path.exists(self.icon_path.get()):
                icon_arg = ["--icon", self.icon_path.get()]
                self.log(f"  Иконка для EXE: {self.icon_path.get()}")
            elif self.logo_path.get() and HAS_PIL:
                try:
                    img = Image.open(self.logo_path.get())
                    ico_path = Path("temp_icon.ico")
                    img.save(ico_path, format='ICO', sizes=[(256,256), (128,128), (64,64), (32,32), (16,16)])
                    icon_arg = ["--icon", str(ico_path)]
                    self.log(self.tr('log_icon_for_exe'))
                except Exception as e:
                    self.log(f"{self.tr('log_icon_for_exe_fail')} {e}")
            else:
                self.log(self.tr('log_icon_not_specified'))

            self.log(self.tr('step_pyinstaller'))
            self.set_status('status_building', "#e67e22")
            dist_dir = save_path.parent
            name = save_path.stem
            self.log(f"{self.tr('log_building')} {save_path}...")
            cmd = [
                sys.executable, "-m", "PyInstaller",
                "--onefile",
                "--windowed",
                "--noconfirm",
                "--log-level=DEBUG",
                "--name", name,
                "--distpath", str(dist_dir),
                "--workpath", str(Path("build_temp") / "work"),
                "--specpath", str(Path("build_temp")),
                *icon_arg,
                str(script_path)
            ]
            self.log(f"{self.tr('log_cmd')} {' '.join(cmd)}")

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            for line in process.stdout:
                self.log(line.rstrip())
            process.wait()

            if process.returncode != 0:
                raise Exception(f"PyInstaller завершился с кодом {process.returncode}. Проверьте лог выше.")

            self.log(self.tr('step_finish'))
            if save_path.exists():
                self.log(f"{self.tr('log_success')} {save_path}")
                self.set_status('status_done', "green")
                messagebox.showinfo(self.tr('msg_success'), f"{self.tr('msg_success')}\n{save_path}")
            else:
                possible = dist_dir / f"{name}.exe"
                if possible.exists():
                    shutil.move(str(possible), str(save_path))
                    self.log(f"{self.tr('log_renamed')} {save_path}")
                    self.set_status('status_done', "green")
                    messagebox.showinfo(self.tr('msg_success'), f"{self.tr('msg_success')}\n{save_path}")
                else:
                    raise Exception("Не найден выходной файл после сборки.")

        except Exception as e:
            self.log(f"{self.tr('log_error')} {e}")
            self.set_status('status_error', "red")
            messagebox.showerror(self.tr('error_build'), f"{self.tr('error_build')}\n{e}")

        finally:
            for f in Path().glob("temp_icon.ico"):
                f.unlink(missing_ok=True)
            shutil.rmtree("build_temp", ignore_errors=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = BuilderApp(root)
    root.mainloop()