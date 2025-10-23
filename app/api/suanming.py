"""
算命学命式計算モジュール
仕様書: 算命学命式計算アルゴリズム仕様.md
ナレッジベース: suanming_knowledge.yaml
"""

import yaml
from datetime import datetime
from typing import Dict, Tuple, List
from pathlib import Path


class SuanmingCalculator:
    """算命学命式計算クラス"""

    def __init__(self, knowledge_path: str = None):
        """
        初期化

        Args:
            knowledge_path: YAMLナレッジベースのパス（省略時は同ディレクトリから読み込み）
        """
        if knowledge_path is None:
            knowledge_path = Path(__file__).parent / "suanming_knowledge.yaml"

        with open(knowledge_path, 'r', encoding='utf-8') as f:
            self.knowledge = yaml.safe_load(f)

        # 定数の取得
        self.TENKAN = self.knowledge['constants']['tenkan']
        self.CHISHI = self.knowledge['constants']['chishi']
        self.TENKAN_TO_ELEMENT = self.knowledge['constants']['tenkan_to_element']
        self.TENKAN_SCORE = self.knowledge['constants']['tenkan_score']

        # 参照テーブルの取得
        self.GOKO_TON = self.knowledge['lookup_tables']['goko_ton']
        self.GOSO_TON = self.knowledge['lookup_tables']['goso_ton']
        self.MONTH_SHI_ORDER = self.knowledge['lookup_tables']['month_shi_order']
        self.HOUR_SHI_ORDER = self.knowledge['lookup_tables']['hour_shi_order']
        self.ZOKKAN = self.knowledge['lookup_tables']['zokkan']
        self.MONTH_BASE = self.knowledge['lookup_tables']['month_base']
        self.CENTURY_CONSTANT = self.knowledge['lookup_tables']['century_constant']
        self.SHOSHO_RELATION = self.knowledge['lookup_tables']['shosho_relation']
        self.SOKOKU_RELATION = self.knowledge['lookup_tables']['sokoku_relation']

        # 六十干支表の生成（日柱計算用）
        self.ROKUJIKKANSHI = self._generate_rokujikkanshi()

    def _generate_rokujikkanshi(self) -> List[Tuple[str, str]]:
        """
        六十干支表を生成

        Returns:
            六十干支のリスト [(干, 支), ...]
        """
        rokujikkanshi = []
        for i in range(60):
            gan = self.TENKAN[i % 10]
            shi = self.CHISHI[i % 12]
            rokujikkanshi.append((gan, shi))
        return rokujikkanshi

    def is_after_risshun(self, year: int, month: int, day: int) -> bool:
        """
        立春以降かどうかを判定（簡易版）

        Args:
            year: 年
            month: 月
            day: 日

        Returns:
            立春以降ならTrue

        Note:
            簡易実装として2月4日を基準とする
            実運用では天文計算または立春日時テーブルが必要
        """
        if month < 2:
            return False
        elif month > 2:
            return True
        else:  # month == 2
            return day >= 4

    def calculate_year_pillar(self, year: int, month: int, day: int) -> Tuple[str, str]:
        """
        年柱（年干・年支）を計算

        Args:
            year: 西暦年
            month: 月
            day: 日

        Returns:
            (年干, 年支)
        """
        # 立春以前は前年扱い
        if not self.is_after_risshun(year, month, day):
            year -= 1

        gan_index = year % 10
        shi_index = year % 12

        return self.TENKAN[gan_index], self.CHISHI[shi_index]

    def _get_sekki_month_index(self, month: int, day: int) -> int:
        """
        節気から月支のインデックスを取得（簡易版）

        Args:
            month: 月
            day: 日

        Returns:
            月支インデックス（0-11）

        Note:
            簡易実装として月の中旬（6日前後）を節気の境目とする
            実運用では正確な節気日時テーブルが必要
        """
        # 節気の境目を簡易的に月の6日とする
        # 立春（2月）→寅月、啓蟄（3月）→卯月...

        # 2月4日以前は前月（丑月）
        if month == 2 and day < 4:
            return 11  # 丑月（12月）

        # 各月の6日以前は前月扱い
        if day < 6:
            month -= 1
            if month < 1:
                month = 12

        # 月から月支インデックスを算出
        # 2月（立春）→寅月（index 0）
        # 3月（啓蟄）→卯月（index 1）
        # ...
        # 1月（小寒）→丑月（index 11）

        if month >= 2:
            return month - 2
        else:  # month == 1
            return 11

    def calculate_month_pillar(
        self,
        year: int,
        month: int,
        day: int,
        year_gan: str
    ) -> Tuple[str, str]:
        """
        月柱（月干・月支）を計算

        Args:
            year: 西暦年
            month: 月
            day: 日
            year_gan: 年干

        Returns:
            (月干, 月支)
        """
        # 月支の決定
        month_shi_index = self._get_sekki_month_index(month, day)
        month_shi = self.MONTH_SHI_ORDER[month_shi_index]

        # 五虎遁：年干から寅月の月干を決定
        base_gan = self.GOKO_TON[year_gan]

        # 寅月（index 0）から現在月まで天干を順行
        base_gan_index = self.TENKAN.index(base_gan)
        month_gan_index = (base_gan_index + month_shi_index) % 10
        month_gan = self.TENKAN[month_gan_index]

        return month_gan, month_shi

    def calculate_day_pillar(self, year: int, month: int, day: int) -> Tuple[str, str]:
        """
        日柱（日干・日支）を計算（高氏日柱公式）

        Args:
            year: 西暦年
            month: 月
            day: 日

        Returns:
            (日干, 日支)
        """
        # 世紀定数の取得
        century = (year // 100) * 100
        century_constant = self.CENTURY_CONSTANT.get(century, 0)

        # 高氏日柱公式
        year_last_two = year % 100
        s = year_last_two - 1
        u = s % 4
        month_base = self.MONTH_BASE[month]

        r = s * 4 * 6 + 5 * (s * 4 * 3 + u) + month_base + day + century_constant
        kanshi_number = r % 60

        # 六十干支表から干支を取得
        day_gan, day_shi = self.ROKUJIKKANSHI[kanshi_number]

        return day_gan, day_shi

    def _get_hour_shi_index(self, hour: int) -> int:
        """
        時刻から時支のインデックスを取得

        Args:
            hour: 時（0-23）

        Returns:
            時支インデックス（0-11）
        """
        # 時支の対応（2時間ごと）
        # 23-1時 → 子（index 0）
        # 1-3時 → 丑（index 1）
        # ...

        if hour == 23:
            return 0  # 子
        else:
            return (hour + 1) // 2

    def calculate_hour_pillar(
        self,
        hour: int,
        minute: int,
        day_gan: str
    ) -> Tuple[str, str]:
        """
        時柱（時干・時支）を計算

        Args:
            hour: 時（0-23）
            minute: 分（0-59）
            day_gan: 日干

        Returns:
            (時干, 時支)
        """
        # 時支の決定
        hour_shi_index = self._get_hour_shi_index(hour)
        hour_shi = self.HOUR_SHI_ORDER[hour_shi_index]

        # 五鼠遁：日干から子時の時干を決定
        base_gan = self.GOSO_TON[day_gan]

        # 子時（index 0）から現在時まで天干を順行
        base_gan_index = self.TENKAN.index(base_gan)
        hour_gan_index = (base_gan_index + hour_shi_index) % 10
        hour_gan = self.TENKAN[hour_gan_index]

        return hour_gan, hour_shi

    def calculate_five_elements(
        self,
        year_gan: str,
        month_gan: str,
        day_gan: str,
        hour_gan: str,
        year_shi: str,
        month_shi: str,
        day_shi: str,
        hour_shi: str
    ) -> Dict[str, int]:
        """
        五行配点を計算

        Args:
            year_gan: 年干
            month_gan: 月干
            day_gan: 日干
            hour_gan: 時干
            year_shi: 年支
            month_shi: 月支
            day_shi: 日支
            hour_shi: 時支

        Returns:
            五行配点の辞書 {"木": score, "火": score, ...}
        """
        five_elements = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}

        # 天干加算（36点固定）
        for gan in [year_gan, month_gan, day_gan, hour_gan]:
            elem = self.TENKAN_TO_ELEMENT[gan]
            five_elements[elem] += self.TENKAN_SCORE

        # 地支加算（蔵干比率100点）
        for shi in [year_shi, month_shi, day_shi, hour_shi]:
            for zokkan_item in self.ZOKKAN[shi]:
                gan = zokkan_item['gan']
                ratio = zokkan_item['ratio']
                elem = self.TENKAN_TO_ELEMENT[gan]
                five_elements[elem] += ratio

        return five_elements

    def select_guardian_gods(
        self,
        five_elements_score: Dict[str, int]
    ) -> Dict[str, List[str]]:
        """
        守護神・忌神を選定

        Args:
            five_elements_score: 五行配点の辞書

        Returns:
            {
                "guardian_gods": [守護神リスト],
                "taboo_elements": [忌神リスト],
                "deficient": [不足五行リスト],
                "excess": [過剰五行リスト]
            }
        """
        # 最小値・最大値の取得
        min_score = min(five_elements_score.values())
        max_score = max(five_elements_score.values())

        # 不足五行・過剰五行の抽出
        deficient = [elem for elem, score in five_elements_score.items() if score == min_score]
        excess = [elem for elem, score in five_elements_score.items() if score == max_score]

        # 守護神候補
        guardian_gods = []

        # 1. 不足五行を守護神候補に追加（優先度1）
        guardian_gods.extend(deficient)

        # 2. 過剰五行を制御する五行を守護神候補に追加（優先度3）
        for excess_elem in excess:
            # 相剋関係を逆引き：過剰五行を制する五行を探す
            for control_elem, controlled_elem in self.SOKOKU_RELATION.items():
                if controlled_elem == excess_elem and control_elem not in guardian_gods:
                    guardian_gods.append(control_elem)

        # 3. 不足五行を生じる五行を守護神候補に追加（優先度4）
        for deficient_elem in deficient:
            # 相生関係を逆引き：不足五行を生じる五行を探す
            for nourish_elem, nourished_elem in self.SHOSHO_RELATION.items():
                if nourished_elem == deficient_elem and nourish_elem not in guardian_gods:
                    guardian_gods.append(nourish_elem)

        # 忌神は過剰五行
        taboo_elements = excess

        return {
            "guardian_gods": guardian_gods,
            "taboo_elements": taboo_elements,
            "deficient": deficient,
            "excess": excess
        }

    def analyze(
        self,
        birthdate: str,
        birthtime: str
    ) -> Dict:
        """
        生年月日・時刻から命式を計算

        Args:
            birthdate: 生年月日（YYYY-MM-DD形式）
            birthtime: 生時刻（HH:MM形式）

        Returns:
            命式計算結果の辞書
        """
        # 日時のパース
        dt = datetime.strptime(f"{birthdate} {birthtime}", "%Y-%m-%d %H:%M")
        year, month, day = dt.year, dt.month, dt.day
        hour, minute = dt.hour, dt.minute

        # 四柱の計算
        year_gan, year_shi = self.calculate_year_pillar(year, month, day)
        month_gan, month_shi = self.calculate_month_pillar(year, month, day, year_gan)
        day_gan, day_shi = self.calculate_day_pillar(year, month, day)
        hour_gan, hour_shi = self.calculate_hour_pillar(hour, minute, day_gan)

        # 五行配点の計算
        five_elements_score = self.calculate_five_elements(
            year_gan, month_gan, day_gan, hour_gan,
            year_shi, month_shi, day_shi, hour_shi
        )

        # 守護神の選定
        guardian_result = self.select_guardian_gods(five_elements_score)

        return {
            "year_gan": year_gan,
            "year_shi": year_shi,
            "month_gan": month_gan,
            "month_shi": month_shi,
            "day_gan": day_gan,
            "day_shi": day_shi,
            "hour_gan": hour_gan,
            "hour_shi": hour_shi,
            "five_elements_score": five_elements_score,
            "guardian_gods": guardian_result["guardian_gods"],
            "taboo_elements": guardian_result["taboo_elements"],
            "deficient": guardian_result["deficient"],
            "excess": guardian_result["excess"]
        }


# モジュールレベルの便利関数
def analyze_suanming(birthdate: str, birthtime: str) -> Dict:
    """
    生年月日・時刻から算命学命式を計算

    Args:
        birthdate: 生年月日（YYYY-MM-DD形式）
        birthtime: 生時刻（HH:MM形式）

    Returns:
        命式計算結果の辞書
    """
    calculator = SuanmingCalculator()
    return calculator.analyze(birthdate, birthtime)
