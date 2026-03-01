import './Board.css'

export default function Board({ board, onCellClick, disabled, currentTurn, playerId, removedPiece }) {
    const isMyTurn = currentTurn === playerId

    return (
        <div className="board">
            {board.map((row, i) =>
                row.map((cell, j) => {
                    const wasRemoved = removedPiece && removedPiece.row === i && removedPiece.col === j
                    return (
                        <button
                            key={`${i}-${j}`}
                            className={`cell ${cell ? 'cell--filled' : ''} ${cell === 'X' ? 'cell--x' : ''} ${cell === 'O' ? 'cell--o' : ''} ${wasRemoved ? 'cell--removed' : ''}`}
                            onClick={() => onCellClick(i, j)}
                            disabled={disabled || !isMyTurn || cell !== ''}
                        >
                            {cell}
                        </button>
                    )
                })
            )}
        </div>
    )
}
