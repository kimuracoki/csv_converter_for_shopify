import flet as ft
import csv_handler  

def main(page: ft.Page): 
    page.title = "CSV Converter" 
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.padding = 20

    status_text = ft.Text()
    download_button = ft.ElevatedButton("Download CSV", disabled=True)

    file_path_1 = None
    file_path_2 = None
    modified_csv_data = []  # CSV分割用のリスト

    def check_ready_to_download():
        """ 両方のCSVがアップロードされたかチェック """
        download_button.disabled = not (file_path_1 and file_path_2)
        page.update()

    def on_file_selected_1(e: ft.FilePickerResultEvent):
        nonlocal file_path_1
        if e.files:
            file_path_1 = e.files[0].path
            status_text.value = "商品一覧CSVが選択されました。"
            check_ready_to_download()

    def on_file_selected_2(e: ft.FilePickerResultEvent):
        nonlocal file_path_2
        if e.files:
            file_path_2 = e.files[0].path
            status_text.value = "バリエーションCSVが選択されました。"
            check_ready_to_download()

    def process_files():
        """ CSVを処理し、15MBごとに分割 """
        nonlocal modified_csv_data
        if file_path_1 and file_path_2:
            modified_csv_data = csv_handler.process_csv(file_path_1, file_path_2)
            status_text.value = f"CSVファイルの処理が完了しました。（{len(modified_csv_data)}個に分割）"
            download_button.disabled = False
            page.update()

    def on_save_dialog_result(e: ft.FilePickerResultEvent, index: int):
        """複数のCSVファイルを保存"""
        if e.path and modified_csv_data:
            try:
                with open(e.path, "w", encoding="utf-8") as f:
                    f.write(modified_csv_data[index])
                status_text.value = f"CSVファイル {index+1} を保存しました。"
            except Exception as ex:
                status_text.value = f"保存エラー: {str(ex)}"

            page.update()

            # 次のファイルの保存ダイアログを開く
            if index + 1 < len(modified_csv_data):
                file_saver.save_file(file_name=f"merged_part_{index+2}.csv", file_type=ft.FilePickerFileType.CUSTOM, allowed_extensions=["csv"], on_result=lambda e: on_save_dialog_result(e, index + 1))

    def on_download(e):
        """CSVを処理して保存ダイアログを開く（複数ファイル対応）"""
        process_files()
        if modified_csv_data:
            # 最初のファイルの保存ダイアログを開く
            file_saver.save_file(file_name="merged_part_1.csv", file_type=ft.FilePickerFileType.CUSTOM, allowed_extensions=["csv"], on_result=lambda e: on_save_dialog_result(e, 0))

    file_picker_1 = ft.FilePicker(on_result=on_file_selected_1)
    file_picker_2 = ft.FilePicker(on_result=on_file_selected_2)
    file_saver = ft.FilePicker()  # 結果の処理は動的に設定
    page.overlay.extend([file_picker_1, file_picker_2, file_saver])

    page.add(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.ElevatedButton("商品一覧CSVを選択", on_click=lambda _: file_picker_1.pick_files(allowed_extensions=["csv"])),
                        ft.ElevatedButton("バリエーションCSVを選択", on_click=lambda _: file_picker_2.pick_files(allowed_extensions=["csv"])),
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

    download_button.on_click = on_download  

ft.app(target=main)
