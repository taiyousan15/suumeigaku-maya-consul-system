import { useState } from 'react'
import Sliders from '../components/Sliders'

interface HomeProps {
  onNavigate: (page: 'home' | 'result' | 'history' | 'admin') => void
  setResultData: (data: any) => void
}

export default function Home({ onNavigate, setResultData }: HomeProps) {
  const [name, setName] = useState('')
  const [birthdate, setBirthdate] = useState('')
  const [birthTime, setBirthTime] = useState('12:00')
  const [birthPlace, setBirthPlace] = useState('東京')
  const [categories, setCategories] = useState<string[]>(['仕事'])
  const [freeText, setFreeText] = useState('')
  const [temperature, setTemperature] = useState(0.5)
  const [intensity, setIntensity] = useState(6)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const categoryOptions = ['仕事', '恋愛', '人間関係', '健康', '金運', '学習']

  const handleCategoryChange = (category: string) => {
    if (categories.includes(category)) {
      setCategories(categories.filter(c => c !== category))
    } else {
      setCategories([...categories, category])
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!birthdate) {
      setError('生年月日は必須です')
      return
    }

    setLoading(true)

    try {
      // 実際のAPIを呼び出し
      const response = await fetch('http://localhost:8080/api/v1/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          birthdate: birthdate,
          birthtime: birthTime
        })
      })

      if (!response.ok) {
        throw new Error(`API Error: ${response.status}`)
      }

      const result = await response.json()
      setResultData(result)
      setLoading(false)
      onNavigate('result')
    } catch (err: any) {
      setError(`エラーが発生しました: ${err.message}`)
      setLoading(false)
    }
  }

  return (
    <div>
      {error && <div className="error">{error}</div>}

      <form onSubmit={handleSubmit}>
        <div className="card">
          <h2 style={{ marginBottom: '24px', color: '#333' }}>基本情報入力</h2>

          <div className="form-group">
            <label>お名前（任意）</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="山田 花子"
            />
          </div>

          <div className="form-group">
            <label>生年月日 <span style={{ color: 'red' }}>*</span></label>
            <input
              type="date"
              value={birthdate}
              onChange={(e) => setBirthdate(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>出生時刻（任意）</label>
            <input
              type="time"
              value={birthTime}
              onChange={(e) => setBirthTime(e.target.value)}
            />
            <small style={{ color: '#666', fontSize: '12px' }}>
              ※不明な場合は12:00（正午）を使用します
            </small>
          </div>

          <div className="form-group">
            <label>出生地（任意）</label>
            <input
              type="text"
              value={birthPlace}
              onChange={(e) => setBirthPlace(e.target.value)}
              placeholder="東京"
            />
          </div>

          <div className="form-group">
            <label>相談カテゴリ（複数選択可）</label>
            <div className="checkbox-group">
              {categoryOptions.map(category => (
                <label key={category} className="checkbox-item">
                  <input
                    type="checkbox"
                    checked={categories.includes(category)}
                    onChange={() => handleCategoryChange(category)}
                  />
                  <span>{category}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label>お悩み・ご相談内容（任意）</label>
            <textarea
              value={freeText}
              onChange={(e) => setFreeText(e.target.value)}
              rows={4}
              placeholder="転職を考えているのですが、タイミングが不安です..."
            />
          </div>
        </div>

        <Sliders
          temperature={temperature}
          setTemperature={setTemperature}
          intensity={intensity}
          setIntensity={setIntensity}
        />

        <button type="submit" className="button-primary" disabled={loading}>
          {loading ? '分析中...' : '結果を見る'}
        </button>
      </form>
    </div>
  )
}
