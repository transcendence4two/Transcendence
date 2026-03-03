import Header from '../components/layout/Header'
import Footer from '../components/layout/Footer'
import GameLobby from '../components/game/GameLobby'
import '../components/game/game.css'

export default function GameLobbyPage() {
    return (
        <div className="container-main">
            <Header />
            <main className="content-main" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem 1rem' }}>
                <div className="game-container">
                    <h1 className="game-title">Tic Tac Infinity</h1>
                    <p className="game-subtitle">Create or join a game session</p>
                    <GameLobby />
                </div>
            </main>
            <Footer />
        </div>
    )
}
