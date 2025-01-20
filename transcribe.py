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


"""
参考
話者分離モデル(pyannote.audio)https://huggingface.co/pyannote/speaker-diarization-3.1


"""

import tkinter as tk
from tkinter import filedialog
import whisper
import os
import glob
import torch
import logging
from pyannote.audio import Pipeline,Audio
import ctypes
import sys
import openai
import json

from conf import *

import m2w

# .envからAPIキーを取得
# HUGGINGFACE_ACCESSTOKEN = os.getenv("HUGGINGFACE_ACCESSTOKEN")
# OPENAI_APIKEY =os.getenv("OPENAI_API_KEY")

# OpenAI APIキーを設定
openai.api_key = OPENAI_API_KEY
SPEAKER_DICT = {
    "Robot": "人間の話を聞いている。自分の情報をほとんど持たないので聞き役になることが多い．1人3役で話す",
    "Human": "実験への参加者。ロボットと話をしている。ロボットではないので，たくさんの個人情報を持っている",
    "実験者": "実験の主催者．最初に日付を述べたり，実験の説明をしたりする．ロボットとは会話しない",
}
MAX_SPEAKER=5

def smart_replacer(text:str,situation:str,find_words: list, replace_words: dict) -> dict:
    """
    ChatGPTを使用して、単語群を置き換えるマッピングを生成する。

    Args:
        text (str): 置き換える文章の全体像
        find_words (list): 上書きする単語のリスト ["単語1","単語2",...]
        replace_words (dict): 置き換え後の候補の辞書 {"単語1":"単語1の説明", "単語2":"単語2の説明", ...}

    Returns:
        dict: 置き換え前の単語と置き換え後の単語の辞書 {"上書きする単語1":"置き換え後1", "上書きする単語2":"置き換え後2", ...}
    """

    sys_prompt = f"""
# Instruction
あなたは、単語マッピング作成機です。
あなたには、与えられた文章及び単語のリストから、適切な単語の置き換えマッピングを生成してもらいます。
以下の説明に従って、上書きすべき単語をどの単語に置き換えればいいかを示してください。

# Situation
{situation}

# Input
## 上書きする単語のリスト
{find_words}
## 置き換え後の単語とその説明
{replace_words}

# Output
JSON形式で，置き換え前の単語と置き換え後の単語の辞書
- 上書きする単語はすべて，置き換え後の単語のどれかで置き換えなければならない
- 一つの単語に対応する置き換え候補が一つでないことがあるので，同じ置き換え後の単語を複数回使ってもよい
例: {{"上書きする単語1":"置き換え後の単語1", "上書きする単語2":"置き換え後の単語2", ...}} (上書きする単語のリストの要素数に応じてリサイズ)
"""
    # ChatGPTにリクエストを送信し、JSON形式でのレスポンスを期待
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": sys_prompt},{"role": "user", "content": text}],
        response_format={"type": "json_object"}
    )
    # レスポンスから置き換えた単語を取得し、辞書に変換
    try:
        replacement = json.loads(response.choices[0].message.content.strip())
    except json.JSONDecodeError:
        logging.error("レスポンスのJSON変換に失敗しました。")
        replacement = {}
    return replacement


