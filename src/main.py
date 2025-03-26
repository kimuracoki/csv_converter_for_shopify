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
    modified_csv_data = None 

    def check_ready_to_download():
        """ 両方のCSVがアップロードされたかチェック """
        download_button.disabled = not (file_path_1 and file_path_2)
        page.update()

    def on_file_selected_1(e: ft.FilePickerResultEvent):
        nonlocal file_path_1
        if e.files:
            file_path_1 = e.files[0].path
            status_text.value = "1つ目のCSVファイルが選択されました。"
            check_ready_to_download()

    def on_file_selected_2(e: ft.FilePickerResultEvent):
        nonlocal file_path_2
        if e.files:
            file_path_2 = e.files[0].path
            status_text.value = "2つ目のCSVファイルが選択されました。"
            check_ready_to_download()

    def process_files():
        nonlocal modified_csv_data
        if file_path_1 and file_path_2:
            modified_csv_data = csv_handler.process_csv(file_path_1, file_path_2)
            status_text.value = "CSVファイルの処理が完了しました。"
            download_button.disabled = False
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
        """CSVを処理して保存ダイアログを開く"""
        process_files()
        file_saver.save_file(file_name="merged_csv.csv", file_type=ft.FilePickerFileType.CUSTOM, allowed_extensions=["csv"])

    file_picker_1 = ft.FilePicker(on_result=on_file_selected_1)
    file_picker_2 = ft.FilePicker(on_result=on_file_selected_2)
    file_saver = ft.FilePicker(on_result=on_save_dialog_result)  
    page.overlay.extend([file_picker_1, file_picker_2, file_saver])

    page.add(
        ft.Column(
            [
                ft.Row(
                    [
                        ft.ElevatedButton("1つ目のファイルを選択", on_click=lambda _: file_picker_1.pick_files(allowed_extensions=["csv"])),
                        ft.ElevatedButton("2つ目のファイルを選択", on_click=lambda _: file_picker_2.pick_files(allowed_extensions=["csv"])),
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