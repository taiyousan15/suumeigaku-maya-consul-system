#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
マヤ暦表の全52年分のCSVファイルを1つに統合するスクリプト
"""

import os
import csv
import calendar
from pathlib import Path

# 基本パス設定
BASE_DIR = Path("/Users/matsumototoshihiko/div/算命学とマヤ暦コンサルシステム/マヤ暦表")
OUTPUT_DIR = BASE_DIR / "マヤ暦表すべて換算表"
OUTPUT_FILE = OUTPUT_DIR / "全年代統合_Kin換算表.csv"

# 出力ディレクトリが存在しない場合は作成
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def get_days_in_month(year, month):
    """指定された年月の日数を返す"""
    return calendar.monthrange(year, month)[1]

def process_year_csv(year):
    """
    指定された年のCSVファイルを読み込み、データを返す

    Returns:
        list: [(年, 月, 日, Kin番号), ...] の形式のリスト
    """
    # フォルダ名のパターンを探す
    folder_pattern = f"{year}年_"
    folders = [f for f in os.listdir(BASE_DIR) if f.startswith(folder_pattern) and os.path.isdir(BASE_DIR / f)]

    if not folders:
        print(f"警告: {year}年のフォルダが見つかりません")
        return []

    folder_name = folders[0]
    csv_file = BASE_DIR / folder_name / f"{year}年_Kin換算表.csv"

    if not csv_file.exists():
        print(f"警告: {csv_file} が見つかりません")
        return []

    data = []

    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)  # ヘッダー行をスキップ

            # ヘッダーから月の順番を確認（1月,2月,...,12月）
            # ヘッダー形式: "日,1月,2月,3月,4月,5月,6月,7月,8月,9月,10月,11月,12月"
            months = header[1:]  # "日"を除く

            # 各行を処理
            for row in reader:
                if not row or len(row) < 2:  # 空行または不完全な行をスキップ
                    continue

                day = int(row[0])  # 日

                # 各月のKin番号を処理（最大12ヶ月まで）
                for month_idx in range(1, 13):  # 1月から12月まで
                    if month_idx >= len(row):  # 列が足りない場合はスキップ
                        break

                    kin_value = row[month_idx]
                    if not kin_value.strip():  # 空のセルをスキップ
                        continue

                    # その月に存在する日かチェック
                    max_day = get_days_in_month(year, month_idx)
                    if day > max_day:
                        continue

                    try:
                        kin_number = int(kin_value)
                        data.append((year, month_idx, day, kin_number))
                    except ValueError:
                        print(f"警告: 無効なKin番号 '{kin_value}' at {year}/{month_idx}/{day}")
                        continue

        print(f"{year}年: {len(data)}件のデータを処理しました")

    except Exception as e:
        print(f"エラー: {csv_file} の処理中にエラーが発生しました: {e}")
        return []

    return data

def main():
    """メイン処理"""
    print("=" * 60)
    print("マヤ暦表統合スクリプト開始")
    print("=" * 60)

    all_data = []

    # 1962年から2013年まで処理
    for year in range(1962, 2014):
        year_data = process_year_csv(year)
        all_data.extend(year_data)

    # データを年月日順にソート
    all_data.sort(key=lambda x: (x[0], x[1], x[2]))

    # CSVファイルに書き込み
    print(f"\n統合CSVファイルを作成中: {OUTPUT_FILE}")

    with open(OUTPUT_FILE, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)

        # ヘッダー行
        writer.writerow(['年', '月', '日', 'Kin番号'])

        # データ行
        for row in all_data:
            writer.writerow(row)

    # 統計情報を出力
    print("\n" + "=" * 60)
    print("統合完了！")
    print("=" * 60)
    print(f"出力ファイル: {OUTPUT_FILE}")
    print(f"総行数: {len(all_data) + 1}行（ヘッダー含む）")
    print(f"データ行数: {len(all_data)}行")

    if all_data:
        first_date = all_data[0]
        last_date = all_data[-1]
        print(f"データ範囲: {first_date[0]}/{first_date[1]}/{first_date[2]} (Kin {first_date[3]}) ～ {last_date[0]}/{last_date[1]}/{last_date[2]} (Kin {last_date[3]})")

        # 年ごとのデータ数を確認
        year_counts = {}
        for year, month, day, kin in all_data:
            year_counts[year] = year_counts.get(year, 0) + 1

        print(f"\n年数: {len(year_counts)}年分")
        print(f"対象年: {min(year_counts.keys())}年 ～ {max(year_counts.keys())}年")

        # 異常なデータがないかチェック
        print("\n各年のデータ数:")
        for year in sorted(year_counts.keys()):
            expected_days = 366 if calendar.isleap(year) else 365
            actual_days = year_counts[year]
            status = "OK" if actual_days == expected_days else f"注意 (期待値: {expected_days})"
            print(f"  {year}年: {actual_days}日 {status}")

    print("\n処理完了！")

if __name__ == "__main__":
    main()