def replacer_tester():
    # NoneとSPEAKER_00からSPEAKER_05までの文字列を含むリストを作成
    speaker_list = ["None"] + [f"SPEAKER_{i:02}" for i in range(6)]
    text="""
[00:00:00][SPEAKER_02]	今日は2024年11月10日10時6分、天気は曇り、実験コード201で実験を始めたいと思います。 本日はご覧いただきありがとうございます。
[00:01:00][SPEAKER_01]	本日はご覧いただきありがとうございます。
[00:01:29][SPEAKER_03]	本日はご覧いただきありがとうございます。 こんにちは。
[00:01:36][SPEAKER_00]	こんにちは。 やっほー。 今日は何してたの?
[00:01:43][SPEAKER_03]	今日は朝起きて実験の協力をずっとしてたよ。
[00:01:55][SPEAKER_00]	実験の協力か。面白そうだね。 どんな実験だったの? それって楽しかった?
[00:02:06][SPEAKER_03]	うん、楽しかった。 えっとね、ロボット越しに知らない人と話して、それでどういう印象を受けるのかみたいな実験をしてきたよ。
[00:02:23][SPEAKER_00]	ロボットと話すのワクワクだね。
[00:02:27][SPEAKER_01]	うん。
[00:02:29][SPEAKER_00]	ええ。 ロボットと話す実験が面白いね。 どんな印象を受けたの?
[00:02:36][SPEAKER_03]	どんな印象? だけど、初対面の人と話すより話しやすかったかな。 今日の朝とかは、その実験の協力のために、 9時? 9時集合だったんだけど、昨日、飲み会があってちょっと寝坊してしまったよ。
[00:03:10][SPEAKER_01]	どーし。 あ、きた。 あはは。 あはは。
[00:03:25][SPEAKER_00]	ロボットと面白いね。どんなことが話しやすかった。 優しいロボットだったのかな
[00:03:33][SPEAKER_01]	どんなロボットだったか
[00:03:46][SPEAKER_03]	ロボットを介して 知らない人と話すみたいな実験だったから ロボットと直接話したわけじゃないけど 初対面の人と話すよりは ロボットがあることによって 話しやすくなるとかあったよ
[00:04:06][SPEAKER_00]	ロボットが間にいると 安心感があるのかもしれないね 不思議だな ロボットのおかげで話しやすくなるって 面白いね その実験 他にも参加した人 たちいたの?
[00:04:31][SPEAKER_03]	うん、いたっぽい 全然知らない人だったけどね
[00:04:35][SPEAKER_00]	たくさんの人が参加してたんだね 知らない人と一緒に参加するのって ドキドキするよね その人たちとは話してみたの?
[00:04:58][None]	あー
"""
    situation="""
- 以下のように，[タイムスタンプ][話者ラベル] 発話内容のフォーマットで，ロボットと人間の会話実験の様子の録音音声が文字起こしされている．
    [00:00:00][SPEAKER_02]	今日は2024年11月10日10時6分、天気は曇り、実験コード201で実験を始めたいと思います。 本日はご覧いただきありがとうございます。
- 話者にラベルを付けることには成功したが，例えばラベル[SPEAKER_02]が具体的にだれを指すのかは不明であるため，あなたに判別してほしい
- 同じ話者に複数のラベルがついていることがある
- userが与えた上書きする単語リストに含まれないラベルが存在する場合，assistantの判断で出力に追加すること
"""
    replace_dict={"Robot":"人間の話を聞いている。自分の情報をほとんど持たないので聞き役になることが多い．1人3役で話す","Human":"ロボットと話をしている。ロボットではないので，たくさんの個人情報を持っている", "実験者":"実験の主催者．ほとんど話さないが，時々実験の教示などを行うことがある"}
    replace=smart_replacer(text,situation=situation,find_words=speaker_list,replace_words=replace_dict)
    print(replace)
    for old_word, new_word in replace.items():
        text = text.replace(old_word, new_word)
    print(text)



