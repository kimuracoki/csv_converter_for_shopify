import pandas as pd
import io
import json

# マッピングファイルの読み込み
with open("./config/mapping.json", "r", encoding="utf-8") as f:
    MAPPING = json.load(f)  # {"Title": "商品名", "Vendor": "ショップサーブカテゴリ名"}

def process_csv(file_path):
    """Shift JIS の CSV を読み込み、マッピング情報を追加して UTF-8 で返す"""
    try:
        # Shift JIS で CSV を読み込む
        df = pd.read_csv(file_path, encoding="shift_jis")

        # すべての項目をそのままコピー
        new_df = pd.DataFrame()

        # マッピングに従って新しいカラムを追加
        for new_col, old_col in MAPPING.items():
            if old_col in df.columns:
                new_df[new_col] = df[old_col]  # 対応するデータをコピー
            else:
                new_df[new_col] = ""  # 該当データがなければ空白

        # DataFrame を UTF-8 の文字列に変換
        csv_buffer = io.StringIO()
        new_df.to_csv(csv_buffer, index=False, encoding="utf-8", sep=",")
        return csv_buffer.getvalue()

    except Exception as ex:
        return f"エラー: {str(ex)}"
