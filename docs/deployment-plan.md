# 算命学×マヤ暦コンサルシステム デプロイ実行計画書

**作成日**: 2025-10-23
**対象環境**: 本番環境（Production）
**バックエンド**: Render
**フロントエンド**: Vercel

---

## 📋 目次

1. [Phase 0: 事前準備](#phase-0-事前準備)
2. [Phase 1: Google Cloud Platform セットアップ](#phase-1-google-cloud-platform-セットアップ)
3. [Phase 2: バックエンドデプロイ（Render）](#phase-2-バックエンドデプロイrender)
4. [Phase 3: フロントエンドデプロイ（Vercel）](#phase-3-フロントエンドデプロイvercel)
5. [Phase 4: 統合テスト](#phase-4-統合テスト)
6. [Phase 5: 本番稼働](#phase-5-本番稼働)
7. [Phase 6: 運用・監視](#phase-6-運用監視)
8. [ロールバック手順](#ロールバック手順)

---

## Phase 0: 事前準備

**所要時間**: 1-2時間
**担当者**: 開発者

### タスクリスト

#### ✅ 0.1 アカウント作成・確認

- [ ] Renderアカウント作成/ログイン
  - URL: https://render.com/
  - GitHubアカウント連携推奨

- [ ] Vercelアカウント作成/ログイン
  - URL: https://vercel.com/
  - GitHubアカウント連携推奨

- [ ] Google Cloud Platformアカウント確認
  - URL: https://console.cloud.google.com/
  - 請求アカウント設定済みを確認

#### ✅ 0.2 環境変数の準備

`.env.production` ファイルを作成：

```bash
# Backend (.env.production)
FLASK_ENV=production
PORT=8080
API_BASE=/api/v1
CORS_ORIGINS=https://your-app.vercel.app
GOOGLE_SERVICE_ACCOUNT_JSON_BASE64=<後で設定>
SHEETS_SPREADSHEET_ID=<後で設定>
OPENAI_API_KEY=<後で設定>
DEFAULT_MONTHLY_LIMIT=50
W_SUAN=0.6
W_MAYA=0.4
```

```bash
# Frontend (.env.production)
VITE_API_BASE=https://your-app.onrender.com/api/v1
```

#### ✅ 0.3 OpenAI APIキー取得

1. OpenAI Platform にアクセス: https://platform.openai.com/
2. API Keys → Create new secret key
3. キーをコピーして安全に保管
4. 使用量制限を設定（推奨: $50/月）

#### ✅ 0.4 コードの最終確認

```bash
# ローカルでテスト実行
cd tests
pytest test_suanming.py -v
# 全25テストが成功することを確認

# ビルド確認
cd ../app/frontend
npm run build
# エラーなくビルドできることを確認
```

#### ✅ 0.5 Gitタグの作成

```bash
git tag -a v1.0.0 -m "Initial production release"
git push origin v1.0.0
```

---

## Phase 1: Google Cloud Platform セットアップ

**所要時間**: 30分
**担当者**: 開発者

### タスクリスト

#### ✅ 1.1 GCPプロジェクト作成

1. GCP Console にアクセス: https://console.cloud.google.com/
2. 「プロジェクトを選択」→「新しいプロジェクト」
3. プロジェクト名: `suumeigaku-maya-system`
4. 「作成」をクリック

#### ✅ 1.2 Google Sheets API 有効化

1. 「APIとサービス」→「ライブラリ」
2. 「Google Sheets API」を検索
3. 「有効にする」をクリック

#### ✅ 1.3 サービスアカウント作成

1. 「APIとサービス」→「認証情報」
2. 「認証情報を作成」→「サービスアカウント」
3. サービスアカウント名: `suumeigaku-api`
4. ロール: 「編集者」を選択
5. 「完了」をクリック

#### ✅ 1.4 サービスアカウントキーの生成

1. 作成したサービスアカウントをクリック
2. 「キー」タブ → 「鍵を追加」→「新しい鍵を作成」
3. キーのタイプ: JSON
4. 「作成」→ JSONファイルがダウンロードされる
5. ファイル名を `service-account.json` に変更

#### ✅ 1.5 JSONキーをBase64エンコード

```bash
# macOS/Linux
base64 -i service-account.json -o service-account-base64.txt

# 出力されたBase64文字列をコピー
cat service-account-base64.txt | pbcopy
```

#### ✅ 1.6 Google Spreadsheetsの作成

1. Google Sheets にアクセス: https://sheets.google.com/
2. 新しいスプレッドシート作成: `SuumeigakuMayaDB`
3. 以下のシートを作成：
   - **Users** シート
     - 列: id, email, api_key, role, monthly_limit, used_count, created_at, updated_at
   - **CalcLogs** シート
     - 列: id, user_id, birthdate, birth_time, birth_place, categories, free_text, suanming_json, maya_json, scores_json, llm_meta_json, created_at
   - **Knowledge** シート
     - 列: key, type, value, updated_at

4. URLからスプレッドシートIDをコピー
   - URL形式: `https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit`
   - `{SPREADSHEET_ID}` の部分をコピー

#### ✅ 1.7 サービスアカウントに共有権限付与

1. スプレッドシートの「共有」ボタンをクリック
2. サービスアカウントのメールアドレスを追加
   - 形式: `suumeigaku-api@project-id.iam.gserviceaccount.com`
3. 権限: 「編集者」
4. 「送信」をクリック

**チェックポイント**:
- ✅ サービスアカウントJSONキーが生成された
- ✅ Base64エンコードされた文字列を取得した
- ✅ スプレッドシートIDを取得した
- ✅ サービスアカウントに編集権限を付与した

---

## Phase 2: バックエンドデプロイ（Render）

**所要時間**: 30-45分
**担当者**: 開発者

### タスクリスト

#### ✅ 2.1 Renderプロジェクト設定

1. Render Dashboard にログイン: https://dashboard.render.com/
2. 「New +」→「Web Service」を選択
3. 「Connect a repository」→ GitHubリポジトリを接続
4. リポジトリ選択: `taiyousan15/suumeigaku-maya-consul-system`
5. 「Connect」をクリック

#### ✅ 2.2 Web Serviceの基本設定

| 項目 | 設定値 |
|-----|-------|
| Name | `suumeigaku-maya-api` |
| Environment | Python 3 |
| Region | Oregon (US West) ※日本に最も近い |
| Branch | `main` |
| Root Directory | `app/api` |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn main:app --bind 0.0.0.0:$PORT --workers 2` |

#### ✅ 2.3 gunicornの追加

`app/api/requirements.txt` に以下を追加：

```txt
Flask==3.0.0
flask-cors==4.0.0
PyYAML==6.0.1
pytest==7.4.3
pytest-cov==4.1.0
gunicorn==21.2.0
```

コミット＆プッシュ：
```bash
git add app/api/requirements.txt
git commit -m "Add gunicorn for production deployment"
git push origin main
```

#### ✅ 2.4 環境変数の設定

Render Dashboard の「Environment」セクションで以下を設定：

| Key | Value |
|-----|-------|
| `FLASK_ENV` | `production` |
| `PORT` | `8080` |
| `API_BASE` | `/api/v1` |
| `CORS_ORIGINS` | `https://your-app.vercel.app` ※Phase 3後に更新 |
| `GOOGLE_SERVICE_ACCOUNT_JSON_BASE64` | ※Phase 1.5でコピーした値 |
| `SHEETS_SPREADSHEET_ID` | ※Phase 1.6で取得したID |
| `OPENAI_API_KEY` | ※Phase 0.3で取得したキー |
| `DEFAULT_MONTHLY_LIMIT` | `50` |
| `W_SUAN` | `0.6` |
| `W_MAYA` | `0.4` |
| `PYTHON_VERSION` | `3.11.0` |

#### ✅ 2.5 デプロイ実行

1. 「Create Web Service」をクリック
2. 自動ビルド＆デプロイが開始される（5-10分）
3. ログを監視してエラーがないか確認

#### ✅ 2.6 デプロイ確認

デプロイ完了後、RenderのURLを確認：
- 形式: `https://suumeigaku-maya-api.onrender.com`

ヘルスチェック：
```bash
curl https://suumeigaku-maya-api.onrender.com/api/v1/health
# Expected: {"status": "ok", "service": "suanming-api", "version": "1.0.0"}
```

APIテスト：
```bash
curl -X POST https://suumeigaku-maya-api.onrender.com/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"birthdate":"2020-02-05","birthtime":"12:00"}'
# Expected: JSON response with suanming and maya data
```

**チェックポイント**:
- ✅ ビルドが成功した
- ✅ サービスが起動した（Logs: "Running on all addresses"）
- ✅ ヘルスチェックが成功した
- ✅ API分析エンドポイントが動作した

---

## Phase 3: フロントエンドデプロイ（Vercel）

**所要時間**: 20-30分
**担当者**: 開発者

### タスクリスト

#### ✅ 3.1 環境変数ファイルの更新

`app/frontend/.env.production` を作成：

```env
VITE_API_BASE=https://suumeigaku-maya-api.onrender.com/api/v1
```

コミット＆プッシュ：
```bash
git add app/frontend/.env.production
git commit -m "Add production environment variables"
git push origin main
```

#### ✅ 3.2 Vercelプロジェクト作成

1. Vercel Dashboard にログイン: https://vercel.com/dashboard
2. 「Add New...」→「Project」を選択
3. GitHubリポジトリをインポート
4. リポジトリ選択: `taiyousan15/suumeigaku-maya-consul-system`
5. 「Import」をクリック

#### ✅ 3.3 プロジェクト設定

| 項目 | 設定値 |
|-----|-------|
| Framework Preset | Vite |
| Root Directory | `app/frontend` |
| Build Command | `npm run build` |
| Output Directory | `dist` |
| Install Command | `npm install` |

#### ✅ 3.4 環境変数の設定

「Environment Variables」セクションで設定：

| Key | Value | Environments |
|-----|-------|-------------|
| `VITE_API_BASE` | `https://suumeigaku-maya-api.onrender.com/api/v1` | Production |

#### ✅ 3.5 デプロイ実行

1. 「Deploy」をクリック
2. ビルド＆デプロイが自動実行される（3-5分）
3. デプロイ完了後、URLを確認
   - 形式: `https://suumeigaku-maya-consul-system-xxx.vercel.app`

#### ✅ 3.6 カスタムドメイン設定（オプション）

1. Vercel Dashboard → プロジェクト → Settings → Domains
2. 「Add Domain」をクリック
3. 独自ドメインを入力（例: `suumeigaku-maya.com`）
4. DNS設定の指示に従う
5. SSL証明書が自動発行される（数分）

#### ✅ 3.7 CORS設定の更新

RenderのバックエンドでCORS設定を更新：

1. Render Dashboard → suumeigaku-maya-api
2. Environment → `CORS_ORIGINS` を編集
3. 値を更新: `https://suumeigaku-maya-consul-system-xxx.vercel.app`
4. 「Save Changes」→ 自動再デプロイ

#### ✅ 3.8 フロントエンド動作確認

1. VercelのURLにアクセス
2. ホーム画面が表示されることを確認
3. 生年月日を入力してフォーム送信
4. 結果画面が表示されることを確認
5. APIとの通信が正常に動作することを確認

**チェックポイント**:
- ✅ ビルドが成功した
- ✅ サイトが公開された
- ✅ UIが正しく表示される
- ✅ APIとの通信が成功する
- ✅ 分析結果が表示される

---

## Phase 4: 統合テスト

**所要時間**: 30-60分
**担当者**: 開発者、QA担当者

### テストシナリオ

#### ✅ 4.1 機能テスト

**TC-001: 基本フロー**
- [ ] ホーム画面で生年月日入力（例: 1990-05-15）
- [ ] 出生時刻入力（例: 14:30）
- [ ] 「結果を見る」ボタンをクリック
- [ ] 分析中の表示が出る
- [ ] 結果画面に遷移する
- [ ] 算命学の結果が表示される（干支、五行配点など）
- [ ] マヤ暦の結果が表示される（Kin、紋章など）
- [ ] 統合スコアが表示される

**TC-002: エラーハンドリング**
- [ ] 生年月日未入力で送信 → エラーメッセージ表示
- [ ] 無効な日付（例: 2025-13-40）→ エラーメッセージ表示
- [ ] ネットワークエラー時の挙動確認

**TC-003: タブ切り替え**
- [ ] 総合タブをクリック → 総合スコア表示
- [ ] 仕事タブをクリック → 仕事スコア表示
- [ ] 恋愛タブをクリック → 恋愛スコア表示
- [ ] 健康タブをクリック → 健康スコア表示
- [ ] 自己成長タブをクリック → 自己成長スコア表示

**TC-004: LLM設定**
- [ ] 温度スライダーを変更（0.0 → 2.0）
- [ ] 煽り度スライダーを変更（1 → 10）
- [ ] 設定が分析に反映されることを確認

#### ✅ 4.2 パフォーマンステスト

**レスポンスタイム計測**
```bash
# APIレスポンスタイム
time curl -X POST https://suumeigaku-maya-api.onrender.com/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"birthdate":"2020-02-05","birthtime":"12:00"}'

# 目標: < 3秒（P95）
```

**負荷テスト（オプション）**
```bash
# Apache Bench を使用
ab -n 100 -c 10 https://suumeigaku-maya-api.onrender.com/api/v1/health

# 目標:
# - Requests per second: > 10 req/sec
# - Time per request: < 1000ms
```

#### ✅ 4.3 セキュリティチェック

- [ ] HTTPS接続が強制される
- [ ] CORS設定が正しく動作する
- [ ] APIキーが環境変数で管理されている
- [ ] エラーメッセージに機密情報が含まれていない
- [ ] XSS対策が施されている
- [ ] CSRF対策が施されている

#### ✅ 4.4 ブラウザ互換性テスト

- [ ] Chrome（最新版）
- [ ] Firefox（最新版）
- [ ] Safari（最新版）
- [ ] Edge（最新版）
- [ ] モバイルブラウザ（iOS Safari、Android Chrome）

#### ✅ 4.5 レスポンシブデザイン確認

- [ ] デスクトップ（1920x1080）
- [ ] タブレット（768x1024）
- [ ] モバイル（375x667）

**チェックポイント**:
- ✅ 全機能テストケースが成功した
- ✅ パフォーマンス目標を達成した
- ✅ セキュリティチェックを通過した
- ✅ 全ブラウザで動作確認した
- ✅ レスポンシブデザインが正常

---

## Phase 5: 本番稼働

**所要時間**: 1時間
**担当者**: プロジェクトマネージャー、開発者

### タスクリスト

#### ✅ 5.1 最終確認

- [ ] Phase 4の全テストが完了している
- [ ] 本番環境のURLを確認
  - Backend: `https://suumeigaku-maya-api.onrender.com`
  - Frontend: `https://suumeigaku-maya-consul-system-xxx.vercel.app`
- [ ] ドキュメントが最新化されている
- [ ] README.mdが更新されている

#### ✅ 5.2 監視設定

**Renderの監視**
1. Render Dashboard → suumeigaku-maya-api → Metrics
2. CPU使用率、メモリ使用率を確認
3. アラート設定（オプション）

**Vercelの監視**
1. Vercel Dashboard → Analytics
2. ページビュー、エラー率を確認

#### ✅ 5.3 ログ設定

**Render Logs**
```bash
# リアルタイムログ確認
# Render Dashboard → Logs タブで確認
```

**Vercel Logs**
```bash
# Vercel Dashboard → Deployments → Latest → Logs
```

#### ✅ 5.4 バックアップ設定

**Google Sheets のバックアップ**
1. Google Sheetsのメニュー → ファイル → コピーを作成
2. 名前: `SuumeigakuMayaDB_Backup_YYYYMMDD`
3. 定期バックアップをカレンダーに設定（週次推奨）

**コードのバックアップ**
- GitHub上でタグ管理されているため追加対応不要

#### ✅ 5.5 リリースノートの作成

`CHANGELOG.md` を更新：

```markdown
# Changelog

## [1.0.0] - 2025-10-23

### Added
- 算命学命式計算エンジン（年柱・月柱・日柱・時柱）
- マヤ暦計算エンジン（Kin、紋章、音、ウェイブスペル）
- 五行配点計算と守護神選定
- React + Vite フロントエンド UI
- Flask REST API
- Google Sheets データベース連携

### Infrastructure
- Render でバックエンドデプロイ
- Vercel でフロントエンドデプロイ
- 本番環境でHTTPS対応完了
```

#### ✅ 5.6 本番リリース宣言

- [ ] ステークホルダーにリリース完了を通知
- [ ] ユーザー向けドキュメント公開
- [ ] サポート体制の確認

**チェックポイント**:
- ✅ 監視体制が整った
- ✅ ログが正常に記録されている
- ✅ バックアップ体制が整った
- ✅ リリースノートが作成された
- ✅ 関係者への通知が完了した

---

## Phase 6: 運用・監視

**担当者**: 運用チーム

### 日次タスク

#### ✅ 6.1 ヘルスチェック

```bash
# 毎朝9:00に実行
curl https://suumeigaku-maya-api.onrender.com/api/v1/health
curl https://suumeigaku-maya-consul-system-xxx.vercel.app/
```

#### ✅ 6.2 エラーログ確認

- Render Dashboard → Logs → エラーログを確認
- Vercel Dashboard → Logs → エラーを確認
- 異常があれば対応

### 週次タスク

#### ✅ 6.3 パフォーマンスレビュー

- Render Metrics でCPU/メモリ使用率を確認
- Vercel Analytics でページビュー、エラー率を確認
- 429エラー（レート制限）の発生状況を確認

#### ✅ 6.4 データベースバックアップ

- Google Sheets のコピーを作成
- バックアップフォルダに保存

### 月次タスク

#### ✅ 6.5 コストレビュー

- Render の請求を確認
- Vercel の請求を確認
- OpenAI API の使用量を確認
- 予算に対する消化率を確認

#### ✅ 6.6 セキュリティアップデート

```bash
# 依存パッケージの脆弱性チェック
cd app/frontend
npm audit

cd ../api
pip list --outdated
```

- 脆弱性が見つかった場合は更新

#### ✅ 6.7 ユーザーフィードバック分析

- 問い合わせ内容を分析
- 改善点を洗い出し
- 次期バージョンの計画

### アラート対応

#### 🚨 サービスダウン時

1. **初動対応（5分以内）**
   - ステータス確認
   - ログ確認
   - ステークホルダーへ通知

2. **原因調査（15分以内）**
   - エラーログ分析
   - インフラ状態確認
   - 外部サービス状態確認

3. **復旧作業（30分以内）**
   - 必要に応じて再デプロイ
   - または Phase 7（ロールバック）実行

4. **事後対応（24時間以内）**
   - インシデントレポート作成
   - 再発防止策の検討
   - 関係者への報告

---

## Phase 7: ロールバック手順

**トリガー**: 重大なバグ発見、サービス障害発生時

### バックエンドのロールバック

#### ✅ 7.1 前バージョンへの復帰（Render）

**方法1: Render Dashboardから**
1. Render Dashboard → suumeigaku-maya-api
2. 「Deploys」タブを開く
3. 前回の成功したデプロイを探す
4. 「Redeploy」ボタンをクリック

**方法2: Gitタグから**
```bash
# ローカルで前バージョンのタグにチェックアウト
git checkout v0.9.0

# 強制プッシュ（注意: 慎重に実行）
git push origin main --force

# Renderが自動的に再デプロイ
```

#### ✅ 7.2 確認

```bash
curl https://suumeigaku-maya-api.onrender.com/api/v1/health
# バージョン番号を確認
```

### フロントエンドのロールバック

#### ✅ 7.3 前バージョンへの復帰（Vercel）

**方法1: Vercel Dashboardから**
1. Vercel Dashboard → プロジェクト
2. 「Deployments」タブを開く
3. 前回の成功したデプロイを探す
4. 「⋯」メニュー → 「Promote to Production」

**方法2: CLI経由**
```bash
# Vercel CLIインストール（初回のみ）
npm i -g vercel

# ログイン
vercel login

# 前回のデプロイをプロモート
vercel promote <deployment-url>
```

#### ✅ 7.4 確認

ブラウザでフロントエンドにアクセスして動作確認

### データベースのロールバック

#### ✅ 7.5 Google Sheets の復元

1. バックアップフォルダから最新のバックアップを開く
2. 「ファイル」→「コピーを作成」
3. 元のスプレッドシート名に変更
4. スプレッドシートIDが変わるため、環境変数を更新
5. Renderで `SHEETS_SPREADSHEET_ID` を新しいIDに更新
6. 再デプロイ

**チェックポイント**:
- ✅ サービスが正常に復旧した
- ✅ データの整合性が保たれている
- ✅ ユーザーへの影響が最小限に抑えられた
- ✅ インシデントレポートを作成した

---

## 📊 デプロイチェックリスト（全体）

### 事前準備
- [ ] Render/Vercelアカウント作成
- [ ] GCPプロジェクト作成
- [ ] OpenAI APIキー取得
- [ ] 環境変数準備
- [ ] ローカルテスト完了

### GCP
- [ ] サービスアカウント作成
- [ ] JSONキーをBase64エンコード
- [ ] Google Sheets作成（Users, CalcLogs, Knowledge）
- [ ] サービスアカウントに共有権限付与

### バックエンド（Render）
- [ ] Web Service作成
- [ ] 環境変数設定（8個）
- [ ] gunicorn追加
- [ ] デプロイ実行
- [ ] ヘルスチェック成功
- [ ] API動作確認

### フロントエンド（Vercel）
- [ ] プロジェクト作成
- [ ] 環境変数設定（VITE_API_BASE）
- [ ] デプロイ実行
- [ ] UI表示確認
- [ ] API連携確認

### CORS設定
- [ ] RenderでVercelのURLをCORS_ORIGINSに設定

### 統合テスト
- [ ] 機能テスト完了（4シナリオ）
- [ ] パフォーマンステスト完了
- [ ] セキュリティチェック完了
- [ ] ブラウザ互換性確認
- [ ] レスポンシブデザイン確認

### 本番稼働
- [ ] 監視設定
- [ ] ログ設定
- [ ] バックアップ設定
- [ ] リリースノート作成
- [ ] 関係者への通知

---

## 🔗 重要URL一覧

| サービス | URL | 用途 |
|---------|-----|------|
| GitHub | https://github.com/taiyousan15/suumeigaku-maya-consul-system | コードリポジトリ |
| Render | https://dashboard.render.com/ | バックエンド管理 |
| Vercel | https://vercel.com/dashboard | フロントエンド管理 |
| GCP Console | https://console.cloud.google.com/ | GCP管理 |
| Google Sheets | ※Phase 1.6で作成 | データベース |
| OpenAI Platform | https://platform.openai.com/ | API管理 |

---

## 📞 サポート連絡先

| 役割 | 担当者 | 連絡先 |
|------|--------|--------|
| プロジェクトマネージャー | ※記入 | ※記入 |
| バックエンド開発 | ※記入 | ※記入 |
| フロントエンド開発 | ※記入 | ※記入 |
| インフラ担当 | ※記入 | ※記入 |
| 運用担当 | ※記入 | ※記入 |

---

## 📝 更新履歴

| 日付 | バージョン | 変更内容 | 担当者 |
|-----|-----------|----------|--------|
| 2025-10-23 | 1.0.0 | 初版作成 | Claude Code |

---

**次のアクション**: Phase 0から順番に実行を開始してください。
