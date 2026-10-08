import { Route, Routes } from 'react-router-dom'
import Header from './components/Header'
import AnalyzePage from './pages/AnalyzePage'
import AssistantPage from './pages/AssistantPage'
import HomePage from './pages/HomePage'


function App() {
  return (
    <div className="min-h-screen bg-paper-soft">
      <Header />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/analyze" element={<AnalyzePage />} />
        <Route path="/assistant" element={<AssistantPage />} />
      </Routes>
    </div>
  )
}

export default App
