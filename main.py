"""
A code of speech recognition with whisper
author: matsumoto

satisfy python requirement
----------------------
pip install git+https://github.com/openai/whisper.git
----------------------

out of python requirement
----------------------
gsudo choco ffmpeg
----------------------
"""

import tkinter as tk
from tkinter import filedialog
import whisper
import os
import glob

def get_audio_paths():
    # フォルダパスを取り出す
    folder_path = filedialog.askdirectory(initialdir="C:/Share", title="フォルダ選択")

    # 音声ファイルの拡張子のリストを作成
    audio_exts = [".wav", ".aiff",  ".mp3", ".aac",".flac", ".ogg",".m4a",".wma"]

    # ファイルパスのリストを作成
    file_paths = []

    # 音声ファイルの拡張子ごとにパターンを作成（**はサブフォルダも含める）
    for audio_ext in audio_exts:
        pattern = folder_path + "/**/*" + audio_ext

        # パターンに一致するパスをリストに格納（recursive=Trueで再帰的に探索）
        paths = glob.glob(pattern, recursive=True)

        # パスがファイルかどうか判定
        for path in paths:
            # パスがファイルなら
            if os.path.isfile(path):
                # パスを絶対パスに変換
                file_path = os.path.abspath(path)
                # 同名のテキストファイルが存在するかどうか判定
                txt_path = os.path.splitext(file_path)[0] + ".txt"
                # テキストファイルが存在しなければ
                if not os.path.exists(txt_path):
                    # ファイルパスをリストに追加
                    file_paths.append(file_path)
    return file_paths

def save_result(file_path,result):
    file_path=os.path.normpath(file_path)
    # 出力を保存するディレクトリを指定
    output_dir = os.path.dirname(file_path) # os.path.dirnameで親ディレクトリを取得
    output_name = os.path.basename(file_path)
    index = output_name.rfind(".")

    #"."が見つかった場合
    if index != -1: # "."から右を"txt"に置き換える 
        output_name = output_name[:index] + ".txt"
    print("name:"+output_name)
    # 出力ファイルのパスを作成
    output_path = os.path.join(output_dir, output_name)
    print(output_path)
    # 出力ファイルに書き込み
    with open(output_path, "w", encoding="utf-8") as f:
        for segment in result["segments"]:
            start = segment["start"]
            end = segment["end"]
            f.write(f"[{start} --> {end}] "+segment["text"]+"\n")

def main():
    root = tk.Tk()
    root.withdraw()
    # file_path = filedialog.askopenfilename()
    file_paths=get_audio_paths()
    print(file_paths)
    

    model = whisper.load_model("large")
    for file_path in file_paths:
        result = model.transcribe(file_path, verbose=True, language="ja")
        save_result(file_path,result)

if __name__ == '__main__':
    main()
