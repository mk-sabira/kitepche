import { Route, Routes } from 'react-router-dom'
import Header from './components/Header'
import AnalyzePage from './pages/AnalyzePage'
import AssistantPage from './pages/AssistantPage'
import BookPage from './pages/BookPage'
import HomePage from './pages/HomePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/Register'
import { useEffect } from 'react'
import { warmUpServer } from './api/warmup'


function App() {
    useEffect(() => {
    warmUpServer()
  }, [])
  return (
    <div className="min-h-screen bg-paper-soft">
      <Header />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/analyze" element={<AnalyzePage />} />
        <Route path="/assistant" element={<AssistantPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />}/>
        <Route path="/books/:id" element={<BookPage />} />
      </Routes>
    </div>
  )
}

export default App
