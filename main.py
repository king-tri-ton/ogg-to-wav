import os
import sys
import subprocess
import requests
import zipfile

def get_ffmpeg_path():
    """Возвращает путь к ffmpeg.exe, скачивает его, если отсутствует."""
    ffmpeg_dir = os.path.join(os.getcwd(), "ffmpeg")
    ffmpeg_exe = os.path.join(ffmpeg_dir, "bin", "ffmpeg.exe")
    
    if not os.path.isfile(ffmpeg_exe):
        print("FFmpeg не найден, скачиваем...")
        url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        zip_path = os.path.join(os.getcwd(), "ffmpeg.zip")
        
        response = requests.get(url, stream=True)
        with open(zip_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=1024):
                file.write(chunk)
        
        print("Распаковываем FFmpeg...")
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(os.getcwd())
        
        extracted_folder = [f for f in os.listdir(os.getcwd()) if f.startswith("ffmpeg")][0]
        os.rename(extracted_folder, ffmpeg_dir)
        os.remove(zip_path)
        
    return ffmpeg_exe

def convert_ogg_to_wav(ogg_file, wav_file):
    """Конвертирует OGG в WAV с помощью FFmpeg."""
    ffmpeg_path = get_ffmpeg_path()
    command = [ffmpeg_path, "-i", ogg_file, wav_file]
    subprocess.run(command, shell=True)
    print(f"Конвертация завершена: {wav_file}")

def main():
    """Основная функция обработки аргументов командной строки."""
    if len(sys.argv) < 2:
        print("Использование: oggtowav путь_к_ogg [путь_для_сохранения]")
        sys.exit(1)
    
    ogg_file = sys.argv[1]
    
    if not os.path.isfile(ogg_file):
        print("Ошибка: Файл не найден.")
        sys.exit(1)
    
    default_output_dir = os.path.join(os.getcwd(), "converted")
    os.makedirs(default_output_dir, exist_ok=True)
    
    if len(sys.argv) > 2:
        output_path = sys.argv[2]
        if os.path.isdir(output_path):
            wav_file = os.path.join(output_path, os.path.basename(ogg_file).replace(".ogg", ".wav"))
        else:
            wav_file = output_path if output_path.endswith(".wav") else output_path + ".wav"
    else:
        wav_file = os.path.join(default_output_dir, os.path.basename(ogg_file).replace(".ogg", ".wav"))
    
    convert_ogg_to_wav(ogg_file, wav_file)
    
if __name__ == "__main__":
    main()