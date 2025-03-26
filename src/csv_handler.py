import pandas as pd
import itertools
import io
import json
import csv

with open("./config/mapping.json", "r", encoding="utf-8") as f:
    MAPPING = json.load(f)  

def process_csv(file_path1, file_path2):
    """Shift JIS の CSV を読み込み、マッピング情報を追加して UTF-8 で返す"""
    try:
        df = pd.read_csv(file_path1, encoding="utf-8")

        new_df = pd.DataFrame()

        for new_col, old_col in MAPPING.items():
            for index, option in enumerate(parse_variant_csv(file_path2)):
                if old_col in df.columns:
                    new_df[new_col] = df[old_col]  
                    # バリエーションによって上書き
                    # new_df['Handle'] = new_df['Handle'] + index
                    # new_df['Variant SKU'] = new_df['Variant SKU'] + index 
                    new_df['Option 1 Name'] = option['name1']
                    new_df['Option 1 Value'] = option['value1']
                    new_df['Option 2 Name'] = option['name2']
                    new_df['Option 2 Value'] = option['value2']
                    new_df['Option 3 Name'] = option['name3']
                    new_df['Option 3 Value'] = option['value3']
                else:
                    new_df[new_col] = ""  

        
        csv_buffer = io.StringIO()
        new_df.to_csv(csv_buffer, index=False, encoding="utf-8", sep=",")
        return csv_buffer.getvalue()

    except Exception as ex:
        return f"エラー: {str(ex)}"

def parse_variant_csv(file_path):
    df = pd.read_csv(file_path, encoding="utf-8", quotechar='"', quoting=csv.QUOTE_ALL, lineterminator='\n', skipinitialspace=True, dtype={'key': str})

    key_df_list = []
    
    for _, row in df.iterrows():
        key = str(row["key"]).strip()  # key を文字列として取得
        
        # 空の DataFrame を作成（カラムのみ定義）
        df_variant = pd.DataFrame(columns=["name1", "value1", "name2", "value2", "name3", "value3"])

        # key と空の DataFrame をタプルとして追加
        key_df_list.append((key, df_variant))

    for key, df in key_df_list:
        print(f"Key: {key}")
        print(df)

    return key_df_list