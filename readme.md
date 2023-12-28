# Ogg to WAV Converter

This project provides a simple Ogg to WAV conversion tool with both a command-line interface and a graphical user interface (GUI). The conversion process utilizes the FFmpeg library.

## File Descriptions

### 1. Main Converter Script

#### `project/main.py`

This Python script (`main.py`) serves as the core converter module. It contains a function `convert_ogg_to_wav` that converts an Ogg file to WAV format using the FFmpeg tool. The script also includes a sample usage demonstrating the conversion of a specific Ogg file.

### 2. GUI Application

#### `project/gui/app.py`

This script (`app.py`) defines a PyQt5-based GUI application for the Ogg to WAV converter. Users can select an Ogg file through the GUI, configure conversion settings, and initiate the conversion process. The application displays conversion logs and includes links to the project's GitHub repository.

### 3. Configuration File

#### `project/gui/config.ini`

This configuration file (`config.ini`) is used by the GUI application to store user-defined settings. The file includes paths for the output folder and the FFmpeg executable.

## Usage

### Main Script Usage

Execute `main.py` to convert a specific Ogg file to WAV format. Modify the script to suit your needs, specifying the input (`ogg_file_path`) and output (`wav_file_path`) file paths.

```bash
python main.py
```

### GUI Application Usage

Run the GUI application (`app.py`) to access a user-friendly interface for Ogg to WAV conversion. Follow these steps:

1. Launch the application using the following command:

    ```bash
    python app.py
    ```

2. Click the "Browse" button to select an Ogg file.

3. Click the "Convert" button to initiate the conversion process.

4. View the conversion progress and logs in the text area.

## Configuration

The GUI application uses the `config.ini` file to store configuration settings. Modify the paths in the `[Paths]` section to specify the output folder (`output_folder`) and the path to the FFmpeg executable (`ffmpeg_path`).

## Dependencies

- Python 3.x
- PyQt5
- FFmpeg

## Acknowledgments

This project is created by King Triton. Visit the [GitHub repository](https://github.com/king-tri-ton/ogg-to-wav) for more information and updates.

© 2023 King Triton. All rights reserved.