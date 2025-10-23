import { useState } from 'react'

interface AdminProps {
  onNavigate: (page: 'home' | 'result' | 'history' | 'admin') => void
}

export default function Admin({ onNavigate }: AdminProps) {
  const [wSuan, setWSuan] = useState(0.6)
  const [wMaya, setWMaya] = useState(0.4)
  const [maxTokens, setMaxTokens] = useState(900)
  const [monthlyLimit, setMonthlyLimit] = useState(50)

  const handleSave = () => {
    // 重みの合計チェック
    if (Math.abs(wSuan + wMaya - 1.0) > 0.01) {
      alert('重みの合計は1.0である必要があります')
      return
    }

    alert('設定を保存しました')
  }

  return (
    <div>
      <div className="card">
        <h2 style={{ marginBottom: '20px', color: '#333' }}>管理画面</h2>
        <p style={{ color: '#666', marginBottom: '30px' }}>
          ※ この画面は管理者のみアクセス可能です
        </p>

        {/* 重み設定 */}
        <div style={{ marginBottom: '30px' }}>
          <h3 style={{ marginBottom: '16px', color: '#667eea' }}>スコア重み設定</h3>

          <div className="slider-container">
            <div className="slider-label">
              <span>算命学の重み</span>
              <span>{wSuan.toFixed(2)}</span>
            </div>
            <input
              type="range"
              min="0.0"
              max="1.0"
              step="0.05"
              value={wSuan}
              onChange={(e) => {
                const newVal = parseFloat(e.target.value)
                setWSuan(newVal)
                setWMaya(1.0 - newVal)
              }}
              className="slider"
            />
          </div>

          <div className="slider-container">
            <div className="slider-label">
              <span>マヤ暦の重み</span>
              <span>{wMaya.toFixed(2)}</span>
            </div>
            <input
              type="range"
              min="0.0"
              max="1.0"
              step="0.05"
              value={wMaya}
              onChange={(e) => {
                const newVal = parseFloat(e.target.value)
                setWMaya(newVal)
                setWSuan(1.0 - newVal)
              }}
              className="slider"
            />
          </div>

          <div style={{
            padding: '12px',
            background: wSuan + wMaya === 1.0 ? '#e8f5e9' : '#ffebee',
            borderRadius: '8px',
            marginTop: '12px'
          }}>
            <p style={{ fontSize: '14px', color: '#555' }}>
              合計: {(wSuan + wMaya).toFixed(2)} {wSuan + wMaya === 1.0 ? '✓' : '⚠️ 合計は1.0である必要があります'}
            </p>
          </div>
        </div>

        {/* LLM設定 */}
        <div style={{ marginBottom: '30px' }}>
          <h3 style={{ marginBottom: '16px', color: '#667eea' }}>LLM設定</h3>

          <div className="form-group">
            <label>最大トークン数</label>
            <input
              type="number"
              value={maxTokens}
              onChange={(e) => setMaxTokens(parseInt(e.target.value))}
              min="256"
              max="1200"
            />
            <small style={{ color: '#666', fontSize: '12px' }}>
              推奨範囲: 256-1200
            </small>
          </div>
        </div>

        {/* レート制限設定 */}
        <div style={{ marginBottom: '30px' }}>
          <h3 style={{ marginBottom: '16px', color: '#667eea' }}>レート制限</h3>

          <div className="form-group">
            <label>月間利用上限（1ユーザーあたり）</label>
            <input
              type="number"
              value={monthlyLimit}
              onChange={(e) => setMonthlyLimit(parseInt(e.target.value))}
              min="1"
              max="1000"
            />
          </div>
        </div>

        {/* 知識ベース編集 */}
        <div style={{ marginBottom: '30px' }}>
          <h3 style={{ marginBottom: '16px', color: '#667eea' }}>知識ベース（用語辞書）</h3>

          <div style={{
            padding: '16px',
            background: '#f5f5f5',
            borderRadius: '8px',
            marginBottom: '12px'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
              <strong>貫索星</strong>
              <button style={{
                padding: '4px 12px',
                background: '#667eea',
                color: 'white',
                border: 'none',
                borderRadius: '4px',
                cursor: 'pointer'
              }}>
                編集
              </button>
            </div>
            <p style={{ fontSize: '14px', color: '#666' }}>
              独立心が強く、マイペースな性格。自分の信念を貫く...
            </p>
          </div>

          <button
            style={{
              padding: '10px 20px',
              background: '#4caf50',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer'
            }}
            onClick={() => alert('新規追加機能は実装中です')}
          >
            ＋ 新規用語を追加
          </button>
        </div>

        {/* 統計情報 */}
        <div style={{ marginBottom: '30px' }}>
          <h3 style={{ marginBottom: '16px', color: '#667eea' }}>利用統計</h3>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px' }}>
            <div style={{ padding: '20px', background: '#f5f5f5', borderRadius: '8px', textAlign: 'center' }}>
              <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#667eea' }}>127</div>
              <div style={{ fontSize: '14px', color: '#666', marginTop: '8px' }}>今月の総分析数</div>
            </div>
            <div style={{ padding: '20px', background: '#f5f5f5', borderRadius: '8px', textAlign: 'center' }}>
              <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#4caf50' }}>42</div>
              <div style={{ fontSize: '14px', color: '#666', marginTop: '8px' }}>アクティブユーザー</div>
            </div>
            <div style={{ padding: '20px', background: '#f5f5f5', borderRadius: '8px', textAlign: 'center' }}>
              <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#ff9800' }}>3.2K</div>
              <div style={{ fontSize: '14px', color: '#666', marginTop: '8px' }}>LLMトークン使用量</div>
            </div>
          </div>
        </div>

        {/* 保存ボタン */}
        <button
          className="button-primary"
          onClick={handleSave}
        >
          設定を保存
        </button>
      </div>
    </div>
  )
}
