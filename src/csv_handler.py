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
        key = str(row["key"]).strip() 
        
        # variant の内容を取得
        variant_cell = row["variant"]
        
        # variant を行ごとに分割
        variant_lines = variant_cell.split("\n")
        
        parsed_variants = []
        
        for variant in variant_lines:
            parts = variant.split(" ", 1)
            if len(parts) == 2:
                name, values = parts
                parsed_variants.append((name, values.split()))  # 2番目の部分（オプション）を分割
        
        # 値の組み合わせを生成
        value_combinations = list(itertools.product(*[v for _, v in parsed_variants]))
        
        # DataFrame 用のデータ
        output = []
        for values in value_combinations:
            flat_list = list(itertools.chain(*zip([name for name, _ in parsed_variants], values)))
            row_data = flat_list + ([""] * (6 - len(flat_list)))  # 最大3ペア (name, value)まで埋める
            output.append(row_data)

        # DataFrame を作成
        header = []
        for i in range(1, 4):  # 最大3つの属性を想定
            header.extend([f"name{i}", f"value{i}"])

        df_variant = pd.DataFrame(output, columns=header)
        
        # key と DataFrame をタプルとして追加
        key_df_list.append((key, df_variant))

    # 結果を表示
    for key, df in key_df_list:
        print(f"Key: {key}")
        print(df)

    return key_df_list