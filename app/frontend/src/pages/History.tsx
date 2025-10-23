interface HistoryProps {
  onNavigate: (page: 'home' | 'result' | 'history' | 'admin') => void
}

export default function History({ onNavigate }: HistoryProps) {
  // モックデータ（後でAPIから取得）
  const mockHistory = [
    {
      id: '1',
      date: '2025-10-23',
      categories: ['仕事', '恋愛'],
      score: 0.72,
      name: '山田 花子'
    },
    {
      id: '2',
      date: '2025-10-20',
      categories: ['健康', '金運'],
      score: 0.65,
      name: '佐藤 太郎'
    },
    {
      id: '3',
      date: '2025-10-15',
      categories: ['人間関係'],
      score: 0.78,
      name: '田中 美咲'
    }
  ]

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.7) return '#4caf50'
    if (score >= 0.5) return '#ff9800'
    return '#f44336'
  }

  return (
    <div>
      <div className="card">
        <h2 style={{ marginBottom: '20px', color: '#333' }}>分析履歴</h2>

        <div style={{ marginBottom: '20px', display: 'flex', gap: '12px' }}>
          <select style={{
            padding: '10px',
            borderRadius: '8px',
            border: '2px solid #e0e0e0',
            fontSize: '14px'
          }}>
            <option>すべてのカテゴリ</option>
            <option>仕事</option>
            <option>恋愛</option>
            <option>健康</option>
            <option>金運</option>
          </select>

          <input
            type="date"
            style={{
              padding: '10px',
              borderRadius: '8px',
              border: '2px solid #e0e0e0',
              fontSize: '14px'
            }}
            placeholder="日付フィルタ"
          />
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
          {mockHistory.map(item => (
            <div
              key={item.id}
              style={{
                padding: '20px',
                background: '#f9f9f9',
                borderRadius: '12px',
                border: '2px solid #e0e0e0',
                cursor: 'pointer',
                transition: 'all 0.3s'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = '#667eea'
                e.currentTarget.style.transform = 'translateY(-2px)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = '#e0e0e0'
                e.currentTarget.style.transform = 'translateY(0)'
              }}
              onClick={() => alert('詳細表示機能は実装中です')}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h3 style={{ color: '#333', marginBottom: '8px' }}>{item.name || '名前なし'}</h3>
                  <p style={{ color: '#666', fontSize: '14px', marginBottom: '8px' }}>
                    {formatDate(item.date)}
                  </p>
                  <div style={{ display: 'flex', gap: '8px' }}>
                    {item.categories.map(cat => (
                      <span
                        key={cat}
                        style={{
                          padding: '4px 12px',
                          background: 'white',
                          borderRadius: '16px',
                          fontSize: '12px',
                          color: '#667eea'
                        }}
                      >
                        {cat}
                      </span>
                    ))}
                  </div>
                </div>
                <div style={{ textAlign: 'right' }}>
                  <div style={{
                    fontSize: '32px',
                    fontWeight: 'bold',
                    color: getScoreColor(item.score)
                  }}>
                    {(item.score * 100).toFixed(0)}
                  </div>
                  <div style={{ fontSize: '14px', color: '#666' }}>点</div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {mockHistory.length === 0 && (
          <div style={{
            textAlign: 'center',
            padding: '40px',
            color: '#999'
          }}>
            <p>まだ分析履歴がありません</p>
            <button
              className="button-primary"
              onClick={() => onNavigate('home')}
              style={{ marginTop: '20px', maxWidth: '300px' }}
            >
              最初の分析を始める
            </button>
          </div>
        )}
      </div>

      <div style={{ marginTop: '20px' }}>
        <button
          className="button-primary"
          onClick={() => alert('CSV出力機能は実装中です')}
        >
          CSV形式でエクスポート
        </button>
      </div>
    </div>
  )
}
