interface WinningCell {
    row: number
    col: number
}

interface GameBoardProps {
    board: string[][]
    onCellClick: (row: number, col: number) => void
    disabled: boolean
    currentTurn?: string
    playerId: string | null
    removedPiece?: { row: number; col: number }
    nextRemovedPiece?: { row: number; col: number }
    winningLine: WinningCell[] | null
}

function getWinningLineClass(winningLine: WinningCell[] | null): string {
    if (!winningLine || winningLine.length < 3) return ''
    const [a, b, c] = winningLine

    if (a.row === b.row && b.row === c.row) return `game-winning-line--row-${a.row}`
    if (a.col === b.col && b.col === c.col) return `game-winning-line--col-${a.col}`
    if (a.row === a.col && c.row === c.col) return 'game-winning-line--diag-1'
    if (a.row + a.col === 2 && c.row + c.col === 2) return 'game-winning-line--diag-2'

    return ''
}

export default function GameBoard({
    board,
    onCellClick,
    disabled,
    currentTurn,
    playerId,
    removedPiece,
    nextRemovedPiece,
    winningLine,
}: GameBoardProps) {
    const isMyTurn = currentTurn === playerId
    const winningLineClass = getWinningLineClass(winningLine)

    return (
        <div className="game-board-container">
            <div className="game-board">
                {board.map((row, i) =>
                    row.map((cell, j) => {
                        const wasRemoved = removedPiece && removedPiece.row === i && removedPiece.col === j
                        const isNextRemoved = nextRemovedPiece && nextRemovedPiece.row === i && nextRemovedPiece.col === j

                        const classes = [
                            'game-cell',
                            cell === 'X' ? 'game-cell--x' : '',
                            cell === 'O' ? 'game-cell--o' : '',
                            wasRemoved ? 'game-cell--removed' : '',
                            isNextRemoved ? 'game-cell--next-removed' : '',
                        ].filter(Boolean).join(' ')

                        return (
                            <button
                                key={`${i}-${j}`}
                                className={classes}
                                onClick={() => onCellClick(i, j)}
                                disabled={disabled || !isMyTurn || cell !== ''}
                            >
                                {cell}
                            </button>
                        )
                    })
                )}
            </div>
            {winningLineClass && <div className={`game-winning-line ${winningLineClass}`} />}
        </div>
    )
}
