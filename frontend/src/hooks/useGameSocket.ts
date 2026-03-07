import { useState, useRef, useCallback, useEffect } from 'react'

interface Player {
    id: string
    symbol: string
}

interface RemovedPiece {
    row: number
    col: number
}

export interface GameState {
    board: string[][]
    state: 'waiting' | 'playing' | 'finished'
    players: Player[]
    current_turn: string
    removed_piece?: RemovedPiece
    next_removed_piece?: RemovedPiece
    round: number
    score: [number, number]
    disconnected_players?: string[]
}

interface WinningCell {
    row: number
    col: number
}

export interface GameOver {
    winner_id: string
    reason: string
    winning_line?: WinningCell[]
    score: [number, number]
}

export interface RoundOver {
    winner_id: string
    reason: string
    winning_line?: WinningCell[]
    round: number
    score: [number, number]
}

interface GameEvent {
    type: string
    message?: string
    data?: unknown
}

interface WebSocketMessage {
    type: string
    payload: Record<string, unknown>
}

const MAX_RECONNECT_ATTEMPTS = 5
const BASE_RECONNECT_DELAY_MS = 1000

export function useGameSocket(sessionId: string) {
    const [connected, setConnected] = useState(false)
    const [gameState, setGameState] = useState<GameState | null>(null)
    const [gameOver, setGameOver] = useState<GameOver | null>(null)
    const [roundOver, setRoundOver] = useState<RoundOver | null>(null)
    const [error, setError] = useState<string | null>(null)
    const [events, setEvents] = useState<GameEvent[]>([])
    const [playerId, setPlayerId] = useState<string | null>(null)
    const [winningLine, setWinningLine] = useState<WinningCell[] | null>(null)
    const [reconnecting, setReconnecting] = useState(false)
    const [opponentDisconnected, setOpponentDisconnected] = useState(false)
    const [opponentReconnected, setOpponentReconnected] = useState(false)
    const wsRef = useRef<WebSocket | null>(null)
    const reconnectAttemptRef = useRef(0)
    const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)
    const intentionalCloseRef = useRef(false)
    const playerIdRef = useRef<string | null>(null)

    const addEvent = useCallback((event: GameEvent) => {
        setEvents((prev) => [...prev.slice(-49), event])
    }, [])

    const connectWsRef = useRef<((pid: string, isReconnect?: boolean) => void) | null>(null)

    const connectWs = useCallback((pid: string, isReconnect = false) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) return

        if (!isReconnect) {
            setPlayerId(pid)
            playerIdRef.current = pid
            setError(null)
            setGameOver(null)
            setRoundOver(null)
            setGameState(null)
            setWinningLine(null)
            setOpponentDisconnected(false)
            intentionalCloseRef.current = false
            reconnectAttemptRef.current = 0
        }

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const host = window.location.host
        const ws = new WebSocket(`${protocol}//${host}/ws?session_id=${sessionId}`)

        ws.onopen = () => {
            setConnected(true)
            setReconnecting(false)
            reconnectAttemptRef.current = 0

            const eventMsg = isReconnect ? 'Reconnected' : 'Connected'
            addEvent({ type: 'system', message: eventMsg })

            ws.send(JSON.stringify({
                type: 'join',
                payload: { player_id: pid },
            }))
        }

        ws.onmessage = (event) => {
            const msg: WebSocketMessage = JSON.parse(event.data)
            addEvent({ type: msg.type, data: msg.payload })

            switch (msg.type) {
                case 'game_state': {
                    const statePayload = msg.payload as unknown as GameState
                    setGameState(statePayload)
                    setRoundOver(null)
                    setWinningLine(null)
                    // Sync opponent disconnection status from server state
                    const dp = statePayload.disconnected_players || []
                    const opponentGone = dp.some((id) => id !== playerIdRef.current)
                    setOpponentDisconnected(opponentGone)
                    if (opponentGone) setOpponentReconnected(false)
                    break
                }
                case 'round_over': {
                    const roPayload = msg.payload as unknown as RoundOver
                    setRoundOver(roPayload)
                    if (roPayload.winning_line) {
                        setWinningLine(roPayload.winning_line)
                    }
                    break
                }
                case 'game_over': {
                    const overPayload = msg.payload as unknown as GameOver
                    setGameOver(overPayload)
                    if (overPayload.winning_line) {
                        setWinningLine(overPayload.winning_line)
                    }
                    break
                }
                case 'player_left': {
                    const leftPayload = msg.payload as { player_id: string; reason?: string }
                    if (leftPayload.player_id !== playerIdRef.current) {
                        setOpponentDisconnected(true)
                    }
                    break
                }
                case 'player_joined': {
                    const joinedPayload = msg.payload as { player_id: string }
                    if (joinedPayload.player_id !== playerIdRef.current) {
                        setOpponentDisconnected(false)
                        setOpponentReconnected(true)
                        setTimeout(() => setOpponentReconnected(false), 2500)
                    }
                    break
                }
                case 'error':
                    setError((msg.payload as { message: string }).message)
                    break
            }
        }

        ws.onclose = () => {
            setConnected(false)
            wsRef.current = null

            if (intentionalCloseRef.current) {
                setWinningLine(null)
                addEvent({ type: 'system', message: 'Disconnected' })
                return
            }

            const currentPid = playerIdRef.current
            if (currentPid && reconnectAttemptRef.current < MAX_RECONNECT_ATTEMPTS) {
                const attempt = reconnectAttemptRef.current
                const delay = BASE_RECONNECT_DELAY_MS * Math.pow(2, attempt)

                setReconnecting(true)
                addEvent({
                    type: 'system',
                    message: `Connection lost. Reconnecting in ${delay / 1000}s (attempt ${attempt + 1}/${MAX_RECONNECT_ATTEMPTS})...`,
                })

                reconnectTimerRef.current = setTimeout(() => {
                    reconnectAttemptRef.current++
                    connectWsRef.current?.(currentPid, true)
                }, delay)
            } else {
                setReconnecting(false)
                setWinningLine(null)
                addEvent({ type: 'system', message: 'Disconnected — max reconnect attempts reached' })
                setError('Connection lost. Please refresh the page.')
            }
        }

        ws.onerror = () => {}

        wsRef.current = ws
    }, [sessionId, addEvent])

    useEffect(() => {
        connectWsRef.current = connectWs
    }, [connectWs])

    const sendMove = useCallback((row: number, col: number) => {
        if (wsRef.current?.readyState !== WebSocket.OPEN) return
        wsRef.current.send(JSON.stringify({
            type: 'move',
            payload: { row, col },
        }))
    }, [])

    const disconnect = useCallback(() => {
        intentionalCloseRef.current = true
        if (reconnectTimerRef.current) {
            clearTimeout(reconnectTimerRef.current)
            reconnectTimerRef.current = null
        }
        setReconnecting(false)
        wsRef.current?.close()
        wsRef.current = null
    }, [])

    useEffect(() => {
        return () => {
            intentionalCloseRef.current = true
            if (reconnectTimerRef.current) {
                clearTimeout(reconnectTimerRef.current)
                reconnectTimerRef.current = null
            }
            wsRef.current?.close()
            wsRef.current = null
        }
    }, [])

    return {
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
        connect: connectWs,
        sendMove,
        disconnect,
    }
}
