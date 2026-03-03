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
}

interface WinningCell {
    row: number
    col: number
}

export interface GameOver {
    winner_id: string
    reason: string
    winning_line?: WinningCell[]
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

export function useGameSocket(sessionId: string) {
    const [connected, setConnected] = useState(false)
    const [gameState, setGameState] = useState<GameState | null>(null)
    const [gameOver, setGameOver] = useState<GameOver | null>(null)
    const [error, setError] = useState<string | null>(null)
    const [events, setEvents] = useState<GameEvent[]>([])
    const [playerId, setPlayerId] = useState<string | null>(null)
    const [winningLine, setWinningLine] = useState<WinningCell[] | null>(null)
    const wsRef = useRef<WebSocket | null>(null)

    const addEvent = useCallback((event: GameEvent) => {
        setEvents((prev) => [...prev.slice(-49), event])
    }, [])

    const connect = useCallback((pid: string) => {
        if (wsRef.current) return

        setPlayerId(pid)
        setError(null)
        setGameOver(null)
        setGameState(null)
        setWinningLine(null)

        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
        const host = window.location.host
        const ws = new WebSocket(`${protocol}//${host}/ws?session_id=${sessionId}`)

        ws.onopen = () => {
            setConnected(true)
            addEvent({ type: 'system', message: 'Connected' })

            ws.send(JSON.stringify({
                type: 'join',
                payload: { player_id: pid },
            }))
        }

        ws.onmessage = (event) => {
            const msg: WebSocketMessage = JSON.parse(event.data)
            addEvent({ type: msg.type, data: msg.payload })

            switch (msg.type) {
                case 'game_state':
                    setGameState(msg.payload as unknown as GameState)
                    break
                case 'game_over': {
                    const overPayload = msg.payload as unknown as GameOver
                    setGameOver(overPayload)
                    if (overPayload.winning_line) {
                        setWinningLine(overPayload.winning_line)
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
            setWinningLine(null)
            wsRef.current = null
            addEvent({ type: 'system', message: 'Disconnected' })
        }

        ws.onerror = () => {
            setError('Connection failed')
        }

        wsRef.current = ws
    }, [sessionId, addEvent])

    const sendMove = useCallback((row: number, col: number) => {
        if (wsRef.current?.readyState !== WebSocket.OPEN) return
        wsRef.current.send(JSON.stringify({
            type: 'move',
            payload: { row, col },
        }))
    }, [])

    const disconnect = useCallback(() => {
        wsRef.current?.close()
        wsRef.current = null
    }, [])

    useEffect(() => {
        return () => {
            wsRef.current?.close()
            wsRef.current = null
        }
    }, [])

    return {
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
    }
}
