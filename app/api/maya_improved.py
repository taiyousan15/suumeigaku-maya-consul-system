"""
マヤ暦計算モジュール（改良版）
仕様書: マヤ暦計算アルゴリズム仕様.md に準拠

Dreamspell（13の月暦）方式で実装
- 基準日: 1987年7月26日 = Kin1
- 閏年の2月29日を除外して計算
- ユリウス通日（JDN）を介した正確な換算
"""

from datetime import datetime, date
from typing import Dict

# マヤ暦の基準日（グレゴリオ暦 1987年7月26日 = Kin 1）
MAYA_BASE_DATE = date(1987, 7, 26)

# 太陽の紋章（20種類）
SOLAR_SEALS = [
    "赤い竜", "白い風", "青い夜", "黄色い種", "赤い蛇",
    "白い世界の橋渡し", "青い手", "黄色い星", "赤い月", "白い犬",
    "青い猿", "黄色い人", "赤い空歩く人", "白い魔法使い", "青い鷲",
    "黄色い戦士", "赤い地球", "白い鏡", "青い嵐", "黄色い太陽"
]

# ウェイブスペル（20種類、太陽の紋章と同じ）
WAVESPELLS = SOLAR_SEALS

# 銀河の音（13種類）
GALACTIC_TONES = list(range(1, 14))


def is_leap_year(year: int) -> bool:
    """
    グレゴリオ暦の閏年判定

    Args:
        year: 西暦年

    Returns:
        閏年ならTrue
    """
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)


def count_leap_days_between(start_date: date, end_date: date) -> int:
    """
    2つの日付間の2月29日の回数を数える（Dreamspell方式）

    Args:
        start_date: 開始日
        end_date: 終了日

    Returns:
        2月29日の回数
    """
    if start_date > end_date:
        start_date, end_date = end_date, start_date

    leap_days = 0
    for year in range(start_date.year, end_date.year + 1):
        if is_leap_year(year):
            feb29 = date(year, 2, 29)
            if start_date <= feb29 <= end_date:
                leap_days += 1

    return leap_days


def calculate_kin(birthdate: str) -> int:
    """
    生年月日からKin番号を計算（Dreamspell方式）

    Dreamspellでは2月29日を「0.0 Hunab Ku」として除外するため、
    通算日数から閏日を引いた値で計算する。

    Args:
        birthdate: 生年月日（YYYY-MM-DD形式）

    Returns:
        Kin番号（1-260）
    """
    birth = datetime.strptime(birthdate, "%Y-%m-%d").date()

    # 基準日からの経過日数（暦日）
    days_diff = (birth - MAYA_BASE_DATE).days

    # Dreamspell方式: 2月29日を除外
    # 基準日と生年月日の間にある2月29日の回数を数える
    if days_diff >= 0:
        leap_days = count_leap_days_between(MAYA_BASE_DATE, birth)
    else:
        leap_days = -count_leap_days_between(birth, MAYA_BASE_DATE)

    # 閏日を除外した実効日数
    effective_days = days_diff - leap_days

    # 260日周期でKin番号を計算（1-260の範囲）
    # 基準日（effective_days=0）がKin1になるように調整
    kin = (effective_days % 260) + 1
    if kin > 260:
        kin -= 260

    return kin


def get_solar_seal(kin: int) -> str:
    """
    Kin番号から太陽の紋章を取得

    計算式: (Kin - 1) mod 20

    Args:
        kin: Kin番号（1-260）

    Returns:
        太陽の紋章
    """
    index = (kin - 1) % 20
    return SOLAR_SEALS[index]


def get_galactic_tone(kin: int) -> int:
    """
    Kin番号から銀河の音を取得

    計算式: (Kin - 1) mod 13 + 1

    Args:
        kin: Kin番号（1-260）

    Returns:
        銀河の音（1-13）
    """
    tone = ((kin - 1) % 13) + 1
    return tone


