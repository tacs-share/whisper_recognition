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
    folder_path = filedialog.askdirectory( title="フォルダ選択")

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
    # 出力ファイルのパスを作成
    output_path = os.path.join(output_dir, output_name)
    print("output: "+output_path)
    # 出力ファイルに書き込み
    with open(output_path, "w", encoding="utf-8") as f:
        # 音声区間ごとに処理
        for segment in result["segments"]:
            # 音声区間の開始時間(秒)を取得
            seconds = int(segment["start"])
            # 時間・分・秒に変換する
            hours = seconds // 3600 # 1時間は3600秒
            minutes = (seconds % 3600) // 60 # 残りの秒数を60で割る
            seconds = (seconds % 3600) % 60 # 残りの秒数を60で割った余り
            # 書き込み
            f.write(f"[{hours:02}:{minutes:02}:{seconds:02}] "+segment["text"]+"\n")

def main():
    root = tk.Tk()
    root.withdraw()
    # ファイル名一覧をフォルダから取得
    file_paths=get_audio_paths()
    print(file_paths)
    
    # モデルのロード (無ければwebからダウンロード)
    model = whisper.load_model("large-v2")
    # 音声ファイルを文字起こし
    for file_path in file_paths:
        # 音声認識結果(辞書)を取得
        result = model.transcribe(file_path, verbose=True, language="ja")
        # 認識結果をパースして音声ファイルと同名の.txtに保存
        save_result(file_path,result)

if __name__ == '__main__':
    main()
