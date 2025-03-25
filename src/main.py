import flet as ft
import csv_handler  # 外部ファイルをインポート

def main(page: ft.Page): 
    page.title = "CSV Converter" 
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.padding = 20

    status_text = ft.Text()
    download_button = ft.ElevatedButton("Download CSV", disabled=True)

    modified_csv_data = None  # 変更後のCSVデータを一時保存

    def on_file_selected(e: ft.FilePickerResultEvent):
        nonlocal modified_csv_data
        if e.files:
            file_path = e.files[0].path
            modified_csv_data = csv_handler.process_csv(file_path)  # 外部ファイルの関数を呼ぶ

            if modified_csv_data.startswith("エラー"):
                status_text.value = modified_csv_data
                download_button.disabled = True
            else:
                download_button.disabled = False
                status_text.value = "CSVファイルの処理が完了しました。ダウンロードできます。"

            page.update()

    def on_save_dialog_result(e: ft.FilePickerResultEvent):
        """ファイルを保存する"""
        if e.path and modified_csv_data:
            try:
                with open(e.path, "w", encoding="utf-8") as f:
                    f.write(modified_csv_data)
                status_text.value = "CSVファイルを正常に保存しました。"
            except Exception as ex:
                status_text.value = f"保存エラー: {str(ex)}"

            page.update()

    def on_download(e):
        """保存ダイアログを開く"""
        file_saver.save_file(file_name="modified_csv.csv", file_type=ft.FilePickerFileType.CUSTOM, allowed_extensions=["csv"])

    file_picker = ft.FilePicker(on_result=on_file_selected)
    file_saver = ft.FilePicker(on_result=on_save_dialog_result)  # 保存用
    page.overlay.extend([file_picker, file_saver])

    page.add(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.ElevatedButton("ファイルを選択", on_click=lambda _: file_picker.pick_files(allowed_extensions=["csv"])),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                status_text,
                ft.Row(
                    [download_button],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
            ]
        )
    )

    download_button.on_click = on_download  # ダウンロードボタンに動作を設定

ft.app(target=main)