def get_wavespell(kin: int) -> str:
    """
    Kin番号からウェイブスペルを取得

    ウェイブスペルは13日ごとに変わる（20ウェイブスペル × 13日 = 260日）

    Args:
        kin: Kin番号（1-260）

    Returns:
        ウェイブスペル
    """
    # ウェイブスペルのインデックス（0-19）
    wavespell_index = ((kin - 1) // 13) % 20
    return WAVESPELLS[wavespell_index]


def analyze_maya(birthdate: str) -> Dict:
    """
    マヤ暦の総合分析（Dreamspell方式）

    Args:
        birthdate: 生年月日（YYYY-MM-DD形式）

    Returns:
        マヤ暦の分析結果
    """
    # Kin番号の計算
    kin = calculate_kin(birthdate)

    # 各要素の取得
    solar_seal = get_solar_seal(kin)
    tone = get_galactic_tone(kin)
    wavespell = get_wavespell(kin)

    return {
        "kin": kin,
        "solar_seal": solar_seal,
        "tone": tone,
        "wavespell": wavespell,
        "system": "Dreamspell (13 Moon Calendar)"
    }


def analyze_maya_classical(birthdate: str) -> Dict:
    """
    古典マヤ暦の分析（GMT相関方式）

    参考: GMT相関ではロングカウント起点（13.0.0.0.0）を
    JDN=584283（紀元前3114年8月11日）とする

    Args:
        birthdate: 生年月日（YYYY-MM-DD形式）

    Returns:
        古典マヤ暦の分析結果
    """
    # JDN計算（簡易版）
    # 本格実装では天文学的ユリウス通日計算が必要
    birth = datetime.strptime(birthdate, "%Y-%m-%d").date()

    # GMT相関の起点（紀元前3114年8月11日）からの通算日数
    # 簡易計算: 現代の日付から基準点までの日数
    # 注: 実運用では正確なJDN計算ライブラリを使用すべき
    gmt_base_jdn = 584283
    birth_jdn = date_to_jdn(birth)

    days_from_gmt = birth_jdn - gmt_base_jdn

    # ツォルキン計算（260日周期）
    # 起点からの日数を260で割った余り + 1でKin番号を算出
    kin_classical = (days_from_gmt % 260) + 1
    if kin_classical > 260:
        kin_classical -= 260

    return {
        "kin": kin_classical,
        "solar_seal": get_solar_seal(kin_classical),
        "tone": get_galactic_tone(kin_classical),
        "wavespell": get_wavespell(kin_classical),
        "system": "Classical Maya (GMT Correlation)"
    }


def date_to_jdn(d: date) -> int:
    """
    グレゴリオ暦の日付をユリウス通日（JDN）に変換

    JDN = 紀元前4713年1月1日12時（グリニッジ）からの連続日数

    Args:
        d: 日付

    Returns:
        ユリウス通日
    """
    a = (14 - d.month) // 12
    y = d.year + 4800 - a
    m = d.month + 12 * a - 3

    jdn = d.day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045

    return jdn


if __name__ == "__main__":
    # テスト実行
    test_dates = ["1992-07-15", "2020-02-05", "2000-01-01", "1987-07-26"]

    print("=== Dreamspell（13の月暦）方式 ===")
    for test_date in test_dates:
        result = analyze_maya(test_date)
        print(f"生年月日: {test_date}")
        print(f"  Kin: {result['kin']}")
        print(f"  太陽の紋章: {result['solar_seal']}")
        print(f"  銀河の音: {result['tone']}")
        print(f"  ウェイブスペル: {result['wavespell']}")
        print()

    print("\n=== 古典マヤ暦（GMT相関）方式 ===")
    for test_date in test_dates:
        result = analyze_maya_classical(test_date)
        print(f"生年月日: {test_date}")
        print(f"  Kin: {result['kin']}")
        print(f"  太陽の紋章: {result['solar_seal']}")
        print(f"  銀河の音: {result['tone']}")
        print(f"  ウェイブスペル: {result['wavespell']}")
        print()
