import subprocess

def convert_ogg_to_wav(ogg_file, wav_file):
    ffmpeg_path = r"C:\python\ffmpeg-master-latest-win64-gpl\bin\ffmpeg.exe"
    command = [ffmpeg_path, "-i", ogg_file, wav_file]
    subprocess.run(command, shell=True)

if __name__ == "__main__":
    ogg_file_path = r"C:\python\oggtomp3\audio_2023-12-28_13-36-56.ogg"
    wav_file_path = r"C:\python\oggtomp3\audio_2023-12-28_13-36-56.wav"
    
    convert_ogg_to_wav(ogg_file_path, wav_file_path)
    print(f"Conversion to WAV completed: {wav_file_path}")
