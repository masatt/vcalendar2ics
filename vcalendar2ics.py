import re
import quopri
import uuid
from datetime import datetime, timedelta
import os


def fold_line(line):
    """75文字を超える行を折り返し"""
    if len(line) <= 75:
        return line
    return "\r\n ".join([line[i:i + 75] for i in range(0, len(line), 75)])


def escape_special_characters(value):
    """ICSファイル用に特殊文字をエスケープ"""
    return value.replace("\\", "\\\\").replace(",", "\\,").replace(";", "\\;").replace("\n", "\\n")


def decode_quoted_printable(field_name, encoded_value):
    """Quoted-Printableエンコードをデコード"""
    try:
        decoded_value = quopri.decodestring(encoded_value).decode('utf-8')
        return escape_special_characters(decoded_value)
    except Exception as e:
        print(f"{field_name} デコードエラー: {e}")
        return "デコードエラー"


def clean_event_data(event_data):
    """不必要なカスタムフィールドを削除"""
    lines = event_data.split("\n")
    filtered_lines = []
    for line in lines:
        # 不要なフィールドを除外
        if not line.startswith(("TZ:+09:00", "CATEGORIES:", "AALARM:", "DALARM:", "RRULE:", "STATUS:", "DUE:", "X-DCM-")):
            filtered_lines.append(line)
    return "\n".join(filtered_lines)


def convert_to_google_calendar_ics(input_file, output_dir):
    try:
        # 入力ファイルを読み込み
        with open(input_file, 'r', encoding='utf-8') as file:
            data = file.read()
        print("入力ファイルを読み込みました。")

        # VEVENTを抽出
        events = re.findall(r"BEGIN:VEVENT(.*?)END:VEVENT", data, re.DOTALL)
        total_events = len(events)
        print(f"総イベント数: {total_events}")

        # 出力ディレクトリ作成
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # イベント処理
        for index, event in enumerate(events, start=1):
            print(f"{index}/{total_events} 件目を処理中...")
            try:
                fields = {}
                lines = event.strip().split("\n")
                dtstart_value = None

                # 各フィールドをバッファリング
                i = 0
                while i < len(lines):
                    line = lines[i]
                    if line.startswith("SUMMARY;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:"):
                        field_name, encoded_value = line.split(":", 1)
                        while encoded_value.endswith("=") and i + 1 < len(lines):
                            i += 1
                            encoded_value = encoded_value[:-1] + lines[i].strip()
                        fields["SUMMARY"] = f"SUMMARY:{decode_quoted_printable('SUMMARY', encoded_value)}\n"
                    elif line.startswith("DESCRIPTION;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:"):
                        field_name, encoded_value = line.split(":", 1)
                        while encoded_value.endswith("=") and i + 1 < len(lines):
                            i += 1
                            encoded_value = encoded_value[:-1] + lines[i].strip()
                        fields["DESCRIPTION"] = f"DESCRIPTION:{decode_quoted_printable('DESCRIPTION', encoded_value)}\n"
                    elif line.startswith("LOCATION;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:"):
                        field_name, encoded_value = line.split(":", 1)
                        while encoded_value.endswith("=") and i + 1 < len(lines):
                            i += 1
                            encoded_value = encoded_value[:-1] + lines[i].strip()
                        fields["LOCATION"] = f"LOCATION:{decode_quoted_printable('LOCATION', encoded_value)}\n"
                    elif line.startswith("DTSTART"):
                        dtstart_value = line.split(":", 1)[1]
                        fields["DTSTART"] = fold_line(line) + "\n"
                    else:
                        field_key = line.split(":", 1)[0]
                        fields[field_key] = fold_line(line) + "\n"
                    i += 1

                if "DTSTART" not in fields:
                    print(f"{index}/{total_events} 件目で開始日時が欠落しています。スキップします。")
                    continue

                # 必須フィールドの順序を調整
                event_data = "BEGIN:VEVENT\n"
                event_data += fields.get("DTSTART", "")
                event_data += fields.get("SUMMARY", "SUMMARY:Untitled Event\n")
                event_data += fields.get("DESCRIPTION", "")
                event_data += fields.get("LOCATION", "")
                for key, value in fields.items():
                    if key not in ("DTSTART", "SUMMARY", "DESCRIPTION", "LOCATION"):
                        event_data += value

                # DTENDを追加（1時間後を終了時刻とする）
                if dtstart_value and "DTEND" not in fields:
                    try:
                        dtstart_obj = datetime.strptime(dtstart_value, '%Y%m%dT%H%M%SZ')
                        dtend_obj = dtstart_obj + timedelta(hours=1)
                        dtend_value = dtend_obj.strftime('%Y%m%dT%H%M%SZ')
                        event_data += fold_line(f"DTEND:{dtend_value}") + "\n"
                    except ValueError as ve:
                        print(f"{index}/{total_events} 件目でDTSTARTの形式が不正です: {ve}")
                        continue

                # クリーンアップ
                event_data = clean_event_data(event_data)

                # 必須フィールドを追加
                dtstamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
                uid = str(uuid.uuid4()) + "@yourdomain.com"
                event_data += fold_line(f"DTSTAMP:{dtstamp}") + "\n"
                event_data += fold_line(f"UID:{uid}") + "\n"
                event_data += "TRANSP:OPAQUE\n"
                event_data += "END:VEVENT\n"

                # 各イベントを個別ファイルに出力
                output_file = os.path.join(output_dir, f"event_{index:03d}.ics")
                with open(output_file, 'w', encoding='utf-8') as file:
                    file.write("BEGIN:VCALENDAR\n")
                    file.write("VERSION:2.0\n")
                    file.write(event_data)
                    file.write("END:VCALENDAR\n")

                print(f"{index}/{total_events} 件目を {output_file} に保存しました。")
            except Exception as e:
                print(f"{index}/{total_events} 件目でエラー発生: {e}")
                continue

    except Exception as e:
        print(f"致命的なエラーが発生しました: {e}")


# 入力ファイルと出力ディレクトリの指定
input_vcalendar = "input.vcalendar"
output_dir = "output_events"

convert_to_google_calendar_ics(input_vcalendar, output_dir)
