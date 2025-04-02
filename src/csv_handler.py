import re
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
            if isinstance(old_col, list):  # old_col がリストの場合
                valid_cols = [col for col in old_col if col in df.columns]  # 存在するカラムを取得
                if valid_cols:
                    new_df[new_col] = df[valid_cols].astype(str).apply(lambda row: ' '.join(row), axis=1)
                else:
                    new_df[new_col] = ""
            elif old_col in df.columns: 
                new_df[new_col] = df[old_col] 
            else:
                new_df[new_col] = "" 

        if "Description" in new_df.columns:
            new_df["Description"] = new_df["Description"].astype(str).apply(process_html)
        
        parse_variant_results = parse_variant_csv(file_path2)
        parsed_keys = {key for key, _ in parse_variant_results}  # parse_variant_csv の key 一覧

        merged_data = []

        new_df["SKU"] = new_df["SKU"].astype(str).str.strip()

        # 結合処理
        for key, df_variant in parse_variant_results:
            key = str(key).strip()
            df_match = new_df[new_df["SKU"] == key]

            if not df_match.empty:
                for i, (_, row) in enumerate(df_variant.iterrows(), start=1):
                    new_row = df_match.copy()
                    new_row["SKU"] = str(key) + f"-{i:02d}"
                    new_row["Option1 name"] = row["name1"]
                    new_row["Option1 value"] = row["value1"]
                    new_row["Option2 name"] = row["name2"]
                    new_row["Option2 value"] = row["value2"]
                    new_row["Option3 name"] = row["name3"]
                    new_row["Option3 value"] = row["value3"]
                    merged_data.append(new_row)
                    print("マージ中：SKU = ", new_row["SKU"])

        df_no_match = new_df[~new_df["SKU"].isin(parsed_keys)].copy()
        if not df_no_match.empty:
            df_no_match["SKU"] = df_no_match["SKU"].astype(str) + "-00"
            df_no_match[["Option1 name", "Option1 value", "Option2 name", "Option2 value", "Option3 name", "Option3 value"]] = ""
            merged_data.append(df_no_match)
            print("マージ中：SKU = ", df_no_match["SKU"])

        df_merged = pd.concat(merged_data, ignore_index=True) if merged_data else new_df.copy()
        
        # 不要なdomを除去＆置き換え
        
        chunk_size = 6000
        csv_chunks = []
        
        for i, chunk in enumerate(range(0, len(df_merged), chunk_size)):
            csv_buffer = io.StringIO()
            df_merged.iloc[chunk:chunk + chunk_size].to_csv(csv_buffer, index=False, encoding="utf-8", sep=",")
            csv_chunks.append((f"merged_part_{i+1}.csv", csv_buffer.getvalue()))
            
        print("処理完了")
        return csv_chunks  # (ファイル名, データ) のリストを返す

    except Exception as ex:
        return [("error.txt", f"エラー: {str(ex)}")]

def parse_variant_csv(file_path):
    df = pd.read_csv(file_path, encoding="shift_jis", quotechar='"', quoting=csv.QUOTE_ALL, lineterminator='\n', skipinitialspace=True)
    key_df_list = []
    
    for _, row in df.iterrows():
        key = str(row["code"]).strip()
        print("バリエーション取得中：key = ", key)
        
        variant_cell = row["options"]
        if pd.isna(variant_cell):
            continue 
        
        variant_lines = variant_cell.split("\n")
        parsed_variants = []
        
        for variant in variant_lines:
            parts = variant.replace("選択して下さい", "").replace("選択してください", "").split(" ", 1)
            if len(parts) == 2:
                name, values = parts
                parsed_variants.append((name, values.split()))
        
        value_combinations = list(itertools.product(*[v for _, v in parsed_variants]))
        output = []
        for values in value_combinations:
            flat_list = list(itertools.chain(*zip([name for name, _ in parsed_variants], values)))
            row_data = flat_list + ([""] * (6 - len(flat_list)))
            output.append(row_data)

        header = []
        for i in range(1, 4):
            header.extend([f"name{i}", f"value{i}"])

        df_variant = pd.DataFrame(output, columns=header)
        key_df_list.append((key, df_variant))

    return key_df_list

def process_html(html: str) -> str:
    html = re.sub(r'<a [^>]*>', '', html)  # <a ...> の開始タグを削除
    html = re.sub(r'</a>', '', html)  # </a> の閉じタグを削除
    html = re.sub(r'<h4>', '<h3>', html)  # <h4> → <h3>
    html = re.sub(r'</h4>', '</h3>', html)  # </h4> → </h3>
    return html