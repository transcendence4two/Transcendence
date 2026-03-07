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

    const [userId] = useState<string | null>(() => {
        const userData = localStorage.getItem('user')
        if (userData) {
            try {
                const parsed = JSON.parse(userData)
                return parsed.id || parsed.username || null
            } catch {
                return null
            }
        }
        return null
    })

    const {
        connected,
        reconnecting,
        opponentDisconnected,
        opponentReconnected,
        gameState,
        gameOver,
        roundOver,
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
    const round = gameState?.round || 1
    const score = gameState?.score || [0, 0]

    const getPlayerLabel = (index: number) => {
        const player = gameState?.players?.[index]
        if (!player) return `Player ${index + 1}`
        const isMe = player.id === playerId
        return isMe ? 'You' : 'Opponent'
    }

    const getStatusText = () => {
        if (gameOver) {
            if (gameOver.winner_id === playerId) return '🎉 You won the match!'
            return `💀 You lost the match! (${gameOver.reason})`
        }
        if (roundOver) {
            if (roundOver.winner_id === playerId) return '✅ You won this round!'
            return '❌ You lost this round!'
        }
        if (state === 'waiting') return '⏳ Waiting for opponent...'
        if (opponentDisconnected) return '⚠️ Waiting for opponent to reconnect...'
        if (opponentReconnected) return '✅ Opponent reconnected!'
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

                    {reconnecting && (
                        <div className="game-error" style={{ marginBottom: '1rem', background: 'rgba(234, 179, 8, 0.15)', borderColor: 'rgba(234, 179, 8, 0.3)', color: '#fbbf24' }}>
                            🔄 Connection lost. Reconnecting…
                        </div>
                    )}

                    {!connected && !reconnecting ? (
                        <div>
                            <p className="game-session-info">
                                Session: <code>{sessionId}</code>
                            </p>
                            <p className="game-subtitle">Connecting...</p>
                        </div>
                    ) : connected ? (
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

                            {/* MD3 Scoreboard */}
                            {state !== 'waiting' && (
                                <div className="game-scoreboard">
                                    <span className="game-scoreboard-player">{getPlayerLabel(0)}</span>
                                    <span className="game-scoreboard-score">
                                        {score[0]} — {score[1]}
                                    </span>
                                    <span className="game-scoreboard-player">{getPlayerLabel(1)}</span>
                                    <span className="game-scoreboard-round">Round {round} of 3</span>
                                </div>
                            )}

                            <div className="game-status">{getStatusText()}</div>

                            {error && <div className="game-error">{error}</div>}

                            {/* Opponent disconnected banner */}
                            {opponentDisconnected && !gameOver && (
                                <div className="game-opponent-disconnected">
                                    ⚠️ Opponent disconnected. They have 15s to reconnect or they forfeit.
                                </div>
                            )}

                            {/* Opponent reconnected banner */}
                            {opponentReconnected && !gameOver && (
                                <div className="game-opponent-disconnected" style={{ background: 'rgba(74, 222, 128, 0.10)', borderColor: 'rgba(74, 222, 128, 0.3)', color: '#4ade80' }}>
                                    ✅ Opponent reconnected!
                                </div>
                            )}

                            {/* Round-over overlay */}
                            {roundOver && !gameOver && (
                                <div className="game-round-overlay">
                                    <div className="game-round-overlay-content">
                                        {roundOver.winner_id === playerId
                                            ? '✅ Round won!'
                                            : '❌ Round lost!'}
                                        <span className="game-round-overlay-sub">Next round starting soon…</span>
                                    </div>
                                </div>
                            )}

                            <GameBoard
                                board={board}
                                onCellClick={sendMove}
                                disabled={!!gameOver || !!roundOver || state !== 'playing'}
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
                    ) : null}
                </div>
            </main>
            <Footer />
        </div>
    )
}
