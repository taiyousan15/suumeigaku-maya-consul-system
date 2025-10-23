interface SlidersProps {
  temperature: number
  setTemperature: (value: number) => void
  intensity: number
  setIntensity: (value: number) => void
}

export default function Sliders({ temperature, setTemperature, intensity, setIntensity }: SlidersProps) {
  return (
    <div className="card">
      <h3 style={{ marginBottom: '20px', color: '#333' }}>LLM設定</h3>

      <div className="slider-container">
        <div className="slider-label">
          <span>温度（創造性）</span>
          <span>{temperature.toFixed(1)}</span>
        </div>
        <input
          type="range"
          min="0.0"
          max="2.0"
          step="0.1"
          value={temperature}
          onChange={(e) => setTemperature(parseFloat(e.target.value))}
          className="slider"
        />
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#666', marginTop: '4px' }}>
          <span>保守的</span>
          <span>創造的</span>
        </div>
      </div>

      <div className="slider-container">
        <div className="slider-label">
          <span>煽り度（表現の強さ）</span>
          <span>{intensity}</span>
        </div>
        <input
          type="range"
          min="1"
          max="10"
          step="1"
          value={intensity}
          onChange={(e) => setIntensity(parseInt(e.target.value))}
          className="slider"
        />
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#666', marginTop: '4px' }}>
          <span>穏やか</span>
          <span>強め</span>
        </div>
      </div>
    </div>
  )
}
