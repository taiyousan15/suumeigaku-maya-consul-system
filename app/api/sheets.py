"""
Google Sheets連携モジュール

データベース代替としてGoogle Sheetsを使用する。
- Users: ユーザー管理
- CalcLogs: 計算履歴
- Knowledge: 知識ベース（設定・辞書・重み）
"""

import os
import json
import base64
from datetime import datetime
from typing import List, Dict, Any, Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class SheetsClient:
    """Google Sheets APIクライアント"""

    def __init__(self):
        """初期化"""
        # 環境変数からサービスアカウント情報を取得
        service_account_json_base64 = os.getenv('GOOGLE_SERVICE_ACCOUNT_JSON_BASE64')
        spreadsheet_id = os.getenv('SHEETS_SPREADSHEET_ID')

        if not service_account_json_base64:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON_BASE64 environment variable is required")
        if not spreadsheet_id:
            raise ValueError("SHEETS_SPREADSHEET_ID environment variable is required")

        # Base64デコード
        service_account_json = base64.b64decode(service_account_json_base64).decode('utf-8')
        service_account_info = json.loads(service_account_json)

        # 認証情報を作成
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )

        # Sheets APIクライアントを構築
        self.service = build('sheets', 'v4', credentials=credentials)
        self.spreadsheet_id = spreadsheet_id

    def _get_range(self, sheet_name: str, range_notation: str = '') -> str:
        """シート範囲を取得"""
        if range_notation:
            return f"{sheet_name}!{range_notation}"
        return sheet_name

    def read_values(self, sheet_name: str, range_notation: str = '') -> List[List[Any]]:
        """値を読み取る"""
        try:
            range_name = self._get_range(sheet_name, range_notation)
            result = self.service.spreadsheets().values().get(
                spreadsheetId=self.spreadsheet_id,
                range=range_name
            ).execute()
            return result.get('values', [])
        except HttpError as error:
            print(f"Error reading from sheet: {error}")
            return []

    def write_values(self, sheet_name: str, values: List[List[Any]], range_notation: str = '') -> bool:
        """値を書き込む"""
        try:
            range_name = self._get_range(sheet_name, range_notation)
            body = {'values': values}
            self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            return True
        except HttpError as error:
            print(f"Error writing to sheet: {error}")
            return False

    def append_values(self, sheet_name: str, values: List[List[Any]]) -> bool:
        """値を追加"""
        try:
            body = {'values': values}
            self.service.spreadsheets().values().append(
                spreadsheetId=self.spreadsheet_id,
                range=sheet_name,
                valueInputOption='RAW',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            return True
        except HttpError as error:
            print(f"Error appending to sheet: {error}")
            return False


class UsersManager:
    """ユーザー管理"""

    def __init__(self, sheets_client: SheetsClient):
        self.client = sheets_client
        self.sheet_name = 'Users'

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """IDでユーザーを取得"""
        rows = self.client.read_values(self.sheet_name)
        if not rows:
            return None

        # ヘッダー行
        headers = rows[0]

        # データ行を検索
        for row in rows[1:]:
            if row and row[0] == user_id:
                return dict(zip(headers, row))

        return None

    def create_user(self, email: str, api_key: str, role: str = 'user', monthly_limit: int = 50) -> str:
        """ユーザーを作成"""
        import uuid
        user_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        values = [[
            user_id,
            email,
            api_key,
            role,
            str(monthly_limit),
            '0',  # used_count
            now,  # created_at
            now   # updated_at
        ]]

        self.client.append_values(self.sheet_name, values)
        return user_id

    def increment_usage(self, user_id: str) -> bool:
        """使用回数をインクリメント"""
        rows = self.client.read_values(self.sheet_name)
        if not rows:
            return False

        headers = rows[0]
        used_count_idx = headers.index('used_count')
        updated_at_idx = headers.index('updated_at')

        for i, row in enumerate(rows[1:], start=2):
            if row and row[0] == user_id:
                current_count = int(row[used_count_idx])
                row[used_count_idx] = str(current_count + 1)
                row[updated_at_idx] = datetime.now().isoformat()

                # 更新
                range_notation = f"A{i}:{chr(65 + len(row) - 1)}{i}"
                return self.client.write_values(self.sheet_name, [row], range_notation)

        return False


class CalcLogsManager:
    """計算履歴管理"""

    def __init__(self, sheets_client: SheetsClient):
        self.client = sheets_client
        self.sheet_name = 'CalcLogs'

    def save_log(self, user_id: str, request_data: Dict[str, Any], result_data: Dict[str, Any]) -> str:
        """ログを保存"""
        import uuid
        log_id = str(uuid.uuid4())
        now = datetime.now().isoformat()

        # カテゴリをCSV形式に変換
        categories = ','.join(request_data.get('categories', []))

        values = [[
            log_id,
            user_id,
            request_data.get('birthdate', ''),
            request_data.get('birth_time', ''),
            request_data.get('birth_place', ''),
            categories,
            request_data.get('free_text', ''),
            json.dumps(result_data.get('suanming', {}), ensure_ascii=False),
            json.dumps(result_data.get('maya', {}), ensure_ascii=False),
            json.dumps(result_data.get('scores', {}), ensure_ascii=False),
            json.dumps(result_data.get('llm', {}), ensure_ascii=False),
            now
        ]]

        self.client.append_values(self.sheet_name, values)
        return log_id

    def get_logs(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """ログを取得"""
        rows = self.client.read_values(self.sheet_name)
        if not rows:
            return []

        headers = rows[0]
        logs = []

        # ユーザーのログのみフィルタリング
        for row in rows[1:]:
            if row and len(row) >= 2 and row[1] == user_id:
                log = dict(zip(headers, row))

                # JSON文字列をパース
                try:
                    log['suanming_json'] = json.loads(log.get('suanming_json', '{}'))
                    log['maya_json'] = json.loads(log.get('maya_json', '{}'))
                    log['scores_json'] = json.loads(log.get('scores_json', '{}'))
                    log['llm_meta_json'] = json.loads(log.get('llm_meta_json', '{}'))
                except json.JSONDecodeError:
                    pass

                logs.append(log)

        # 作成日時でソート（降順）
        logs.sort(key=lambda x: x.get('created_at', ''), reverse=True)

        return logs[:limit]


class KnowledgeManager:
    """知識ベース管理"""

    def __init__(self, sheets_client: SheetsClient):
        self.client = sheets_client
        self.sheet_name = 'Knowledge'

    def get_value(self, key: str) -> Optional[Any]:
        """値を取得"""
        rows = self.client.read_values(self.sheet_name)
        if not rows:
            return None

        for row in rows[1:]:
            if row and row[0] == key:
                try:
                    return json.loads(row[2])  # value列
                except json.JSONDecodeError:
                    return row[2]

        return None

    def set_value(self, key: str, value_type: str, value: Any) -> bool:
        """値を設定"""
        rows = self.client.read_values(self.sheet_name)
        now = datetime.now().isoformat()

        # 既存のキーを検索
        if rows:
            headers = rows[0]
            for i, row in enumerate(rows[1:], start=2):
                if row and row[0] == key:
                    # 更新
                    new_row = [key, value_type, json.dumps(value, ensure_ascii=False), now]
                    range_notation = f"A{i}:D{i}"
                    return self.client.write_values(self.sheet_name, [new_row], range_notation)

        # 新規追加
        values = [[key, value_type, json.dumps(value, ensure_ascii=False), now]]
        return self.client.append_values(self.sheet_name, values)

    def get_weights(self) -> Dict[str, float]:
        """重み設定を取得"""
        weights = self.get_value('weights')
        if weights:
            return weights

        # デフォルト値
        return {
            'w_suan': 0.6,
            'w_maya': 0.4
        }

    def set_weights(self, w_suan: float, w_maya: float) -> bool:
        """重み設定を保存"""
        weights = {
            'w_suan': w_suan,
            'w_maya': w_maya
        }
        return self.set_value('weights', 'weighing', weights)


# シングルトンインスタンス（オプション）
_sheets_client = None
_users_manager = None
_calc_logs_manager = None
_knowledge_manager = None


def get_sheets_client() -> SheetsClient:
    """Sheetsクライアントを取得"""
    global _sheets_client
    if _sheets_client is None:
        _sheets_client = SheetsClient()
    return _sheets_client


def get_users_manager() -> UsersManager:
    """ユーザーマネージャーを取得"""
    global _users_manager
    if _users_manager is None:
        _users_manager = UsersManager(get_sheets_client())
    return _users_manager


def get_calc_logs_manager() -> CalcLogsManager:
    """計算ログマネージャーを取得"""
    global _calc_logs_manager
    if _calc_logs_manager is None:
        _calc_logs_manager = CalcLogsManager(get_sheets_client())
    return _calc_logs_manager


def get_knowledge_manager() -> KnowledgeManager:
    """知識ベースマネージャーを取得"""
    global _knowledge_manager
    if _knowledge_manager is None:
        _knowledge_manager = KnowledgeManager(get_sheets_client())
    return _knowledge_manager
