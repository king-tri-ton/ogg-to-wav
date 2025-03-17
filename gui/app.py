import sys
import os
import subprocess
import requests
import zipfile
import shutil
from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton, QLabel, QFileDialog, 
                            QVBoxLayout, QTextEdit, QTabWidget, QLineEdit, QHBoxLayout,
                            QMessageBox, QProgressBar, QGroupBox)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QProcess, QSettings, Qt, QThread, pyqtSignal

class DownloadFFmpegThread(QThread):
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    
    def __init__(self, download_path):
        super().__init__()
        self.download_path = download_path
        
    def run(self):
        try:
            # URL для скачивания ffmpeg для Windows
            url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
            
            # Создаем временную директорию
            temp_dir = os.path.join(os.path.dirname(self.download_path), "temp_ffmpeg")
            os.makedirs(temp_dir, exist_ok=True)
            
            # Скачиваем файл
            zip_path = os.path.join(temp_dir, "ffmpeg.zip")
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            
            bytes_downloaded = 0
            with open(zip_path, 'wb') as f:
                for data in response.iter_content(chunk_size=4096):
                    bytes_downloaded += len(data)
                    f.write(data)
                    progress = int(bytes_downloaded / total_size * 100)
                    self.progress_signal.emit(progress)
            
            # Распаковываем архив
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)
            
            # Находим ffmpeg.exe в распакованных файлах
            ffmpeg_exe = None
            for root, dirs, files in os.walk(temp_dir):
                if "ffmpeg.exe" in files:
                    ffmpeg_exe = os.path.join(root, "ffmpeg.exe")
                    break
            
            if ffmpeg_exe:
                # Копируем ffmpeg.exe в указанный путь
                os.makedirs(os.path.dirname(self.download_path), exist_ok=True)
                shutil.copy2(ffmpeg_exe, self.download_path)
                self.finished_signal.emit(self.download_path)
            else:
                self.error_signal.emit("ffmpeg.exe не найден в распакованных файлах")
            
            # Удаляем временную директорию
            shutil.rmtree(temp_dir)
            
        except Exception as e:
            self.error_signal.emit(f"Ошибка при скачивании: {str(e)}")


