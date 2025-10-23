import { useState } from 'react'

interface ResultProps {
  onNavigate: (page: 'home' | 'result' | 'history' | 'admin') => void
  resultData: any
}

export default function Result({ onNavigate, resultData }: ResultProps) {
  const [activeTab, setActiveTab] = useState('overall')

  if (!resultData) {
    return (
      <div className="card">
        <p>結果データがありません。</p>
        <button className="button-primary" onClick={() => onNavigate('home')}>
          ホームに戻る
        </button>
      </div>
    )
  }

  const { data } = resultData
  const { suanming, maya, scores, insights } = data

  const tabs = [
    { id: 'overall', label: '総合' },
    { id: 'work', label: '仕事' },
    { id: 'love', label: '恋愛' },
    { id: 'health', label: '健康' },
    { id: 'growth', label: '自己成長' }
  ]

  const renderScore = (score: number) => {
    return (score * 100).toFixed(0)
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.7) return '#4caf50'
    if (score >= 0.5) return '#ff9800'
    return '#f44336'
  }

  return (
    <div>
      {/* 総合スコアカード */}
      <div className="score-card">
        <h2>総合スコア</h2>
        <div className="score-value">{renderScore(scores.overall)}点</div>
        <p>今のあなたは、バランスが取れた状態です</p>
        <div className="keywords">
          <span className="keyword-tag">今日のキーワード: 調和</span>
          <span className="keyword-tag">今週: 飛躍</span>
          <span className="keyword-tag">今月: 成長</span>
        </div>
      </div>

      {/* タブ */}
      <div className="tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* コンテンツ */}
      <div className="card">
        {activeTab === 'overall' && (
          <div>
            <h3 style={{ marginBottom: '20px', color: '#333' }}>総合分析</h3>

            {/* 算命学セクション */}
            <div style={{ marginBottom: '30px', padding: '20px', background: '#f5f5f5', borderRadius: '8px' }}>
              <h4 style={{ color: '#667eea', marginBottom: '16px' }}>算命学からの分析</h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
                <div>
                  <strong>年柱:</strong> {suanming.year_gan}{suanming.year_shi}
                </div>
                <div>
                  <strong>月柱:</strong> {suanming.month_gan}{suanming.month_shi}
                </div>
                <div>
                  <strong>日柱:</strong> {suanming.day_gan}{suanming.day_shi}
                </div>
                <div>
                  <strong>時柱:</strong> {suanming.hour_gan}{suanming.hour_shi}
                </div>
                <div style={{ gridColumn: 'span 2' }}>
                  <strong>守護神:</strong> {suanming.guardian_gods.join('、')}
                </div>
                <div style={{ gridColumn: 'span 2' }}>
                  <strong>忌神:</strong> {suanming.taboo_elements.join('、')}
                </div>
              </div>
              <div style={{ marginTop: '16px' }}>
                <strong>五行バランス:</strong>
                <div style={{ display: 'flex', gap: '8px', marginTop: '8px', flexWrap: 'wrap' }}>
                  {Object.entries(suanming.five_elements_score).map(([element, score]) => (
                    <span key={element} style={{
                      padding: '6px 12px',
                      background: 'white',
                      borderRadius: '6px',
                      fontSize: '14px'
                    }}>
                      {element}: {score}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* マヤ暦セクション */}
            <div style={{ marginBottom: '30px', padding: '20px', background: '#f5f5f5', borderRadius: '8px' }}>
              <h4 style={{ color: '#764ba2', marginBottom: '16px' }}>マヤ暦からの分析</h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
                <div>
                  <strong>Kin:</strong> {maya.kin}
                </div>
                <div>
                  <strong>太陽の紋章:</strong> {maya.solar_seal}
                </div>
                <div>
                  <strong>銀河の音:</strong> {maya.tone}
                </div>
                <div>
                  <strong>ウェイブスペル:</strong> {maya.wavespell}
                </div>
              </div>
            </div>

            {/* 統合インサイト */}
            <div>
              <h4 style={{ marginBottom: '16px', color: '#333' }}>行動提案</h4>
              {insights.map((insight: any, index: number) => (
                <div key={index} style={{
                  marginBottom: '16px',
                  padding: '16px',
                  background: '#f9f9f9',
                  borderLeft: '4px solid #667eea',
                  borderRadius: '4px'
                }}>
                  <h5 style={{ color: '#667eea', marginBottom: '8px' }}>{insight.title}</h5>
                  <p style={{ color: '#555', lineHeight: '1.6' }}>{insight.advice}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab !== 'overall' && (
          <div>
            <h3 style={{ marginBottom: '20px', color: '#333' }}>
              {tabs.find(t => t.id === activeTab)?.label}運
            </h3>
            <div style={{ marginBottom: '20px' }}>
              <div style={{
                fontSize: '48px',
                fontWeight: 'bold',
                color: getScoreColor(scores[activeTab as keyof typeof scores]),
                marginBottom: '8px'
              }}>
                {renderScore(scores[activeTab as keyof typeof scores])}点
              </div>
            </div>
            <div style={{ padding: '20px', background: '#f5f5f5', borderRadius: '8px' }}>
              <p style={{ lineHeight: '1.8', color: '#555' }}>
                {activeTab === 'work' && '仕事面では、新しい挑戦に適した時期です。チームワークを大切にすることで、より良い成果が期待できます。'}
                {activeTab === 'love' && '恋愛面では、相手の気持ちを理解することが重要です。コミュニケーションを大切にしましょう。'}
                {activeTab === 'health' && '健康面では、休息を十分に取ることが大切です。無理をせず、バランスの取れた生活を心がけましょう。'}
                {activeTab === 'growth' && '自己成長の面では、学びを深める絶好の機会です。新しい知識や経験を積極的に取り入れましょう。'}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* アクションボタン */}
      <div style={{ display: 'flex', gap: '12px', marginTop: '20px' }}>
        <button
          className="button-primary"
          onClick={() => onNavigate('home')}
          style={{ flex: 1 }}
        >
          新しい分析
        </button>
        <button
          className="button-primary"
          onClick={() => alert('結果をコピーしました')}
          style={{ flex: 1, background: '#4caf50' }}
        >
          結果をコピー
        </button>
      </div>
    </div>
  )
}
