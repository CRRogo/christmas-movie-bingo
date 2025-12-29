import { useState, useEffect } from 'react'
import BingoCardGenerator from './components/BingoCardGenerator'
import './App.css'

function App() {
  return (
    <div className="app">
      <main>
        <BingoCardGenerator />
      </main>
    </div>
  )
}

export default App

