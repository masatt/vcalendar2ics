import re
import quopri

def convert_to_ics(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as file:
        data = file.read()

    # VEVENTを抽出
    events = re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", data, re.DOTALL)
    total_events = len(events)
    print(f"総イベント数: {total_events}")

    ics_content = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Your App Name//NONSGML v1.0//EN\nCALSCALE:GREGORIAN\n"

    for index, event in enumerate(events, start=1):
        print(f"{index}/{total_events} 件目を処理中...")
        try:
            event_data = "BEGIN:VEVENT\n"
            lines = event.strip().split("\n")
            i = 0
            while i < len(lines):
                line = lines[i]
                if line.startswith("SUMMARY;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:") or line.startswith("DESCRIPTION;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:"):
                    # Quoted-Printableのデータを処理
                    field_name, encoded_value = line.split(":", 1)
                    while encoded_value.endswith("=") and i + 1 < len(lines):
                        i += 1
                        encoded_value = encoded_value[:-1] + lines[i].strip()
                    try:
                        decoded_value = quopri.decodestring(encoded_value).decode('utf-8')
                    except Exception as e:
                        decoded_value = "デコードエラー"
                        print(f"{field_name} デコードエラー: {e}")
                    event_data += f"{field_name.split(';')[0]}:{decoded_value}\n"
                else:
                    # 他のフィールドはそのまま追加
                    event_data += line + "\n"
                i += 1
            event_data += "END:VEVENT\n"
            ics_content += event_data
        except Exception as e:
            print(f"{index}/{total_events} 件目でエラー発生: {e}")
            print("問題のイベントをスキップします。")
            continue

    ics_content += "END:VCALENDAR\n"

    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(ics_content)

    print(f"変換が完了しました: {output_file}")

# 入力ファイルと出力ファイルの指定
input_vcalendar = "input.vcalendar"
output_ics = "output.ics"

convert_to_ics(input_vcalendar, output_ics)
