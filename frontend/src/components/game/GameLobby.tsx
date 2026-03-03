import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import './game.css'

export default function GameLobby() {
    const navigate = useNavigate()
    const [joinId, setJoinId] = useState('')

    const createGame = () => {
        const id = crypto.randomUUID()
        navigate(`/game/${id}`)
    }

    const joinGame = (e: React.FormEvent) => {
        e.preventDefault()
        if (!joinId.trim()) return
        navigate(`/game/${joinId.trim()}`)
    }

    return (
        <div className="game-lobby">
            <div className="game-lobby-action">
                <button
                    type="button"
                    className="game-btn game-btn--primary"
                    onClick={createGame}
                >
                    🎮 Create New Game
                </button>
            </div>

            <div className="game-divider">or join existing</div>

            <form onSubmit={joinGame} className="game-lobby-action">
                <div className="game-input-group">
                    <label>Session ID</label>
                    <input
                        value={joinId}
                        onChange={(e) => setJoinId(e.target.value)}
                        placeholder="paste session id"
                    />
                </div>
                <button
                    type="submit"
                    className="game-btn game-btn--secondary"
                    disabled={!joinId.trim()}
                >
                    Join Game
                </button>
            </form>
        </div>
    )
}
