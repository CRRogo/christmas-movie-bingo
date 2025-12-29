import { useState, useEffect, useRef } from 'react'
import './BingoCardGenerator.css'

const GRID_SIZE = 5
const FREE_SPACE_ROW = 2
const FREE_SPACE_COL = 2

function BingoCardGenerator() {
  const [backgroundImage, setBackgroundImage] = useState(null)
  const [squares, setSquares] = useState([])
  const [metadata, setMetadata] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [currentCard, setCurrentCard] = useState(null)
  const canvasRef = useRef(null)

  // Load all assets
  useEffect(() => {
    loadAssets()
  }, [])

  const loadAssets = async () => {
    try {
      // Load metadata first to get exact dimensions
      const metadataResponse = await fetch('/squares/metadata.json')
      const metadataData = await metadataResponse.json()
      setMetadata(metadataData)
      
      console.log('Loaded metadata:', metadataData)

      // Load the original full image as background
      // We'll place squares on top at their exact extraction positions
      const bgImg = new Image()
      bgImg.crossOrigin = 'anonymous'
      bgImg.src = '/unnamed.webp'  // Use original image
      
      await new Promise((resolve, reject) => {
        bgImg.onload = () => {
          console.log('Background loaded:', bgImg.width, 'x', bgImg.height)
          resolve()
        }
        bgImg.onerror = reject
      })

      setBackgroundImage(bgImg)

      // Load all squares from /squares folder
      const squareImages = []
      for (let row = 0; row < GRID_SIZE; row++) {
        for (let col = 0; col < GRID_SIZE; col++) {
          const img = new Image()
          img.crossOrigin = 'anonymous'
          const squarePath = `/squares/square_${row}_${col}.png`
          img.src = squarePath
          
          await new Promise((resolve, reject) => {
            img.onload = () => {
              console.log(`Loaded square_${row}_${col}.png from ${squarePath}:`, img.width, 'x', img.height)
              squareImages.push({
                image: img,
                row,
                col,
                originalPosition: { row, col },
                filename: `square_${row}_${col}.png`
              })
              resolve()
            }
            img.onerror = (err) => {
              console.error(`Failed to load ${squarePath}:`, err)
              reject(err)
            }
          })
        }
      }
      
      console.log(`Loaded ${squareImages.length} squares total`)
      
      // Verify we have all 25 squares
      if (squareImages.length !== 25) {
        console.error(`Expected 25 squares but loaded ${squareImages.length}`)
      }
      
      // Log all loaded squares for debugging
      squareImages.forEach(sq => {
        console.log(`Square loaded: ${sq.filename} at position (${sq.row}, ${sq.col})`)
      })

      setSquares(squareImages)
      setIsLoading(false)
      
      // Generate initial card
      generateCard(bgImg, squareImages, metadataData)
    } catch (error) {
      console.error('Error loading assets:', error)
      setIsLoading(false)
    }
  }

  const shuffleArray = (array) => {
    const shuffled = [...array]
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]
    }
    return shuffled
  }

  const generateCard = (bgImg, squareImages, metadataData) => {
    if (!bgImg || !squareImages.length || !metadataData) return

    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    
    // Set canvas size to match background
    canvas.width = bgImg.width
    canvas.height = bgImg.height

    // Draw background
    ctx.drawImage(bgImg, 0, 0)

    // Get square dimensions from metadata
    const squareSize = metadataData.square_size
    const squareWidth = squareSize.width
    const squareHeight = squareSize.height
    
    console.log('Using square size:', squareWidth, 'x', squareHeight)

    // Create a map of squares by their original position for easy lookup
    const squaresByPosition = {}
    squareImages.forEach(sq => {
      const key = `${sq.row}_${sq.col}`
      squaresByPosition[key] = sq
    })

    // Separate free space from other squares
    const freeSpace = squaresByPosition[`${FREE_SPACE_ROW}_${FREE_SPACE_COL}`]
    const otherSquares = squareImages.filter(
      sq => !(sq.row === FREE_SPACE_ROW && sq.col === FREE_SPACE_COL)
    )

    // Shuffle other squares
    const shuffledSquares = shuffleArray(otherSquares)

    // Place squares using the EXACT extraction bounds from metadata
    // This ensures perfect alignment with how the squares were extracted
    
    let shuffledIndex = 0
    for (let row = 0; row < GRID_SIZE; row++) {
      for (let col = 0; col < GRID_SIZE; col++) {
        // Get the exact extraction bounds from metadata
        const squareKey = `square_${row}_${col}.png`
        const squareInfo = metadataData.squares[squareKey]
        
        // Use the exact extraction bounds from metadata: [left, top, right, bottom]
        if (!squareInfo || !squareInfo.extraction_bounds) {
          console.error(`Missing extraction bounds for ${squareKey}`)
          continue
        }
        
        // Use the exact extraction bounds: [left, top, right, bottom]
        const [extractLeft, extractTop, extractRight, extractBottom] = squareInfo.extraction_bounds
        
        // Calculate the exact size that was extracted (before resizing)
        // This ensures perfect alignment to cover the original square exactly
        const extractedWidth = extractRight - extractLeft
        const extractedHeight = extractBottom - extractTop
        
        // Place square at exact extraction position with exact extracted dimensions
        // This ensures perfect alignment to cover the original square
        if (row === FREE_SPACE_ROW && col === FREE_SPACE_COL) {
          // Place free space at exact position
          if (freeSpace) {
            ctx.drawImage(freeSpace.image, extractLeft, extractTop, extractedWidth, extractedHeight)
          }
        } else {
          // Place shuffled square at exact position
          if (shuffledIndex < shuffledSquares.length) {
            const squareToPlace = shuffledSquares[shuffledIndex]
            // Use the exact extracted dimensions to ensure perfect coverage
            ctx.drawImage(
              squareToPlace.image, 
              extractLeft, 
              extractTop, 
              extractedWidth, 
              extractedHeight
            )
            shuffledIndex++
          }
        }
      }
    }

    // Convert canvas to image data URL
    const dataUrl = canvas.toDataURL('image/png')
    setCurrentCard(dataUrl)
  }

  const handleGenerate = () => {
    if (backgroundImage && squares.length && metadata) {
      generateCard(backgroundImage, squares, metadata)
    }
  }

  const handleDownload = () => {
    if (!currentCard) return

    const link = document.createElement('a')
    link.download = `bingo-card-${Date.now()}.png`
    link.href = currentCard
    link.click()
  }

  if (isLoading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading bingo card assets...</p>
      </div>
    )
  }

  return (
    <div className="bingo-generator">
      <div className="controls">
        <button onClick={handleGenerate} className="generate-btn">
          🎲 Generate New Card
        </button>
        {currentCard && (
          <button onClick={handleDownload} className="download-btn">
            💾 Download Card
          </button>
        )}
      </div>

      <div className="card-container">
        <canvas ref={canvasRef} style={{ display: 'none' }} />
        {currentCard && (
          <img 
            src={currentCard} 
            alt="Generated Bingo Card" 
            className="bingo-card"
          />
        )}
      </div>
    </div>
  )
}

export default BingoCardGenerator