class Transcriber:
    def __init__(self):
        pass

    def snd2wav(self, filepath: str) -> str:
        """
        指定された音声ファイルを読み込み、.wav形式で保存する。
        既に.wav形式の場合は変換を行わない。

        Args:
            filepath (str): 音声ファイルのパス

        Returns:
            str: 変換後の.wavファイルのパス
        """
        import os
        from pydub import AudioSegment

        # ファイルの拡張子を取得
        _, ext = os.path.splitext(filepath)

        # .wavでない場合変換する
        if ext.lower() != ".wav":
            try:
                # 新しい.wavファイルのパスを作成
                wav_path = os.path.splitext(filepath)[0] + ".wav"
                # .wavファイルが既に存在する場合、変換をスキップ
                if os.path.exists(wav_path):
                    print(f".wavファイルが既に存在するため変換をスキップ: {wav_path}")
                    return ""
                # 音声ファイルを読み込む
                audio = AudioSegment.from_file(filepath)
                # .wav形式で保存
                audio.export(wav_path, format="wav")
                print(f"変換完了: {filepath} -> {wav_path}")
                return wav_path  # 変換後のファイルパスを返す
            except Exception as e:
                print(f"変換失敗: {filepath}. エラー: {e}")
                return ""
        else:
            print(f".wavファイルのため変換不要: {filepath}")
            return filepath  # 変換不要の場合、元のファイルパスを返す


    def get_audio_paths(self, folder_path):

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

    def get_video_paths(self, folder_path):
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
                    # 同名のテキストファイルが存在するかどうか判定
                    txt_path = os.path.splitext(file_path)[0] + ".txt"
                    # テキストファイルが存在しなければ
                    if not os.path.exists(txt_path):
                        # ファイルパスをリストに追加
                        file_paths.append(file_path)
        return file_paths

    def get_speaker(self, start, end, annotated_list):
        """
        指定された期間内で最も多く発話した話者をannotated_listから取得する。
        
        Args:
            start (float): 期間の開始時間（秒）
            end (float): 期間の終了時間（秒）
            annotated_list (list): 各音声セグメントと話者のリスト
        
        Returns:
            str: 最も発話時間が長い話者
        """
        speaker_durations = {}
        for segment, speaker in annotated_list:
            # セグメントが指定期間と重なる部分を計算
            overlap_start = max(start, segment.start)
            overlap_end = min(end, segment.end)
            overlap = max(0, overlap_end - overlap_start)
            if overlap > 0:
                if speaker in speaker_durations:
                    speaker_durations[speaker] += overlap
                else:
                    speaker_durations[speaker] = overlap
        if not speaker_durations:
            return None
        # 最も発話時間が長い話者を取得
        dominant_speaker = max(speaker_durations, key=speaker_durations.get)
        return dominant_speaker

    def map_speaker(self, text: str, replace_dict: dict) -> str:
        """
        与えられたテキストの話者部分を置換するメソッド。
        
        Args:
            text (str): 話者ラベルを含むテキスト
            replace_dict (dict): 置換辞書
        
        Returns:
            str: 話者ラベルが置換されたテキスト
        """
        # 話者ラベルのリストを作成
        speaker_list = ["None"] + [f"SPEAKER_{i:02}" for i in range(MAX_SPEAKER)]
        
        # situationを定義
        situation = """
        - 以下のように，"[タイムスタンプ][話者ラベル] 発話内容" のフォーマットで，ロボットと人間の会話実験の様子の録音音声が文字起こしされている．
            [00:00:00][SPEAKER_04] 今日は2024年11月10日10時6分、天気は曇り、実験コード201で実験を始めたいと思います。 本日はご覧いただきありがとうございます。
        - 話者にラベルを付けることには成功したが，例えばラベル[SPEAKER_04]が具体的にだれを指すのかは不明であるため，あなたに判別してほしい
        - 同じ話者に複数のラベルが対応していることがある
        """
        
        # smart_replacerを使用して置換を実行
        replace = smart_replacer(text, situation=situation, find_words=speaker_list, replace_words=replace_dict)
        
        # 置換結果をテキストに反映
        for old_word, new_word in replace.items():
            text = text.replace(old_word, new_word)
        
        return text

    def save_result(self, file_path, result, annotated_list: list):
        file_path = os.path.normpath(file_path)
        # 出力を保存するディレクトリを指定
        output_dir = os.path.dirname(file_path)  # os.path.dirnameで親ディレクトリを取得
        output_name = os.path.basename(file_path)
        index = output_name.rfind(".")

        #"."が見つかった場合
        if index != -1:  # "."から右を"txt"に置き換える 
            output_name = output_name[:index] + ".txt"
        # 出力ファイルのパスを作成
        output_path = os.path.join(output_dir, output_name)
        print("output: " + output_path)
        # 音声区間ごとに処理
        text=""
        # 1つ前のループの話者を保存する変数を初期化
        previous_speaker = None
        previous_text =None
        for segment in result["segments"]:
            speaker = self.get_speaker(segment["start"], segment["end"], annotated_list)
            if previous_speaker!=speaker:
                # 音声区間の開始時間(秒)を取得
                seconds = int(segment["start"])
                # 時間・分・秒に変換する
                hours = seconds // 3600  # 1時間は3600秒
                minutes = (seconds % 3600) // 60  # 残りの秒数を60で割る
                seconds = (seconds % 3600) % 60  # 残りの秒数を60で割った余り
                # 書き込み
                text+=f"\n[{hours:02}:{minutes:02}:{seconds:02}][{speaker}]\t{segment['text']}"
            else:
                if previous_text!=segment['text']:# 同じ認識が繰り返されるバグが起きることがあるので，対策
                    # 前回の記述に追記
                    text+=' '+segment['text']
            previous_text=segment['text']
            previous_speaker=speaker
        text=self.map_speaker(text,SPEAKER_DICT)
        # 出力ファイルに書き込み
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(text)

    def setup_logger(self):
        """ロガーを設定する関数"""
        # ロガーを作成
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)  # ログレベルをDEBUGに設定

        # コンソールハンドラを作成してロガーに追加
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)

        # フォーマッタを作成してハンドラに設定
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)

        # ハンドラをロガーに追加
        logger.addHandler(console_handler)

        # ログメッセージを出力
        logger.debug("Logger has been set up.")
        return logger
    
    def get_annotated_list(self,file_path):
        # 話者分離のためのモデルを準備 (なければダウンロードする)
        """
        ここで権限がどうとか言うエラーが出たら，開発者モードをONにしてみる (もしくは，管理者権限でpythonを実行する)
        また，huggingfaceのアカウントで認証(↓)が必要
        https://huggingface.co/pyannote/speaker-diarization/tree/main
        https://huggingface.co/pyannote/segmentation
        """
        pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization",use_auth_token=HUGGINGFACE_ACCESSTOKEN)
        if torch.cuda.is_available():
            self.logger.debug("diarization: GPUで動作")
            pipeline.to(torch.device("cuda"))
        else:
            self.logger.debug("diarization: CPUで動作")
        diarization=pipeline(file_path)
        annotated_list=[] # 話者分離結果を格納するリスト
        for segment, _, speaker in diarization.itertracks(yield_label=True):
            self.logger.debug(f"[{segment.start:03.1f}s - {segment.end:03.1f}s] {speaker}")
            annotated_list.append([segment,speaker])
        del pipeline
        del diarization
        torch.cuda.empty_cache()
        return annotated_list

    
    def whisper_recognition(self,file_path,annotated_list):
        # whisperモデルのロード (無ければwebからダウンロード)
        model_size = "large-v2"  # 使用するモデルサイズ(v3はめっちゃハルシネーションが起こるのでv2を利用．これ以上精度上げるならもっといいデバイス使うしかない)
        if torch.cuda.is_available():
            """
            GPU利用にはcudaをインストールする必要がある．cudaのバージョンは環境依存なので中級者向け．だいたいcu118でいいけど，やりこむならもっと別のバージョン入れる
            python3 -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
            """
            model = whisper.load_model(model_size, device="cuda")  # GPUを指定
            self.logger.debug("GPUを使用してモデルをロードしました。")
        else:
            model = whisper.load_model(model_size)  # デフォルト(CPUを指定)
            self.logger.debug("CPUを使用してモデルをロードしました。")
        
        result = model.transcribe(file_path, verbose=True, language="ja")
        self.save_result(file_path,result,annotated_list)

        # 使い終わったらリリース (めっちゃGPUメモリ食うので)
        del model
        torch.cuda.empty_cache()

    def transcribe(self,dirpath):
        """メイン関数"""
        # ロガーを設定
        self.logger = self.setup_logger()


        # 利用可能なwhisperモデルを表示
        print(whisper.available_models())


        # 動画ファイルを音声に変換する
        m2w.movie2wav(dirpath)

        file_paths=self.get_audio_paths(dirpath)

        wav_paths=[]
        # pyannoteが一部の音声ファイルを受け付けないので(少なくともm4aは無理)，.wavに変換
        for file_path in file_paths:
            wav_path=self.snd2wav(file_path)
            if wav_path:
                wav_paths.append(wav_path)
        self.logger.debug(f".wavファイルのリスト: {wav_paths}")
        
        # 音声ファイルを文字起こし
        for wav_path in wav_paths:
            annotated_list=self.get_annotated_list(wav_path)
            self.whisper_recognition(wav_path,annotated_list)

def main():
    transcriber=Transcriber()
    
    # まとめて文字起こししたいフォルダのパスを取得
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="フォルダ選択")

    transcriber.transcribe(folder_path)



if __name__ == "__main__":
    
    main()
    # replacer_tester()