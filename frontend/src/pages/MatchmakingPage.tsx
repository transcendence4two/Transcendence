import { useEffect, useState, useRef, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import Header from '../components/layout/Header'
import Footer from '../components/layout/Footer'
import '../components/game/game.css'

const POLLING_INTERVAL_MS = 2500

interface UserData {
    id: string
    username: string
}

type MatchmakingState = 'joining' | 'queued' | 'matched' | 'error'

function getUser(): UserData | null {
    const raw = localStorage.getItem('user')
    if (!raw) return null
    try {
        return JSON.parse(raw)
    } catch {
        return null
    }
}

export default function MatchmakingPage() {
    const navigate = useNavigate()
    const [state, setState] = useState<MatchmakingState>('joining')
    const [errorMessage, setErrorMessage] = useState<string | null>(null)
    const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null)
    const user = useRef(getUser())

    const stopPolling = useCallback(() => {
        if (pollingRef.current) {
            clearInterval(pollingRef.current)
            pollingRef.current = null
        }
    }, [])

    const pollStatus = useCallback(async () => {
        if (!user.current) return
        const token = localStorage.getItem('access_token')
        try {
            const res = await fetch(
                `/api/tournaments/matchmaking/status/${user.current.id}`,
                { headers: { Authorization: `Bearer ${token}` } },
            )
            if (!res.ok) return

            const data = await res.json()

            if (data.status === 'matched' && data.game_session_id) {
                stopPolling()
                setState('matched')
                setTimeout(() => navigate(`/game/${data.game_session_id}`), 600)
            }
        } catch {
            // Silently retry on next poll
        }
    }, [navigate, stopPolling])

    const joinQueue = useCallback(async () => {
        if (!user.current) {
            navigate('/login', { replace: true })
            return
        }

        const token = localStorage.getItem('access_token')
        setState('joining')
        setErrorMessage(null)

        try {
            const res = await fetch('/api/tournaments/join', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({
                    user_id: user.current.id,
                    display_name: user.current.username,
                }),
            })

            if (!res.ok) {
                const data = await res.json().catch(() => ({}))
                throw new Error(data.detail || 'Failed to join matchmaking')
            }

            const entry = await res.json()

            if (entry.status === 'matched' && entry.game_session_id) {
                setState('matched')
                setTimeout(() => navigate(`/game/${entry.game_session_id}`), 600)
                return
            }

            setState('queued')
            pollingRef.current = setInterval(pollStatus, POLLING_INTERVAL_MS)
        } catch (err: unknown) {
            setState('error')
            setErrorMessage(
                err instanceof Error ? err.message : 'Something went wrong',
            )
        }
    }, [navigate, pollStatus])

    useEffect(() => {
        joinQueue()
        return stopPolling
    }, [joinQueue, stopPolling])

    const handleCancel = () => {
        stopPolling()
        navigate('/home')
    }

    return (
        <div className="container-main">
            <Header />
            <main
                className="content-main"
                style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    padding: '2rem 1rem',
                }}
            >
                <div className="game-container">
                    <h1 className="game-title">Tic Tac Infinity</h1>

                    {state === 'joining' && (
                        <div style={{ textAlign: 'center' }}>
                            <div className="matchmaking-spinner" />
                            <p className="game-subtitle" style={{ marginTop: '1.5rem' }}>
                                Entering matchmaking queue…
                            </p>
                        </div>
                    )}

                    {state === 'queued' && (
                        <div style={{ textAlign: 'center' }}>
                            <div className="matchmaking-spinner" />
                            <p
                                className="game-status"
                                style={{ color: '#818cf8', marginTop: '1.5rem' }}
                            >
                                🔍 Looking for an opponent…
                            </p>
                            <p className="game-subtitle">
                                Please wait while we find a worthy challenger
                            </p>
                            <button
                                type="button"
                                className="game-btn game-btn--secondary"
                                onClick={handleCancel}
                            >
                                Cancel
                            </button>
                        </div>
                    )}

                    {state === 'matched' && (
                        <div style={{ textAlign: 'center' }}>
                            <p
                                className="game-status"
                                style={{ color: '#4ade80', fontSize: '1.25rem' }}
                            >
                                ✅ Opponent found!
                            </p>
                            <p className="game-subtitle">
                                Redirecting to the game…
                            </p>
                        </div>
                    )}

                    {state === 'error' && (
                        <div style={{ textAlign: 'center' }}>
                            <div className="game-error" style={{ marginBottom: '1rem' }}>
                                {errorMessage}
                            </div>
                            <button
                                type="button"
                                className="game-btn game-btn--primary"
                                onClick={joinQueue}
                            >
                                Try Again
                            </button>
                            <button
                                type="button"
                                className="game-btn game-btn--secondary"
                                onClick={handleCancel}
                            >
                                Back to Dashboard
                            </button>
                        </div>
                    )}
                </div>
            </main>
            <Footer />
        </div>
    )
}
