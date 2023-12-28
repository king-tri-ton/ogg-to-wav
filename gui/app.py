import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QFileDialog, QVBoxLayout, QTextEdit
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QProcess, QSettings, Qt
import os

class OggToWavConverter(QWidget):
    def __init__(self):
        super().__init__()

        self.settings = QSettings('config.ini', QSettings.IniFormat)
        self.init_ui()
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(self.handle_stdout)
        self.process.readyReadStandardError.connect(self.handle_stderr)
        self.process.finished.connect(self.handle_finished)

    def init_ui(self):
        self.setGeometry(300, 300, 530, 400)
        self.setFixedSize(530, 350)
        self.setWindowTitle('Ogg to WAV Converter')

        self.ogg_label = QLabel('Select the .ogg file:', self)
        self.ogg_label.setGeometry(20, 20, 150, 20)

        self.ogg_file_path = QLabel('', self)
        self.ogg_file_path.setGeometry(170, 20, 250, 20)

        self.ogg_button = QPushButton('Browse', self)
        self.ogg_button.setGeometry(425, 20, 80, 25)
        self.ogg_button.clicked.connect(self.choose_ogg_file)

        self.convert_button = QPushButton('Convert', self)
        self.convert_button.setGeometry(200, 60, 120, 30)
        self.convert_button.clicked.connect(self.convert)

        self.log_text = QTextEdit(self)
        self.log_text.setGeometry(25, 120, 480, 150)
        self.log_text.setReadOnly(True)

        self.info_layout = QVBoxLayout()

        self.info_label = QLabel('© 2023 King Triton. All Right Reserved.', self)
        self.info_label.setAlignment(Qt.AlignCenter)
        self.info_layout.addWidget(self.info_label)

        self.github_link_label = QLabel('<a href="https://github.com/king-tri-ton/ogg-to-wav">GitHub</a>', self)
        self.github_link_label.setAlignment(Qt.AlignCenter)
        self.github_link_label.setOpenExternalLinks(True)
        self.info_layout.addWidget(self.github_link_label)

        self.info_widget = QWidget(self)
        self.info_widget.setGeometry(20, 280, 480, 60)
        self.info_widget.setLayout(self.info_layout)

    def choose_ogg_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        ogg_file, _ = QFileDialog.getOpenFileName(self, "Select the .ogg file", "", "Ogg files (*.ogg);;All Files (*)", options=options)
        if ogg_file:
            self.ogg_file_path.setText(ogg_file)

    def convert(self):
        ogg_file = self.ogg_file_path.text()

        if ogg_file:
            ogg_base_name = os.path.basename(ogg_file)
            output_folder = self.settings.value('Paths/output_folder', '')
            wav_file = os.path.join(output_folder, os.path.splitext(ogg_base_name)[0] + ".wav")

            ffmpeg_path = self.settings.value('Paths/ffmpeg_path', '')
            if not os.path.exists(ffmpeg_path):
                self.log_text.append("Error: Specify the correct path to ffmpeg in the configuration file.")
                return

            self.log_text.clear()
            self.log_text.append(f"Convert to WAV: {ogg_file} -> {wav_file}")
            self.convert_ogg_to_wav(ogg_file, wav_file, ffmpeg_path)

    def convert_ogg_to_wav(self, ogg_file, wav_file, ffmpeg_path):
        self.log_text.append(f"ffmpeg_path: {ffmpeg_path}")
        command = [ffmpeg_path, "-i", ogg_file, wav_file]
        self.process.start(command[0], command[1:])
        
    def handle_stdout(self):
        data = self.process.readAllStandardOutput().data().decode('utf-8')
        self.log_text.append(data)

    def handle_stderr(self):
        data = self.process.readAllStandardError().data().decode('utf-8')
        self.log_text.append(data)

    def handle_finished(self):
        self.log_text.append("Conversion complete.")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = OggToWavConverter()
    ex.show()
    sys.exit(app.exec_())
