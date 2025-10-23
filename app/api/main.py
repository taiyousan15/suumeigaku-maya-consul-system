"""
Flask API エンドポイント
算命学×マヤ暦コンサルシステムAPI
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from datetime import datetime
import traceback
import uuid
from suanming import SuanmingCalculator
from maya import analyze_maya

app = Flask(__name__)
CORS(app)  # フロントエンドからのアクセスを許可

# 算命学計算インスタンスの初期化
calculator = SuanmingCalculator()


@app.route('/api/v1/health', methods=['GET'])
def health_check():
    """ヘルスチェックエンドポイント"""
    return jsonify({
        "status": "ok",
        "service": "suanming-api",
        "version": "1.0.0"
    }), 200


@app.route('/api/v1/analyze', methods=['POST'])
def analyze():
    """
    算命学×マヤ暦総合分析エンドポイント

    Request Body:
        {
            "birthdate": "YYYY-MM-DD",
            "birth_time": "HH:MM" (optional, default: "12:00"),
            "categories": ["仕事", "恋愛"] (optional),
            "llm_prefs": {
                "temperature": 0.5,
                "intensity": 6
            } (optional)
        }

    Response:
        {
            "request_id": "uuid",
            "ts": "2025-10-23T...",
            "data": {
                "suanming": {...},
                "maya": {...},
                "scores": {...},
                "insights": [...]
            }
        }
    """
    try:
        # リクエストボディの取得
        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "message": "リクエストボディが空です"
            }), 400

        # 入力検証
        birthdate = data.get('birthdate')
        birthtime = data.get('birth_time', '12:00')
        categories = data.get('categories', ['仕事'])
        llm_prefs = data.get('llm_prefs', {})

        if not birthdate:
            return jsonify({
                "status": "error",
                "message": "birthdateは必須です（形式: YYYY-MM-DD）"
            }), 400

        # 日時形式の検証
        try:
            datetime.strptime(birthdate, "%Y-%m-%d")
        except ValueError:
            return jsonify({
                "status": "error",
                "message": "birthdateの形式が不正です（正しい形式: YYYY-MM-DD）"
            }), 400

        try:
            datetime.strptime(birthtime, "%H:%M")
        except ValueError:
            return jsonify({
                "status": "error",
                "message": "birth_timeの形式が不正です（正しい形式: HH:MM）"
            }), 400

        # 算命学命式計算の実行
        suanming_result = calculator.analyze(birthdate, birthtime)

        # マヤ暦計算の実行
        maya_result = analyze_maya(birthdate)

        # 統合スコアの計算
        scores = calculate_scores(suanming_result, maya_result)

        # インサイトの生成
        insights = generate_insights(suanming_result, maya_result, categories)

        # レスポンスの返却
        return jsonify({
            "request_id": str(uuid.uuid4()),
            "ts": datetime.now().isoformat(),
            "data": {
                "suanming": suanming_result,
                "maya": maya_result,
                "scores": scores,
                "insights": insights,
                "llm": {
                    "used_tokens": 0,  # TODO: LLM統合後に実装
                    "temperature": llm_prefs.get('temperature', 0.5),
                    "intensity": llm_prefs.get('intensity', 6)
                }
            }
        }), 200

    except Exception as e:
        # エラーハンドリング
        app.logger.error(f"Error in /api/v1/analyze: {str(e)}")
        app.logger.error(traceback.format_exc())

        return jsonify({
            "status": "error",
            "message": "サーバー内部エラーが発生しました",
            "detail": str(e)
        }), 500


def calculate_scores(suanming_result: dict, maya_result: dict) -> dict:
    """統合スコアの計算"""
    five_elements = suanming_result['five_elements_score']
    total = sum(five_elements.values())
    normalized = {k: v / total for k, v in five_elements.items()}

    kin_norm = maya_result['kin'] / 260
    tone_norm = maya_result['tone'] / 13

    w_suan, w_maya = 0.6, 0.4

    overall = (sum(normalized.values()) / 5) * w_suan + (kin_norm + tone_norm) / 2 * w_maya
    work = normalized.get('木', 0) * 0.4 + normalized.get('金', 0) * 0.3 + tone_norm * 0.3
    love = normalized.get('火', 0) * 0.5 + kin_norm * 0.5
    health = normalized.get('土', 0) * 0.4 + normalized.get('水', 0) * 0.3 + tone_norm * 0.3
    growth = normalized.get('木', 0) * 0.3 + normalized.get('火', 0) * 0.3 + kin_norm * 0.4

    return {
        "overall": round(overall, 2),
        "work": round(work, 2),
        "love": round(love, 2),
        "health": round(health, 2),
        "growth": round(growth, 2)
    }


def generate_insights(suanming_result: dict, maya_result: dict, categories: list) -> list:
    """インサイトの生成"""
    insights = []

    guardian_gods = suanming_result.get('guardian_gods', [])
    if '火' in guardian_gods:
        insights.append({
            "title": "エネルギッシュな活動を",
            "advice": "火のエネルギーを取り入れることで、情熱的な活動が吉となります。"
        })

    if '木' in guardian_gods:
        insights.append({
            "title": "成長と発展の時期",
            "advice": "木のエネルギーは成長を表します。学びに力を入れましょう。"
        })

    if '水' in guardian_gods:
        insights.append({
            "title": "柔軟性を大切に",
            "advice": "水のように柔軟な対応が求められます。"
        })

    solar_seal = maya_result['solar_seal']
    if '赤い' in solar_seal:
        insights.append({
            "title": "行動力を発揮",
            "advice": f"{solar_seal}のエネルギーは、積極的な行動を後押しします。"
        })

    if len(insights) < 3:
        insights.append({
            "title": "バランスを意識",
            "advice": "五行のバランスを整えることで、運気が安定します。"
        })

    return insights[:3]


@app.errorhandler(404)
def not_found(error):
    """404エラーハンドラ"""
    return jsonify({
        "status": "error",
        "message": "指定されたエンドポイントが見つかりません"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """500エラーハンドラ"""
    return jsonify({
        "status": "error",
        "message": "サーバー内部エラーが発生しました"
    }), 500


if __name__ == '__main__':
    # 開発環境での起動
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=True
    )
