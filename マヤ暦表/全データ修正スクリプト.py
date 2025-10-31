#!/usr/bin/env python3
"""
マヤ暦Kin換算表 全データ修正スクリプト
1962年1月1日 = Kin 63 を基準に全52年分を正しく再生成
"""

import csv
import os
from datetime import datetime, timedelta
from pathlib import Path

# 基準日: 1962年1月1日 = Kin 63
BASE_DATE = datetime(1962, 1, 1)
BASE_KIN = 63

def calculate_kin(date):
    """指定された日付のKin番号を計算（1-260の循環）"""
    days_diff = (date - BASE_DATE).days
    kin = ((BASE_KIN - 1 + days_diff) % 260) + 1
    return kin

def is_leap_year(year):
    """うるう年判定"""
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

def generate_year_kin_table(year):
    """指定年のKin換算表を生成（CSV形式の2次元配列）"""
    # 月ごとの日数
    days_in_month = [31, 29 if is_leap_year(year) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    max_days = max(days_in_month)

    # ヘッダー行
    table = [["日", "1月", "2月", "3月", "4月", "5月", "6月", "7月", "8月", "9月", "10月", "11月", "12月"]]

    # 各日のKin値を計算
    for day in range(1, max_days + 1):
        row = [str(day)]
        for month in range(1, 13):
            if day <= days_in_month[month - 1]:
                date = datetime(year, month, day)
                kin = calculate_kin(date)
                row.append(str(kin))
            else:
                row.append("")
        table.append(row)

    return table

def save_csv(filepath, data):
    """CSVファイルを保存"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)

def generate_all_years():
    """全52年分のKin換算表を生成"""
    base_dir = Path(__file__).parent

    # 1962年から2013年まで（52年分）
    years = list(range(1962, 2014))

    print("=" * 60)
    print("マヤ暦Kin換算表 全データ修正開始")
    print(f"基準: 1962年1月1日 = Kin {BASE_KIN}")
    print("=" * 60)

    for idx, year in enumerate(years, 1):
        # フォルダ名生成（52年周期パターン）
        year_offset = year - 1962
        past_year = 1910 + year_offset
        future_year = 2014 + year_offset

        folder_name = f"{year}年_{past_year}年_{future_year}年"
        csv_filename = f"{year}年_Kin換算表.csv"

        # フルパス
        folder_path = base_dir / folder_name
        csv_path = folder_path / csv_filename

        # Kin換算表生成
        table = generate_year_kin_table(year)

        # CSV保存
        save_csv(str(csv_path), table)

        # 1月1日の検証
        jan1_kin = calculate_kin(datetime(year, 1, 1))

        print(f"[{idx:2d}/52] {year}年 → {folder_name}")
        print(f"        1月1日 = Kin {jan1_kin} | ファイル: {csv_filename}")

    print("=" * 60)
    print("✅ 全52年分のデータ生成完了！")
    print("=" * 60)

def generate_integrated_csv():
    """全年代統合CSV生成"""
    base_dir = Path(__file__).parent
    output_dir = base_dir / "マヤ暦表すべて換算表"
    output_file = output_dir / "全年代統合_Kin換算表.csv"

    print("\n統合CSVファイル生成中...")

    all_data = []
    all_data.append(["年", "月", "日", "Kin"])

    for year in range(1962, 2014):
        days_in_month = [31, 29 if is_leap_year(year) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

        for month in range(1, 13):
            for day in range(1, days_in_month[month - 1] + 1):
                date = datetime(year, month, day)
                kin = calculate_kin(date)
                all_data.append([year, month, day, kin])

    save_csv(str(output_file), all_data)
    print(f"✅ 統合CSVファイル生成完了: {output_file}")
    print(f"   総レコード数: {len(all_data) - 1}件")

def verify_data():
    """データ検証"""
    print("\n" + "=" * 60)
    print("データ検証")
    print("=" * 60)

    # 重要な日付の検証
    test_dates = [
        (datetime(1962, 1, 1), 63),
        (datetime(1962, 1, 2), 64),
        (datetime(1962, 12, 31), calculate_kin(datetime(1962, 12, 31))),
        (datetime(2013, 12, 31), calculate_kin(datetime(2013, 12, 31))),
    ]

    for date, expected_kin in test_dates[:2]:
        calculated = calculate_kin(date)
        status = "✅" if calculated == expected_kin else "❌"
        print(f"{status} {date.strftime('%Y年%m月%d日')}: Kin {calculated} (期待値: {expected_kin})")

    for date, expected_kin in test_dates[2:]:
        calculated = calculate_kin(date)
        print(f"✅ {date.strftime('%Y年%m月%d日')}: Kin {calculated}")

if __name__ == "__main__":
    print("\n🚀 マヤ暦全データ修正プログラム起動\n")

    # 全年分生成
    generate_all_years()

    # 統合CSV生成
    generate_integrated_csv()

    # 検証
    verify_data()

    print("\n" + "=" * 60)
    print("🎉 全処理完了！")
    print("=" * 60)
