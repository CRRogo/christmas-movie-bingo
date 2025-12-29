import { useState, useEffect } from 'react'
import BingoCardGenerator from './components/BingoCardGenerator'
import './App.css'

function App() {
  return (
    <div className="app">
      <header className="app-header">
        <h1>🎄 Hallmark Christmas Bingo Generator 🎄</h1>
        <p className="subtitle">Generate your own randomized bingo cards!</p>
      </header>
      <main>
        <BingoCardGenerator />
      </main>
    </div>
  )
}

export default App

