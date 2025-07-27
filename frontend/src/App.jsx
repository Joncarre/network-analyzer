import { useState } from 'react'
import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import HomePage from './pages/HomePage'
import CapturePage from './pages/CapturePage'
import AnalysisPage from './pages/AnalysisPage'

function App() {
  return (
    <div className="min-h-screen bg-gray-900">
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/capture" element={<CapturePage />} />
          <Route path="/analysis" element={<AnalysisPage />} />
        </Routes>
      </div>
    </div>
  )
}

export default App
