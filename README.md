# 算命学×マヤ暦コンサルシステム

生年月日から算命学とマヤ暦に基づいた総合的なアドバイスを提供するWebアプリケーション

## 📊 システム概要

このシステムは、算命学の命式計算（干支・五行配点・守護神選定）とマヤ暦の計算（Kin・紋章・音・ウェイブスペル）を統合し、女性向けの悩み相談（仕事/恋愛/人間関係/健康/運気）に対して再現性のある助言を提供します。

### 主な機能

- 📅 生年月日・出生時刻からの命式計算
- 🔮 算命学の四柱推命（年柱・月柱・日柱・時柱）
- 🌟 マヤ暦のツォルキン計算
- 💡 テーマ別スコア算出（仕事/恋愛/健康/自己成長）
- 🤖 LLMによる結果の整形と提案生成

## 🏗️ アーキテクチャ

```
┌─────────────────┐      HTTPS       ┌──────────────────┐
│   Frontend      │ ◄──────────────► │   Backend API    │
│   (Vercel)      │     REST API     │   (Render)       │
│  React + Vite   │                  │  Python + Flask  │
└─────────────────┘                  └────────┬─────────┘
                                              │
                                              ▼
                                     ┌─────────────────┐
                                     │  Google Sheets  │
                                     │   (Database)    │
                                     └─────────────────┘
```

## 🚀 クイックスタート

### 必要環境

- Node.js 18+
- Python 3.11+
- npm または yarn

### ローカル開発環境のセットアップ

#### 1. リポジトリのクローン

```bash
git clone https://github.com/taiyousan15/suumeigaku-maya-consul-system.git
cd suumeigaku-maya-consul-system
```

#### 2. バックエンドの起動

```bash
cd app/api
pip install -r requirements.txt
python3 main.py
```

→ http://localhost:8080/ で起動

#### 3. フロントエンドの起動

```bash
cd app/frontend
npm install
npm run dev
```

→ http://localhost:3001/ で起動

#### 4. ブラウザでアクセス

http://localhost:3001/ を開いて、生年月日を入力すると分析結果が表示されます。

## 📁 プロジェクト構成

```
.
├── app/
│   ├── api/                          # バックエンドAPI
│   │   ├── main.py                   # Flask APIエントリーポイント
│   │   ├── suanming.py               # 算命学計算エンジン
│   │   ├── maya.py                   # マヤ暦計算エンジン（シンプル版）
│   │   ├── maya_improved.py          # マヤ暦計算エンジン（改良版・Dreamspell準拠）
│   │   ├── suanming_knowledge.yaml   # 算命学ナレッジベース
│   │   └── requirements.txt          # Python依存パッケージ
│   └── frontend/                     # フロントエンド
│       ├── src/
│       │   ├── pages/                # ページコンポーネント
│       │   ├── components/           # 共通コンポーネント
│       │   └── main.tsx              # エントリーポイント
│       ├── package.json
│       └── vite.config.ts
├── tests/                            # テストコード
│   └── test_suanming.py              # 算命学テスト（25件）
├── docs/                             # ドキュメント
│   └── deployment-plan.md            # デプロイ実行計画書
├── 算命学の要件定義書.md
└── 算命学命式計算アルゴリズム仕様.md
```

## 🧪 テスト

### バックエンドテスト

```bash
cd tests
pytest test_suanming.py -v
```

**結果**: 25テスト全て成功

### フロントエンドビルド

```bash
cd app/frontend
npm run build
```

## 🌐 デプロイ

詳細なデプロイ手順は [docs/deployment-plan.md](docs/deployment-plan.md) を参照してください。

### 概要

| コンポーネント | プラットフォーム | URL例 |
|--------------|----------------|-------|
| フロントエンド | Vercel | https://suumeigaku-maya.vercel.app |
| バックエンド | Render | https://suumeigaku-maya-api.onrender.com |
| データベース | Google Sheets | - |

### デプロイコマンド

**Vercel（フロントエンド）**
```bash
cd app/frontend
vercel --prod
```

**Render（バックエンド）**
- GitHubプッシュで自動デプロイ
- または Render Dashboard から手動デプロイ

## 📊 API仕様

### エンドポイント

#### `GET /api/v1/health`
ヘルスチェック

**レスポンス:**
```json
{
  "status": "ok",
  "service": "suanming-api",
  "version": "1.0.0"
}
```

#### `POST /api/v1/analyze`
算命学×マヤ暦の総合分析

**リクエスト:**
```json
{
  "birthdate": "2020-02-05",
  "birthtime": "12:00"
}
```

**レスポンス:**
```json
{
  "request_id": "uuid",
  "ts": "2025-10-23T12:34:56+09:00",
  "data": {
    "suanming": {
      "year_gan": "庚", "year_shi": "子",
      "day_gan": "甲", "day_shi": "子",
      "five_elements_score": {"木": 36, "火": 70, ...},
      "guardian_gods": ["木", "土", "水"]
    },
    "maya": {
      "kin": 183,
      "solar_seal": "青い夜",
      "tone": 1,
      "wavespell": "青い鷹"
    },
    "scores": {
      "overall": 0.72,
      "work": 0.68,
      "love": 0.75,
      "health": 0.61,
      "growth": 0.78
    },
    "insights": [...]
  }
}
```

## 🔧 技術スタック

### フロントエンド
- React 18.2.0
- TypeScript 5.3.3
- Vite 5.0.8
- React Router Dom 6.20.0

### バックエンド
- Python 3.11
- Flask 3.0.0
- PyYAML 6.0.1
- pytest 7.4.3

### インフラ
- Vercel (フロントエンド)
- Render (バックエンド)
- Google Sheets (データベース)

## 📖 ドキュメント

- [デプロイ実行計画書](docs/deployment-plan.md)
- [要件定義書](算命学の要件定義書.md)
- [アルゴリズム仕様書](算命学命式計算アルゴリズム仕様.md)

## 🤝 貢献

プルリクエストを歓迎します。大きな変更の場合は、まずIssueを開いて変更内容を議論してください。

## 📄 ライセンス

未定

## 👥 開発チーム

- プロジェクト: 算命学×マヤ暦コンサルシステム
- リポジトリ: https://github.com/taiyousan15/suumeigaku-maya-consul-system

## 📞 サポート

問題が発生した場合は、[GitHub Issues](https://github.com/taiyousan15/suumeigaku-maya-consul-system/issues) で報告してください。

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)
