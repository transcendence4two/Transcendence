import { useState, useRef, useCallback, useEffect } from 'react'

export function useGameSocket(sessionId) {
    const [connected, setConnected] = useState(false)
    const [gameState, setGameState] = useState(null)
    const [gameOver, setGameOver] = useState(null)
    const [error, setError] = useState(null)
    const [events, setEvents] = useState([])
    const [playerId, setPlayerId] = useState(null)
    const wsRef = useRef(null)

    const addEvent = useCallback((event) => {
        setEvents((prev) => [...prev.slice(-49), event])
    }, [])

    const connect = useCallback((pid) => {
        if (wsRef.current) return

        setPlayerId(pid)
        setError(null)
        setGameOver(null)
        setGameState(null)

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
            const msg = JSON.parse(event.data)
            addEvent({ type: msg.type, data: msg.payload })

            switch (msg.type) {
                case 'game_state':
                    setGameState(msg.payload)
                    break
                case 'game_over':
                    setGameOver(msg.payload)
                    break
                case 'error':
                    setError(msg.payload.message)
                    break
            }
        }

        ws.onclose = () => {
            setConnected(false)
            wsRef.current = null
            addEvent({ type: 'system', message: 'Disconnected' })
        }

        ws.onerror = () => {
            setError('Connection failed')
        }

        wsRef.current = ws
    }, [sessionId, addEvent])

    const sendMove = useCallback((row, col) => {
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
        connect,
        sendMove,
        disconnect,
    }
}

