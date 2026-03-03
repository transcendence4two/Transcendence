import './Board.css'

export default function Board({ board, onCellClick, disabled, currentTurn, playerId, removedPiece, nextRemovedPiece, winningLine }) {
    const isMyTurn = currentTurn === playerId

    const getWinningLineClass = () => {
        if (!winningLine || winningLine.length < 3) return ''
        const [a, b, c] = winningLine

        // Horizontal
        if (a.row === b.row && b.row === c.row) return `winning-line--row-${a.row}`
        // Vertical
        if (a.col === b.col && b.col === c.col) return `winning-line--col-${a.col}`
        // Diagonals
        if (a.row === a.col && c.row === c.col) return 'winning-line--diag-1'
        if (a.row + a.col === 2 && c.row + c.col === 2) return 'winning-line--diag-2'

        return ''
    }

    const winningLineClass = getWinningLineClass()

    return (
        <div className="board-container">
            <div className="board">
                {board.map((row, i) =>
                    row.map((cell, j) => {
                        const wasRemoved = removedPiece && removedPiece.row === i && removedPiece.col === j
                        const isNextRemoved = nextRemovedPiece && nextRemovedPiece.row === i && nextRemovedPiece.col === j
                        return (
                            <button
                                key={`${i}-${j}`}
                                className={`cell ${cell ? 'cell--filled' : ''} ${cell === 'X' ? 'cell--x' : ''} ${cell === 'O' ? 'cell--o' : ''} ${wasRemoved ? 'cell--removed' : ''} ${isNextRemoved ? 'cell--next-removed' : ''}`}
                                onClick={() => onCellClick(i, j)}
                                disabled={disabled || !isMyTurn || cell !== ''}
                            >
                                {cell}
                            </button>
                        )
                    })
                )}
            </div>
            {winningLineClass && <div className={`winning-line ${winningLineClass}`} />}
        </div>
    )
}
