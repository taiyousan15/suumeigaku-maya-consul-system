#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統合CSVファイルの欠損データをチェックするスクリプト
"""

import csv
import calendar
from pathlib import Path
from datetime import date, timedelta

# 統合CSVファイルのパス
CSV_FILE = Path("/Users/matsumototoshihiko/div/算命学とマヤ暦コンサルシステム/マヤ暦表/マヤ暦表すべて換算表/全年代統合_Kin換算表.csv")

def check_missing_dates():
    """統合CSVファイル内の欠損日付をチェック"""

    # CSVファイルからデータを読み込む
    existing_dates = set()

    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            year = int(row['年'])
            month = int(row['月'])
            day = int(row['日'])
            existing_dates.add((year, month, day))

    print("=" * 60)
    print("欠損データチェック")
    print("=" * 60)

    missing_count = 0

    # 1962年から2013年まで各日をチェック
    for year in range(1962, 2014):
        missing_days = []

        for month in range(1, 13):
            days_in_month = calendar.monthrange(year, month)[1]

            for day in range(1, days_in_month + 1):
                if (year, month, day) not in existing_dates:
                    missing_days.append(f"{year}/{month}/{day}")
                    missing_count += 1

        if missing_days:
            print(f"\n{year}年 ({len(missing_days)}日欠損):")
            for missing_day in missing_days[:10]:  # 最初の10個のみ表示
                print(f"  - {missing_day}")
            if len(missing_days) > 10:
                print(f"  ... 他 {len(missing_days) - 10}日")

    print("\n" + "=" * 60)
    print(f"総欠損日数: {missing_count}日")
    print("=" * 60)

if __name__ == "__main__":
    check_missing_dates()
