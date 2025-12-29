import { useState, useEffect, useRef } from 'react'
import './BingoCardGenerator.css'

const GRID_SIZE = 5
const FREE_SPACE_ROW = 2
const FREE_SPACE_COL = 2

// Seeded random number generator
function seededRandom(seed) {
  let value = seed
  return function() {
    value = (value * 9301 + 49297) % 233280
    return value / 233280
  }
}

function seededShuffle(array, seed) {
  const random = seededRandom(seed)
  const shuffled = [...array]
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(random() * (i + 1))
    ;[shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]
  }
  return shuffled
}

// Convert square key (e.g., "square_0_0.png") to index (0-24)
function squareKeyToIndex(squareKey) {
  const match = squareKey.match(/square_(\d+)_(\d+)\.png/)
  if (match) {
    const row = parseInt(match[1])
    const col = parseInt(match[2])
    return row * 5 + col
  }
  return null
}

// Convert index (0-24) to square key
function indexToSquareKey(index) {
  const row = Math.floor(index / 5)
  const col = index % 5
  return `square_${row}_${col}.png`
}

// Encode highlighted squares as a bitmask (25 bits = one number)
function encodeHighlights(highlightedSquares) {
  if (highlightedSquares.size === 0) return ''
  
  let bitmask = 0
  highlightedSquares.forEach(squareKey => {
    const index = squareKeyToIndex(squareKey)
    if (index !== null && index >= 0 && index < 25) {
      bitmask |= (1 << index)
    }
  })
  
  // Convert number to base36 string (0-9, a-z) for compact encoding
  // Base36 is more efficient than base64 for numbers
  return bitmask.toString(36)
}

// Decode base36 string to highlighted squares set
function decodeHighlights(encoded) {
  if (!encoded) return new Set()
  
  try {
    // Parse base36 string to number
    const bitmask = parseInt(encoded, 36)
    
    const highlighted = new Set()
    for (let i = 0; i < 25; i++) {
      if (bitmask & (1 << i)) {
        const squareKey = indexToSquareKey(i)
        highlighted.add(squareKey)
      }
    }
    
    return highlighted
  } catch (e) {
    console.error('Failed to decode highlights:', e)
    return new Set()
  }
}

