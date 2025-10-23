"""
マヤ暦計算モジュール（ツォルキン260日周期）

マヤ暦のKin番号、太陽の紋章、銀河の音、ウェイブスペルを計算します。
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


def calculate_kin(birthdate: str) -> int:
    """
    生年月日からKin番号を計算

    Args:
        birthdate: 生年月日（YYYY-MM-DD形式）

    Returns:
        Kin番号（1-260）
    """
    birth = datetime.strptime(birthdate, "%Y-%m-%d").date()

    # 基準日からの経過日数
    days_diff = (birth - MAYA_BASE_DATE).days

    # 260日周期でKin番号を計算（1-260の範囲）
    kin = (days_diff % 260) + 1

    # 負の数になる場合の調整
    if kin <= 0:
        kin += 260

    return kin


def get_solar_seal(kin: int) -> str:
    """
    Kin番号から太陽の紋章を取得

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

    Args:
        kin: Kin番号（1-260）

    Returns:
        ウェイブスペル
    """
    # ウェイブスペルは13日ごとに変わる（20ウェイブスペル × 13日 = 260日）
    wavespell_index = ((kin - 1) // 13) % 20
    return WAVESPELLS[wavespell_index]


def analyze_maya(birthdate: str) -> Dict:
    """
    マヤ暦の総合分析

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
        "wavespell": wavespell
    }


if __name__ == "__main__":
    # テスト実行
    test_dates = ["1992-07-15", "2020-02-05", "2000-01-01"]

    for test_date in test_dates:
        result = analyze_maya(test_date)
        print(f"生年月日: {test_date}")
        print(f"  Kin: {result['kin']}")
        print(f"  太陽の紋章: {result['solar_seal']}")
        print(f"  銀河の音: {result['tone']}")
        print(f"  ウェイブスペル: {result['wavespell']}")
        print()
