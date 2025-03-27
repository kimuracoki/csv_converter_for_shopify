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
        df = pd.read_csv(file_path1, encoding="shift_jis", quotechar='"', quoting=csv.QUOTE_ALL, lineterminator='\n', skipinitialspace=True)

        new_df = pd.DataFrame()

        for new_col, old_col in MAPPING.items():
            if old_col in df.columns: 
                new_df[new_col] = df[old_col] 
            else:
                new_df[new_col] = "" 
        
        parse_variant_results = parse_variant_csv(file_path2)
        parsed_keys = {key for key, _ in parse_variant_results}  # parse_variant_csv の key 一覧

        merged_data = []

        new_df["SKU"] = new_df["SKU"].astype(str).str.strip()

        # 結合処理
        for key, df_variant in parse_variant_results:
            key = str(key).strip()
            # `SKU` と `key` が一致するデータを取得
            df_match = new_df[new_df["SKU"] == key]

            if not df_match.empty:
                for i, (_, row) in enumerate(df_variant.iterrows(), start=1):
                    new_row = df_match.copy()  # 結合元のデータをコピー
                    new_row["SKU"] = str(key) + f"-{i:02d}"
                    new_row["Option1 name"] = row["name1"]
                    new_row["Option1 value"] = row["value1"]
                    new_row["Option2 name"] = row["name2"]
                    new_row["Option2 value"] = row["value2"]
                    new_row["Option3 name"] = row["name3"]
                    new_row["Option3 value"] = row["value3"]
                    merged_data.append(new_row)  # リストに追加
                    print("マージ中：SKU = ", new_row["SKU"])

        # `SKU` が `parse_variant_csv` にない場合の処理
        df_no_match = new_df[~new_df["SKU"].isin(parsed_keys)].copy()
        if not df_no_match.empty:
            df_no_match["SKU"] = df_no_match["SKU"].astype(str) + "-00"
            df_no_match["Option1 name"] = ""
            df_no_match["Option1 value"] = ""
            df_no_match["Option2 name"] = ""
            df_no_match["Option2 value"] = ""
            df_no_match["Option3 name"] = ""
            df_no_match["Option3 value"] = ""
            merged_data.append(df_no_match)
            print("マージ中：SKU = ", df_no_match["SKU"])

        # `merged_data` が空でない場合のみ `concat` を実行
        df_merged = pd.concat(merged_data, ignore_index=True) if merged_data else new_df.copy()
        
        
        csv_buffer = io.StringIO()
        df_merged.to_csv(csv_buffer, index=False, encoding="utf-8", sep=",")
        print("処理完了")
        return csv_buffer.getvalue()

    except Exception as ex:
        return f"エラー: {str(ex)}"

def parse_variant_csv(file_path):
    df = pd.read_csv(file_path, encoding="shift_jis", quotechar='"', quoting=csv.QUOTE_ALL, lineterminator='\n', skipinitialspace=True)
    key_df_list = []
    
    for _, row in df.iterrows():
        key = str(row["code"]).strip()
        print("バリエーション取得中：key = ", key)
        
        # variant の内容を取得
        variant_cell = row["options"]
        if pd.isna(variant_cell):
            continue 
        
        # variant を行ごとに分割
        variant_lines = variant_cell.split("\n")
        
        parsed_variants = []
        
        for variant in variant_lines:
            parts = variant.replace("選択して下さい", "").split(" ", 1)
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