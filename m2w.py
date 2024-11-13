import tkinter as tk
from tkinter import filedialog
import whisper
import os
import glob



def get_video_paths(folder_path):
    """
    フォルダ内の動画ファイルのパスを取得する関数

    Returns:
        list: 動画ファイルのパスのリスト
    """

    # 動画ファイルの拡張子のリストを作成
    video_exts = [".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv"]

    # ファイルパスのリストを作成
    file_paths = []

    # 動画ファイルの拡張子ごとにパターンを作成（**はサブフォルダも含める）
    for video_ext in video_exts:
        pattern = folder_path + "/**/*" + video_ext

        # パターンに一致するパスをリストに格納（recursive=Trueで再帰的に探索）
        paths = glob.glob(pattern, recursive=True)

        # パスがファイルかどうか判定
        for path in paths:
            # パスがファイルなら
            if os.path.isfile(path):
                # パスを絶対パスに変換
                file_path = os.path.abspath(path)
                # 同名のwavファイルが存在するかどうか判定
                txt_path = os.path.splitext(file_path)[0] + ".wav"
                # wavファイルが存在しなければ
                if not os.path.exists(txt_path):
                    # ファイルパスをリストに追加
                    file_paths.append(file_path)
    return file_paths


def movie2wav(folder_path):
    file_paths=get_video_paths(folder_path)
    """
    動画ファイルから音声を抽出し、同名の音声ファイルとして保存する関数
    """
    for file_path in file_paths:
        # 出力ファイルのパスを作成
        output_path = os.path.splitext(file_path)[0] + ".wav"
        
        # ffmpegを使用して音声を抽出
        command = f"ffmpeg -i \"{file_path}\" -q:a 0 -map a \"{output_path}\""
        os.system(command)


def main():
    # フォルダのパスを取得
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="フォルダ選択")
    print(get_video_paths(folder_path))
    movie2wav(folder_path)







if __name__ == '__main__':
    main()