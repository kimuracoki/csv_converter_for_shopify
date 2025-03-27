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
        df = pd.read_csv(file_path1, encoding="utf-8", quotechar='"', quoting=csv.QUOTE_ALL, lineterminator='\n', skipinitialspace=True)

        new_df = pd.DataFrame()

        for new_col, old_col in MAPPING.items():
            if old_col in df.columns: 
                new_df[new_col] = df[old_col] 
            else:
                new_df[new_col] = "" 
        
        parse_variant_results = parse_variant_csv(file_path2)
        parsed_keys = {key for key, _ in parse_variant_results}  # parse_variant_csv の key 一覧

        merged_data = []

        # 結合処理
        for key, df_variant in parse_variant_results:
            # `Handle` と `key` が一致するデータを取得
            df_match = new_df[new_df["Handle"] == key]

            if not df_match.empty:
                for i, (_, row) in enumerate(df_variant.iterrows(), start=1):
                    new_row = df_match.copy()  # 結合元のデータをコピー
                    new_row["Handle"] = key + f"-{i:02d}"  # Handleを "-01", "-02" のように採番
                    new_row["Option 1 Name"] = row["name1"]
                    new_row["Option 1 Value"] = row["value1"]
                    new_row["Option 2 Name"] = row["name2"]
                    new_row["Option 2 Value"] = row["value2"]
                    new_row["Option 3 Name"] = row["name3"]
                    new_row["Option 3 Value"] = row["value3"]
                    merged_data.append(new_row)  # リストに追加

        # `Handle` が `parse_variant_csv` にない場合の処理
        df_no_match = new_df[~new_df["Handle"].isin(parsed_keys)].copy()
        if not df_no_match.empty:
            df_no_match["Handle"] = df_no_match["Handle"] + "-00"  # Handle に "-00" を追加
            df_no_match["Option 1 Name"] = ""
            df_no_match["Option  Value"] = ""
            df_no_match["Option 2 Name"] = ""
            df_no_match["Option 2 Value"] = ""
            df_no_match["Option 3 Name"] = ""
            df_no_match["Option 3 Value"] = ""
            merged_data.append(df_no_match)

        # `merged_data` が空でない場合のみ `concat` を実行
        df_merged = pd.concat(merged_data, ignore_index=True) if merged_data else new_df.copy()
        
        
        csv_buffer = io.StringIO()
        df_merged.to_csv(csv_buffer, index=False, encoding="utf-8", sep=",")
        return csv_buffer.getvalue()

    except Exception as ex:
        return f"エラー: {str(ex)}"

def parse_variant_csv(file_path):
    df = pd.read_csv(file_path, encoding="utf-8", quotechar='"', quoting=csv.QUOTE_ALL, lineterminator='\n', skipinitialspace=True)

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

    return key_df_list