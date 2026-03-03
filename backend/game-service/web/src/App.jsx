import { useState, useEffect } from 'react'
import { useGameSocket } from './useGameSocket'
import Board from './Board'
import './App.css'

const EMPTY_BOARD = [['', '', ''], ['', '', ''], ['', '', '']]

function getSessionFromURL() {
  const path = window.location.pathname
  const match = path.match(/^\/game\/(.+)$/)
  return match ? match[1] : null
}

function Lobby() {
  const [playerName, setPlayerName] = useState('')
  const [joinId, setJoinId] = useState('')

  const createGame = (e) => {
    e.preventDefault()
    if (!playerName.trim()) return
    const id = crypto.randomUUID()
    window.location.href = `/game/${id}?player=${encodeURIComponent(playerName.trim())}`
  }

  const joinGame = (e) => {
    e.preventDefault()
    if (!playerName.trim() || !joinId.trim()) return
    window.location.href = `/game/${joinId.trim()}?player=${encodeURIComponent(playerName.trim())}`
  }

  return (
    <div className="lobby">
      <div className="input-group">
        <label>Your Name</label>
        <input
          value={playerName}
          onChange={(e) => setPlayerName(e.target.value)}
          placeholder="player name"
          autoFocus
        />
      </div>

      <form onSubmit={createGame} className="lobby-action">
        <button type="submit" className="btn btn--primary" disabled={!playerName.trim()}>
          Create New Game
        </button>
      </form>

      <div className="divider">or join existing</div>

      <form onSubmit={joinGame} className="lobby-action">
        <div className="input-group">
          <label>Session ID</label>
          <input
            value={joinId}
            onChange={(e) => setJoinId(e.target.value)}
            placeholder="paste session id"
          />
        </div>
        <button type="submit" className="btn btn--secondary" disabled={!playerName.trim() || !joinId.trim()}>
          Join Game
        </button>
      </form>
    </div>
  )
}

function Game({ sessionId, initialPlayer }) {
  const [playerInput, setPlayerInput] = useState(initialPlayer || '')

  const {
    connected,
    gameState,
    gameOver,
    error,
    events,
    playerId,
    winningLine,
    connect,
    sendMove,
    disconnect,
  } = useGameSocket(sessionId)

  useEffect(() => {
    if (initialPlayer && !connected) {
      connect(initialPlayer)
    }
  }, [initialPlayer])

  const handleJoin = (e) => {
    e.preventDefault()
    if (!playerInput.trim()) return
    connect(playerInput.trim())
  }

  const board = gameState?.board || EMPTY_BOARD
  const state = gameState?.state || 'waiting'
  const mySymbol = gameState?.players?.find((p) => p.id === playerId)?.symbol
  const isMyTurn = gameState?.current_turn === playerId

  const getStatusText = () => {
    if (gameOver) {
      if (gameOver.winner_id === playerId) return '🎉 You won!'
      return `💀 You lost! (${gameOver.reason})`
    }
    if (state === 'waiting') return '⏳ Waiting for opponent...'
    if (isMyTurn) return '🟢 Your turn'
    return '🔴 Opponent\'s turn'
  }

  const handleDisconnect = () => {
    disconnect()
    window.location.href = '/'
  }

  const copyLink = () => {
    navigator.clipboard.writeText(window.location.origin + `/game/${sessionId}`)
  }

  return (
    <div className="game">
      {!connected ? (
        <form className="join-form" onSubmit={handleJoin}>
          <p className="session-info">Session: <code>{sessionId}</code></p>
          <div className="input-group">
            <label>Your Name</label>
            <input
              value={playerInput}
              onChange={(e) => setPlayerInput(e.target.value)}
              placeholder="player name"
              autoFocus
            />
          </div>
          <button type="submit" className="btn btn--primary">Join Game</button>
        </form>
      ) : (
        <>
          <div className="game-info">
            <span className="badge badge--connected">Connected</span>
            <span className="badge">Player: <strong>{playerId}</strong></span>
            {mySymbol && <span className={`badge badge--${mySymbol.toLowerCase()}`}>Symbol: {mySymbol}</span>}
            <button className="badge badge--copy" onClick={copyLink} title="Copy invite link">
              📋 Copy Link
            </button>
          </div>

          <div className="status">{getStatusText()}</div>

          {error && <div className="error">{error}</div>}

          <Board
            board={board}
            onCellClick={sendMove}
            disabled={!!gameOver || state !== 'playing'}
            currentTurn={gameState?.current_turn}
            playerId={playerId}
            removedPiece={gameState?.removed_piece}
            winningLine={winningLine}
          />

          <button className="btn btn--secondary" onClick={handleDisconnect}>
            Leave Game
          </button>

          <details className="event-log">
            <summary>Event Log ({events.length})</summary>
            <div className="events">
              {events.map((ev, i) => (
                <div key={i} className="event">
                  <span className="event-type">[{ev.type}]</span>
                  <span>{ev.message || JSON.stringify(ev.data)}</span>
                </div>
              ))}
            </div>
          </details>
        </>
      )}
    </div>
  )
}

export default function App() {
  const sessionId = getSessionFromURL()
  const params = new URLSearchParams(window.location.search)
  const initialPlayer = params.get('player')

  return (
    <div className="app">
      <h1>Tic Tac Infinity</h1>
      <p className="subtitle">WebSocket Test Client</p>

      {sessionId ? (
        <Game sessionId={sessionId} initialPlayer={initialPlayer} />
      ) : (
        <Lobby />
      )}
    </div>
  )
}