class OggToWavConverter(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QSettings('config.ini', QSettings.IniFormat)
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        self.setGeometry(300, 300, 600, 400)
        self.setFixedSize(600, 400)
        self.setWindowTitle('OGG to WAV Converter')
        
        # Основной макет
        main_layout = QVBoxLayout()
        
        # Создаем вкладки
        self.tabs = QTabWidget()
        
        # Вкладка конвертации
        self.conversion_tab = QWidget()
        self.init_conversion_tab()
        self.tabs.addTab(self.conversion_tab, "Конвертация")
        
        # Вкладка настроек
        self.settings_tab = QWidget()
        self.init_settings_tab()
        self.tabs.addTab(self.settings_tab, "Настройки")
        
        main_layout.addWidget(self.tabs)
        
        # Информация о программе
        self.info_layout = QVBoxLayout()
        self.info_label = QLabel('© 2025 King Triton. All Right Reserved.', self)
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_layout.addWidget(self.info_label)
        self.github_link_label = QLabel('<a href="https://github.com/king-tri-ton/ogg-to-wav">GitHub</a>', self)
        self.github_link_label.setAlignment(Qt.AlignCenter)
        self.github_link_label.setOpenExternalLinks(True)
        self.info_layout.addWidget(self.github_link_label)
        
        main_layout.addLayout(self.info_layout)
        
        self.setLayout(main_layout)
    
    def init_conversion_tab(self):
        layout = QVBoxLayout()
        
        # Выбор OGG файла
        file_group = QGroupBox("Выбор файла")
        file_layout = QHBoxLayout()
        
        self.ogg_label = QLabel('Выберите .ogg файл:')
        self.ogg_file_path = QLineEdit()
        self.ogg_file_path.setReadOnly(True)
        self.ogg_button = QPushButton('Обзор')
        self.ogg_button.clicked.connect(self.choose_ogg_file)
        
        file_layout.addWidget(self.ogg_label)
        file_layout.addWidget(self.ogg_file_path)
        file_layout.addWidget(self.ogg_button)
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Кнопка конвертации
        convert_layout = QHBoxLayout()
        self.convert_button = QPushButton('Конвертировать')
        self.convert_button.clicked.connect(self.convert)
        self.convert_button.setMinimumHeight(40)
        convert_layout.addStretch()
        convert_layout.addWidget(self.convert_button)
        convert_layout.addStretch()
        layout.addLayout(convert_layout)
        
        # Лог конвертации
        log_group = QGroupBox("Лог")
        log_layout = QVBoxLayout()
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        self.conversion_tab.setLayout(layout)
    
    def init_settings_tab(self):
        layout = QVBoxLayout()
        
        # Путь к папке с результатами
        output_group = QGroupBox("Папка с результатами")
        output_layout = QHBoxLayout()
        
        self.output_folder_label = QLabel('Путь к папке:')
        self.output_folder_path = QLineEdit()
        self.output_folder_button = QPushButton('Обзор')
        self.output_folder_button.clicked.connect(self.choose_output_folder)
        
        output_layout.addWidget(self.output_folder_label)
        output_layout.addWidget(self.output_folder_path)
        output_layout.addWidget(self.output_folder_button)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)
        
        # Путь к ffmpeg
        ffmpeg_group = QGroupBox("FFmpeg")
        ffmpeg_layout = QVBoxLayout()
        
        path_layout = QHBoxLayout()
        self.ffmpeg_label = QLabel('Путь к FFmpeg:')
        self.ffmpeg_path = QLineEdit()
        self.ffmpeg_button = QPushButton('Обзор')
        self.ffmpeg_button.clicked.connect(self.choose_ffmpeg)
        
        path_layout.addWidget(self.ffmpeg_label)
        path_layout.addWidget(self.ffmpeg_path)
        path_layout.addWidget(self.ffmpeg_button)
        ffmpeg_layout.addLayout(path_layout)
        
        download_layout = QVBoxLayout()
        self.download_ffmpeg_button = QPushButton('Скачать и установить FFmpeg')
        self.download_ffmpeg_button.clicked.connect(self.download_ffmpeg)
        self.download_progress = QProgressBar()
        self.download_progress.setVisible(False)
        
        download_layout.addWidget(self.download_ffmpeg_button)
        download_layout.addWidget(self.download_progress)
        ffmpeg_layout.addLayout(download_layout)
        
        ffmpeg_group.setLayout(ffmpeg_layout)
        layout.addWidget(ffmpeg_group)
        
        # Кнопка сохранения настроек
        save_layout = QHBoxLayout()
        self.save_button = QPushButton('Сохранить настройки')
        self.save_button.clicked.connect(self.save_settings)
        self.save_button.setMinimumHeight(40)
        save_layout.addStretch()
        save_layout.addWidget(self.save_button)
        save_layout.addStretch()
        layout.addLayout(save_layout)
        
        layout.addStretch()
        
        self.settings_tab.setLayout(layout)
    
    def load_settings(self):
        self.output_folder_path.setText(self.settings.value('Paths/output_folder', ''))
        self.ffmpeg_path.setText(self.settings.value('Paths/ffmpeg_path', ''))
    
    def save_settings(self):
        self.settings.setValue('Paths/output_folder', self.output_folder_path.text())
        self.settings.setValue('Paths/ffmpeg_path', self.ffmpeg_path.text())
        self.settings.sync()
        QMessageBox.information(self, "Сохранено", "Настройки успешно сохранены.")
    
    def choose_ogg_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        ogg_file, _ = QFileDialog.getOpenFileName(self, "Выберите .ogg файл", "", "Ogg файлы (*.ogg);;Все файлы (*)", options=options)
        if ogg_file:
            self.ogg_file_path.setText(ogg_file)
    
    def choose_output_folder(self):
        options = QFileDialog.Options()
        output_folder = QFileDialog.getExistingDirectory(self, "Выберите папку для результатов", "", options=options)
        if output_folder:
            self.output_folder_path.setText(output_folder)
    
    def choose_ffmpeg(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        ffmpeg_path, _ = QFileDialog.getOpenFileName(self, "Выберите ffmpeg.exe", "", "Исполняемые файлы (*.exe);;Все файлы (*)", options=options)
        if ffmpeg_path:
            self.ffmpeg_path.setText(ffmpeg_path)
    
    def download_ffmpeg(self):
        # Определяем путь для скачивания
        download_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ffmpeg")
        os.makedirs(download_dir, exist_ok=True)
        download_path = os.path.join(download_dir, "ffmpeg.exe")
        
        # Создаем и запускаем поток для скачивания
        self.download_thread = DownloadFFmpegThread(download_path)
        self.download_thread.progress_signal.connect(self.update_download_progress)
        self.download_thread.finished_signal.connect(self.download_finished)
        self.download_thread.error_signal.connect(self.download_error)
        
        self.download_progress.setVisible(True)
        self.download_progress.setValue(0)
        self.download_ffmpeg_button.setEnabled(False)
        self.download_thread.start()
    
    def update_download_progress(self, value):
        self.download_progress.setValue(value)
    
    def download_finished(self, path):
        self.ffmpeg_path.setText(path)
        self.download_progress.setVisible(False)
        self.download_ffmpeg_button.setEnabled(True)
        QMessageBox.information(self, "Загрузка завершена", f"FFmpeg успешно загружен и установлен по пути:\n{path}")
    
    def download_error(self, error):
        self.download_progress.setVisible(False)
        self.download_ffmpeg_button.setEnabled(True)
        QMessageBox.critical(self, "Ошибка загрузки", error)
    
    def convert(self):
        ogg_file = self.ogg_file_path.text()
        if not ogg_file:
            QMessageBox.warning(self, "Ошибка", "Выберите .ogg файл для конвертации.")
            return
        
        output_folder = self.settings.value('Paths/output_folder', '')
        if not output_folder:
            QMessageBox.warning(self, "Ошибка", "Не указана папка для результатов. Перейдите во вкладку 'Настройки'.")
            self.tabs.setCurrentIndex(1)
            return
        
        ffmpeg_path = self.settings.value('Paths/ffmpeg_path', '')
        if not ffmpeg_path or not os.path.exists(ffmpeg_path):
            QMessageBox.warning(self, "Ошибка", "Не указан корректный путь к ffmpeg. Перейдите во вкладку 'Настройки'.")
            self.tabs.setCurrentIndex(1)
            return
        
        ogg_base_name = os.path.basename(ogg_file)
        wav_file = os.path.join(output_folder, os.path.splitext(ogg_base_name)[0] + ".wav")
        
        self.log_text.clear()
        self.log_text.append(f"Конвертация в WAV: {ogg_file} -> {wav_file}")
        
        self.convert_ogg_to_wav(ogg_file, wav_file, ffmpeg_path)
    
    def convert_ogg_to_wav(self, ogg_file, wav_file, ffmpeg_path):
        self.log_text.append(f"ffmpeg_path: {ffmpeg_path}")
        # Создаем директорию для выходного файла если её нет
        os.makedirs(os.path.dirname(wav_file), exist_ok=True)
        # Запускаем процесс конвертации
        command = [ffmpeg_path, "-i", ogg_file, wav_file]
        self.process.start(command[0], command[1:])

    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode('utf-8')
        self.log_text.append(data)

    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode('utf-8')
        self.log_text.append(data)

    def handle_finished(self):
        exit_code = self.process.exitCode()
        if exit_code == 0:
            self.log_text.append("Конвертация успешно завершена.")
            # Показываем сообщение об успешной конвертации
            QMessageBox.information(self, "Готово", "Конвертация успешно завершена.")
        else:
            self.log_text.append(f"Процесс завершился с кодом ошибки: {exit_code}")
            QMessageBox.critical(self, "Ошибка", f"Процесс конвертации завершился с ошибкой (код {exit_code}).")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = OggToWavConverter()
    ex.show()
    sys.exit(app.exec_())