function BingoCardGenerator() {
  const [backgroundImage, setBackgroundImage] = useState(null)
  const [squares, setSquares] = useState([])
  const [metadata, setMetadata] = useState(null)
  const [isLoading, setIsLoading] = useState(true)
  const [currentCard, setCurrentCard] = useState(null)
  const [highlightedSquares, setHighlightedSquares] = useState(new Set())
  const [winningSquares, setWinningSquares] = useState(new Set())
  const [currentShuffledSquares, setCurrentShuffledSquares] = useState(null)
  const [playerName, setPlayerName] = useState('')
  const [movieName, setMovieName] = useState('')
  const [showWarningModal, setShowWarningModal] = useState(false)
  const canvasRef = useRef(null)

  // Load state from URL on mount and load assets
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const urlName = params.get('name')
    const urlMovie = params.get('movie')
    const urlHighlights = params.get('h') // Use 'h' for highlights (shorter)
    
    if (urlName) setPlayerName(urlName)
    if (urlMovie) setMovieName(urlMovie)
    if (urlHighlights) {
      const decoded = decodeHighlights(urlHighlights)
      setHighlightedSquares(decoded)
    }
    
    // Load assets - this will generate the card automatically
    loadAssets()
  }, [])
  
  // Regenerate card when assets are loaded and URL params exist
  useEffect(() => {
    if (backgroundImage && squares.length && metadata) {
      const params = new URLSearchParams(window.location.search)
      const urlName = params.get('name')
      const urlMovie = params.get('movie')
      const urlHighlights = params.get('h')
      
      if (urlName && urlMovie) {
        const seed = generateSeed(urlName, urlMovie)
        const highlights = urlHighlights ? decodeHighlights(urlHighlights) : new Set()
        generateCard(backgroundImage, squares, metadata, highlights, false, seed)
        const winning = checkBingo(highlights, metadata)
        setWinningSquares(winning)
      } else if (!urlName && !urlMovie) {
        // Generate random card if no URL params
        const seed = Math.floor(Math.random() * 1000000)
        generateCard(backgroundImage, squares, metadata, new Set(), false, seed)
        setWinningSquares(new Set())
      }
    }
  }, [backgroundImage, squares, metadata])
  
  // Update URL when state changes
  useEffect(() => {
    if (playerName && movieName) {
      const params = new URLSearchParams()
      params.set('name', playerName)
      params.set('movie', movieName)
      
      if (highlightedSquares.size > 0) {
        const encoded = encodeHighlights(highlightedSquares)
        params.set('h', encoded) // Use 'h' for highlights (shorter)
      }
      
      const newUrl = `${window.location.pathname}?${params.toString()}`
      window.history.replaceState({}, '', newUrl)
    }
  }, [playerName, movieName, highlightedSquares])

  const loadAssets = async () => {
    try {
      // Get base path from vite config (for GitHub Pages deployment)
      // BASE_URL already includes trailing slash when set in vite.config.js
      const basePath = import.meta.env.BASE_URL || '/'
      
      // Helper to construct asset URLs
      // In production with base path, public folder files are at the root of the served directory
      // So we need to use the base path prefix
      const getAssetUrl = (path) => {
        // Remove leading slash from path if present
        const cleanPath = path.startsWith('/') ? path.slice(1) : path
        // Ensure basePath ends with / and path doesn't start with /
        const normalizedBase = basePath.endsWith('/') ? basePath : `${basePath}/`
        // Construct the full path
        const fullPath = `${normalizedBase}${cleanPath}`
        return fullPath
      }
      
      // Try multiple path strategies to find the assets
      const tryLoadMetadata = async () => {
        const pathsToTry = [
          getAssetUrl('squares/metadata.json'), // With base path
          '/squares/metadata.json', // Without base path (root)
          './squares/metadata.json', // Relative
          'squares/metadata.json', // Just the path
        ]
        
        for (const path of pathsToTry) {
          try {
            console.log('Trying to load metadata from:', path)
            const response = await fetch(path)
            if (response.ok) {
              console.log('Successfully loaded metadata from:', path)
              return response
            }
          } catch (e) {
            console.log('Failed to load from:', path, e)
            continue
          }
        }
        throw new Error('Failed to load metadata from all attempted paths')
      }
      
      const metadataResponse = await tryLoadMetadata()
      if (!metadataResponse.ok) {
        throw new Error(`Failed to load metadata: ${metadataResponse.status} ${metadataResponse.statusText}`)
      }
      const metadataData = await metadataResponse.json()
      setMetadata(metadataData)
      
      console.log('Loaded metadata:', metadataData)

      // Load the original full image as background
      // We'll place squares on top at their exact extraction positions
      const bgImg = new Image()
      bgImg.crossOrigin = 'anonymous'
      bgImg.src = getAssetUrl('unnamed.webp')  // Use original image
      
      await new Promise((resolve, reject) => {
        bgImg.onload = () => {
          console.log('Background loaded:', bgImg.width, 'x', bgImg.height)
          resolve()
        }
        bgImg.onerror = (err) => {
          console.error('Failed to load background image:', err)
          reject(err)
        }
      })

      setBackgroundImage(bgImg)

      // Load all squares from /squares folder
      const squareImages = []
      for (let row = 0; row < GRID_SIZE; row++) {
        for (let col = 0; col < GRID_SIZE; col++) {
          const img = new Image()
          img.crossOrigin = 'anonymous'
          const squarePath = getAssetUrl(`squares/square_${row}_${col}.png`)
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
      
      // Always generate a card after loading assets
      const params = new URLSearchParams(window.location.search)
      const urlName = params.get('name')
      const urlMovie = params.get('movie')
      
      if (bgImg && squareImages.length && metadataData) {
        let seed
        let initialHighlights = new Set()
        
        if (urlName && urlMovie) {
          // Use URL parameters if they exist
          const combined = `${urlName.toLowerCase().trim()}_${urlMovie.toLowerCase().trim()}`
          let hash = 0
          for (let i = 0; i < combined.length; i++) {
            const char = combined.charCodeAt(i)
            hash = ((hash << 5) - hash) + char
            hash = hash & hash
          }
          seed = Math.abs(hash)
          
          // Get highlights from URL
          const urlHighlights = params.get('h')
          if (urlHighlights) {
            initialHighlights = decodeHighlights(urlHighlights)
          }
        } else {
          // Generate a random example card with a random seed
          // Don't set the input fields, just generate a random card
          seed = Math.floor(Math.random() * 1000000)
        }
        
        // Generate card with seed and highlights
        generateCard(bgImg, squareImages, metadataData, initialHighlights, false, seed)
        
        // Check for bingo with initial highlights
        const winning = checkBingo(initialHighlights, metadataData)
        setWinningSquares(winning)
      }
    } catch (error) {
      console.error('Error loading assets:', error)
      setIsLoading(false)
    }
  }

  const generateSeed = (name, movie) => {
    // Create a seed from the name and movie strings
    const combined = `${name.toLowerCase().trim()}_${movie.toLowerCase().trim()}`
    let hash = 0
    for (let i = 0; i < combined.length; i++) {
      const char = combined.charCodeAt(i)
      hash = ((hash << 5) - hash) + char
      hash = hash & hash // Convert to 32-bit integer
    }
    return Math.abs(hash)
  }

  const checkBingo = (highlighted, metadataData) => {
    // Convert highlighted set to grid positions
    const grid = Array(5).fill(null).map(() => Array(5).fill(false))
    
    // Mark highlighted squares (free space is always considered highlighted)
    for (let row = 0; row < GRID_SIZE; row++) {
      for (let col = 0; col < GRID_SIZE; col++) {
        const squareKey = `square_${row}_${col}.png`
        if (row === FREE_SPACE_ROW && col === FREE_SPACE_COL) {
          // Free space is always marked
          grid[row][col] = true
        } else if (highlighted.has(squareKey)) {
          grid[row][col] = true
        }
      }
    }

    const winning = new Set()

    // Check horizontal lines
    for (let row = 0; row < GRID_SIZE; row++) {
      if (grid[row].every(cell => cell === true)) {
        // All 5 in this row are highlighted
        for (let col = 0; col < GRID_SIZE; col++) {
          const squareKey = `square_${row}_${col}.png`
          winning.add(squareKey)
        }
      }
    }

    // Check vertical lines
    for (let col = 0; col < GRID_SIZE; col++) {
      let allHighlighted = true
      for (let row = 0; row < GRID_SIZE; row++) {
        if (!grid[row][col]) {
          allHighlighted = false
          break
        }
      }
      if (allHighlighted) {
        // All 5 in this column are highlighted
        for (let row = 0; row < GRID_SIZE; row++) {
          const squareKey = `square_${row}_${col}.png`
          winning.add(squareKey)
        }
      }
    }

    // Check diagonal (top-left to bottom-right)
    let diagonal1 = true
    for (let i = 0; i < GRID_SIZE; i++) {
      if (!grid[i][i]) {
        diagonal1 = false
        break
      }
    }
    if (diagonal1) {
      for (let i = 0; i < GRID_SIZE; i++) {
        const squareKey = `square_${i}_${i}.png`
        winning.add(squareKey)
      }
    }

    // Check diagonal (top-right to bottom-left)
    let diagonal2 = true
    for (let i = 0; i < GRID_SIZE; i++) {
      if (!grid[i][GRID_SIZE - 1 - i]) {
        diagonal2 = false
        break
      }
    }
    if (diagonal2) {
      for (let i = 0; i < GRID_SIZE; i++) {
        const squareKey = `square_${i}_${GRID_SIZE - 1 - i}.png`
        winning.add(squareKey)
      }
    }

    return winning
  }

  const generateCard = (bgImg, squareImages, metadataData, highlights = highlightedSquares, preserveShuffle = false, seed = null) => {
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
    let shuffledSquares
    if (preserveShuffle && currentShuffledSquares && currentShuffledSquares.length === otherSquares.length) {
      // Reuse existing shuffle when preserving (for highlight updates)
      shuffledSquares = currentShuffledSquares
    } else {
      // Create new shuffle using seed if provided
      if (seed !== null) {
        shuffledSquares = seededShuffle(otherSquares, seed)
      } else {
        // Fallback to random shuffle if no seed
        shuffledSquares = seededShuffle(otherSquares, Math.random() * 1000000)
      }
      setCurrentShuffledSquares(shuffledSquares)
    }

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

    // Check for bingo and get winning squares
    const winning = checkBingo(highlights, metadataData)
    
    // Draw highlight circles for clicked squares
    highlights.forEach(squareKey => {
      const squareInfo = metadataData.squares[squareKey]
      if (squareInfo && squareInfo.extraction_bounds) {
        const [extractLeft, extractTop, extractRight, extractBottom] = squareInfo.extraction_bounds
        const centerX = (extractLeft + extractRight) / 2
        const centerY = (extractTop + extractBottom) / 2
        const radius = Math.min((extractRight - extractLeft), (extractBottom - extractTop)) / 2 - 5
        
        // Draw green circle if it's part of a winning line, red otherwise
        ctx.save()
        ctx.globalAlpha = 0.4
        ctx.fillStyle = winning.has(squareKey) ? 'green' : 'red'
        ctx.beginPath()
        ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI)
        ctx.fill()
        ctx.restore()
      }
    })
    
    // Also highlight free space if it's part of a winning line
    const freeSpaceKey = `square_${FREE_SPACE_ROW}_${FREE_SPACE_COL}.png`
    if (winning.has(freeSpaceKey)) {
      const squareInfo = metadataData.squares[freeSpaceKey]
      if (squareInfo && squareInfo.extraction_bounds) {
        const [extractLeft, extractTop, extractRight, extractBottom] = squareInfo.extraction_bounds
        const centerX = (extractLeft + extractRight) / 2
        const centerY = (extractTop + extractBottom) / 2
        const radius = Math.min((extractRight - extractLeft), (extractBottom - extractTop)) / 2 - 5
        
        ctx.save()
        ctx.globalAlpha = 0.4
        ctx.fillStyle = 'green'
        ctx.beginPath()
        ctx.arc(centerX, centerY, radius, 0, 2 * Math.PI)
        ctx.fill()
        ctx.restore()
      }
    }

    // Convert canvas to image data URL
    const dataUrl = canvas.toDataURL('image/png')
    setCurrentCard(dataUrl)
  }

  const handleGenerate = () => {
    if (!playerName.trim() || !movieName.trim()) {
      alert('Please enter both your name and the movie name')
      return
    }
    
    // Warn if there are highlighted squares
    if (highlightedSquares.size > 0) {
      setShowWarningModal(true)
      return
    }
    
    // Proceed with generation
    proceedWithGeneration()
  }

  const proceedWithGeneration = () => {
    setShowWarningModal(false)
    
    if (backgroundImage && squares.length && metadata) {
      // Clear highlights and winning squares when generating new card
      setHighlightedSquares(new Set())
      setWinningSquares(new Set())
      
      // Generate seed from name and movie
      const seed = generateSeed(playerName, movieName)
      
      // Generate new card with seeded shuffle
      generateCard(backgroundImage, squares, metadata, new Set(), false, seed)
    }
  }

  const handleCanvasClick = (e) => {
    if (!metadata || !currentCard) return

    const img = e.currentTarget
    const rect = img.getBoundingClientRect()
    
    // Calculate click position relative to the actual image dimensions
    const scaleX = img.naturalWidth / rect.width
    const scaleY = img.naturalHeight / rect.height
    
    const x = (e.clientX - rect.left) * scaleX
    const y = (e.clientY - rect.top) * scaleY

    // Find which square was clicked
    for (let row = 0; row < GRID_SIZE; row++) {
      for (let col = 0; col < GRID_SIZE; col++) {
        const squareKey = `square_${row}_${col}.png`
        const squareInfo = metadata.squares[squareKey]
        
        if (squareInfo && squareInfo.extraction_bounds) {
          const [extractLeft, extractTop, extractRight, extractBottom] = squareInfo.extraction_bounds
          
          if (x >= extractLeft && x <= extractRight && y >= extractTop && y <= extractBottom) {
            // Toggle highlight
            const newHighlighted = new Set(highlightedSquares)
            if (newHighlighted.has(squareKey)) {
              newHighlighted.delete(squareKey)
            } else {
              newHighlighted.add(squareKey)
            }
            setHighlightedSquares(newHighlighted)
            
            // Check for bingo
            const winning = checkBingo(newHighlighted, metadata)
            setWinningSquares(winning)
            
            // Regenerate card with updated highlights (preserve shuffle)
            if (backgroundImage && squares.length) {
              generateCard(backgroundImage, squares, metadata, newHighlighted, true)
            }
            return // Exit early after finding the clicked square
          }
        }
      }
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
      {showWarningModal && (
        <div className="modal-overlay" onClick={() => setShowWarningModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>⚠️ Warning</h2>
            <p>
              You have <strong>{highlightedSquares.size}</strong> square(s) marked.
              Generating a new card will clear all your marks.
            </p>
            <p>Do you want to continue?</p>
            <div className="modal-buttons">
              <button 
                className="modal-btn modal-btn-cancel" 
                onClick={() => setShowWarningModal(false)}
              >
                Cancel
              </button>
              <button 
                className="modal-btn modal-btn-confirm" 
                onClick={proceedWithGeneration}
              >
                Continue
              </button>
            </div>
          </div>
        </div>
      )}
      <div className="controls">
        <div className="input-group">
          <label htmlFor="player-name">Your Name:</label>
          <input
            id="player-name"
            type="text"
            value={playerName}
            onChange={(e) => setPlayerName(e.target.value)}
            placeholder="Enter your name"
            className="name-input"
          />
        </div>
        <div className="input-group">
          <label htmlFor="movie-name">Movie Name:</label>
          <input
            id="movie-name"
            type="text"
            value={movieName}
            onChange={(e) => setMovieName(e.target.value)}
            placeholder="Enter movie name"
            className="name-input"
          />
        </div>
        <button 
          onClick={handleGenerate} 
          className="generate-btn"
          disabled={!playerName.trim() || !movieName.trim()}
        >
          🎲 Generate
        </button>
        {currentCard && (
          <button onClick={handleDownload} className="download-btn">
            💾 Download
          </button>
        )}
      </div>

      <div className="card-container">
        <canvas 
          ref={canvasRef} 
          style={{ display: 'none' }} 
        />
        {currentCard && (
          <img 
            src={currentCard} 
            alt="Generated Bingo Card" 
            className="bingo-card"
            onClick={handleCanvasClick}
            style={{ cursor: 'pointer' }}
          />
        )}
      </div>
    </div>
  )
}

export default BingoCardGenerator

