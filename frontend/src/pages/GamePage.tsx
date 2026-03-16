import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import Header from '../components/layout/Header'
import Footer from '../components/layout/Footer'
import GameBoard from '../components/game/GameBoard'
import { useGameSocket } from '../hooks/useGameSocket'

const EMPTY_BOARD = [['', '', ''], ['', '', ''], ['', '', '']]

export default function GamePage() {
    const { sessionId } = useParams<{ sessionId: string }>()
    const navigate = useNavigate()
    const [redirectCountdown, setRedirectCountdown] = useState<number>(3)

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
        playerId,
        winningLine,
        connect,
        sendMove,
        disconnect,
    } = useGameSocket(sessionId || '')

    const [userMap, setUserMap] = useState<Record<string, { username: string; avatarUrl?: string }>>({})

    useEffect(() => {
        if (userId && sessionId && !connected) {
            connect(userId)
        }
    }, [userId, sessionId, connected, connect])

    useEffect(() => {
        const fetchUsernames = async () => {
            const players = gameState?.players || []
            const token = localStorage.getItem('access_token')

            for (const p of players) {
                if (p.id && !userMap[p.id]) {
                    try {
                        const res = await fetch(`/api/users/${p.id}`, {
                            headers: token ? { Authorization: `Bearer ${token}` } : {},
                        })
                        if (res.ok) {
                            const data = await res.json()
                            setUserMap((prev) => ({
                                ...prev,
                                [p.id]: {
                                    username: data.username,
                                    avatarUrl: data.avatar_url
                                }
                            }))
                        }
                    } catch (e) {
                    }
                }
            }
        }
        fetchUsernames()
    }, [gameState?.players]) // eslint-disable-line react-hooks/exhaustive-deps

    useEffect(() => {
        if (!gameOver) return

        const interval = setInterval(() => {
            setRedirectCountdown((prev) => (prev > 0 ? prev - 1 : prev))
        }, 1000)

        const timer = setTimeout(() => {
            disconnect()
            navigate('/home')
        }, 3000)

        return () => {
            clearInterval(interval)
            clearTimeout(timer)
        }
    }, [gameOver, disconnect, navigate])

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
        const pName = userMap[player.id]?.username || (isMe ? 'You' : 'Opponent')
        return pName
    }

    const getStatusText = () => {
        if (gameOver) {
            if (gameOver.winner_id === playerId) return '🎉 You won the match!'
            const winnerName = gameOver.winner_id ? (userMap[gameOver.winner_id]?.username || 'Opponent') : 'Opponent'
            return `💀 ${winnerName} won the match! (${gameOver.reason})`
        }
        if (roundOver) {
            if (roundOver.winner_id === playerId) return '✅ You won this round!'
            return '❌ You lost this round!'
        }
        if (state === 'waiting') return '⏳ Waiting for opponent...'
        if (opponentDisconnected) return '⚠️ Waiting for opponent to reconnect...'
        if (opponentReconnected) return '✅ Opponent reconnected!'
        if (isMyTurn) return '🟢 Your turn'
        const oppName = gameState?.players?.find((p) => p.id !== playerId)?.id
        const displayOppName = oppName ? userMap[oppName]?.username || 'Opponent' : 'Opponent'
        return `🔴 ${displayOppName}'s turn`
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
                            {/* Avatars Container */}
                            <div className="game-avatars-container">
                                {gameState?.players?.map((p, index) => {
                                    const user = userMap[p.id]
                                    const isMe = p.id === playerId
                                    const displayName = user?.username || (isMe ? 'You' : `Player ${index + 1}`)

                                    return (
                                        <div key={p.id} style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                                            {index === 1 && <span className="game-vs-badge">VS</span>}
                                            <div className="game-avatar-wrapper">
                                                <div className="game-avatar-circle">
                                                    {user?.avatarUrl ? (
                                                        <img src={user.avatarUrl} alt={displayName} className="game-avatar-image" />
                                                    ) : (
                                                        displayName.substring(0, 2).toUpperCase()
                                                    )}
                                                </div>
                                                <span className="game-avatar-name" title={displayName}>
                                                    {displayName}
                                                </span>
                                            </div>
                                        </div>
                                    )
                                })}
                            </div>

                            <div className="game-info">
                                <span className="game-badge game-badge--connected">Connected</span>
                                {playerId && (
                                    <span className="game-badge">Player: <strong>{userMap[playerId]?.username || 'You'}</strong></span>
                                )}
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
                                {gameOver
                                    ? `Returning to Dashboard (${redirectCountdown}s)...`
                                    : 'Leave Game'}
                            </button>
                        </>
                    ) : null}
                </div>
            </main>
            <Footer />
        </div>
    )
}
