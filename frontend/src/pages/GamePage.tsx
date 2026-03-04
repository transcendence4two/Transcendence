import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Header from '../components/layout/Header'
import Footer from '../components/layout/Footer'
import GameBoard from '../components/game/GameBoard'
import { useGameSocket } from '../hooks/useGameSocket'
import '../components/game/game.css'

const EMPTY_BOARD = [['', '', ''], ['', '', ''], ['', '', '']]

export default function GamePage() {
    const { sessionId } = useParams<{ sessionId: string }>()
    const navigate = useNavigate()

    const [userId, setUserId] = useState<string | null>(null)

    useEffect(() => {
        const userData = localStorage.getItem('user')
        if (userData) {
            try {
                const parsed = JSON.parse(userData)
                setUserId(parsed.id || parsed.username || null)
            } catch {
                setUserId(null)
            }
        }
    }, [])

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
    } = useGameSocket(sessionId || '')

    useEffect(() => {
        if (userId && sessionId && !connected) {
            connect(userId)
        }
    }, [userId, sessionId, connected, connect])

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
        return "🔴 Opponent's turn"
    }

    const handleDisconnect = () => {
        disconnect()
        navigate('/home')
    }

    const copyLink = () => {
        navigator.clipboard.writeText(window.location.href)
    }

    if (!sessionId) {
        navigate('/home')
        return null
    }

    return (
        <div className="container-main">
            <Header />
            <main className="content-main" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem 1rem' }}>
                <div className="game-container">
                    <h1 className="game-title">Tic Tac Infinity</h1>

                    {!connected ? (
                        <div>
                            <p className="game-session-info">
                                Session: <code>{sessionId}</code>
                            </p>
                            <p className="game-subtitle">Connecting...</p>
                        </div>
                    ) : (
                        <>
                            <div className="game-info">
                                <span className="game-badge game-badge--connected">Connected</span>
                                <span className="game-badge">Player: <strong>{playerId}</strong></span>
                                {mySymbol && (
                                    <span className={`game-badge game-badge--${mySymbol.toLowerCase()}`}>
                                        Symbol: {mySymbol}
                                    </span>
                                )}
                                <button className="game-badge game-badge--copy" onClick={copyLink} title="Copy invite link">
                                    📋 Copy Link
                                </button>
                            </div>

                            <div className="game-status">{getStatusText()}</div>

                            {error && <div className="game-error">{error}</div>}

                            <GameBoard
                                board={board}
                                onCellClick={sendMove}
                                disabled={!!gameOver || state !== 'playing'}
                                currentTurn={gameState?.current_turn}
                                playerId={playerId}
                                removedPiece={gameState?.removed_piece}
                                nextRemovedPiece={gameState?.next_removed_piece}
                                winningLine={winningLine}
                            />

                            <button className="game-btn game-btn--secondary" onClick={handleDisconnect}>
                                Leave Game
                            </button>

                            <details className="game-event-log">
                                <summary>Event Log ({events.length})</summary>
                                <div className="game-events">
                                    {events.map((ev, i) => (
                                        <div key={i} className="game-event">
                                            <span className="game-event-type">[{ev.type}]</span>
                                            <span>{ev.message || JSON.stringify(ev.data)}</span>
                                        </div>
                                    ))}
                                </div>
                            </details>
                        </>
                    )}
                </div>
            </main>
            <Footer />
        </div>
    )
}
