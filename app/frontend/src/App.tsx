import { useState } from 'react'
import Home from './pages/Home'
import Result from './pages/Result'
import History from './pages/History'
import Admin from './pages/Admin'

type Page = 'home' | 'result' | 'history' | 'admin'

function App() {
  const [currentPage, setCurrentPage] = useState<Page>('home')
  const [resultData, setResultData] = useState<any>(null)

  const renderPage = () => {
    switch (currentPage) {
      case 'home':
        return <Home onNavigate={setCurrentPage} setResultData={setResultData} />
      case 'result':
        return <Result onNavigate={setCurrentPage} resultData={resultData} />
      case 'history':
        return <History onNavigate={setCurrentPage} />
      case 'admin':
        return <Admin onNavigate={setCurrentPage} />
      default:
        return <Home onNavigate={setCurrentPage} setResultData={setResultData} />
    }
  }

  return (
    <div className="container">
      <header className="header">
        <h1>算命学×マヤ暦コンサルシステム</h1>
        <p style={{ color: '#666', marginTop: '8px' }}>
          生年月日から、算命学とマヤ暦に基づいた総合的なアドバイスを提供します
        </p>
        <nav className="nav">
          <button
            className={`nav-button ${currentPage === 'home' ? 'active' : ''}`}
            onClick={() => setCurrentPage('home')}
          >
            ホーム
          </button>
          <button
            className={`nav-button ${currentPage === 'result' ? 'active' : ''}`}
            onClick={() => setCurrentPage('result')}
          >
            結果
          </button>
          <button
            className={`nav-button ${currentPage === 'history' ? 'active' : ''}`}
            onClick={() => setCurrentPage('history')}
          >
            履歴
          </button>
          <button
            className={`nav-button ${currentPage === 'admin' ? 'active' : ''}`}
            onClick={() => setCurrentPage('admin')}
          >
            管理
          </button>
        </nav>
      </header>

      <main>{renderPage()}</main>

      <footer className="footer">
        <p>※ 本サービスはエンターテインメント・自己理解支援を目的としています</p>
        <p>医療・法律・投資助言ではありません</p>
      </footer>
    </div>
  )
}

export default App
