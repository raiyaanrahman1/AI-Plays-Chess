const boardElement = document.getElementById('board');
const baseUrl = window.location.protocol + "//" + window.location.hostname;
const apiUrl = baseUrl + ':8000/api/';

const squares = Array(8);
for (let i = 7; i >= 0; i--) {
    const boardRowEl = document.createElement('div');
    const boardRow = [];
    boardRowEl.classList.add('board-row');
    for (let j = 0; j < 8; j++) {
        const colour = i % 2 == j % 2 ? 'dark' : 'light';
        const square = document.createElement('div');
        square.classList.add('square', `${colour}-square`);
        boardRowEl.append(square);
        boardRow.push(square);
    }
    boardElement.append(boardRowEl);
    squares[i] = boardRow;
}

function updateBoard(board) {
    const letterToColour = {'W': 'white', 'B': 'black'}
    const pieceLetterToPiece = {
        'P': 'pawn',
        'B': 'bishop',
        'N': 'knight',
        'R': 'rook',
        'Q': 'queen',
        'K': 'king'
    }
    board.forEach((row, i) => {
        row.forEach((piece, j) => {
            if (piece === '') {
                squares[i][j].innerHTML = '';
                return;
            }
            const pieceWrapper = document.createElement('div');
            const pieceEl = document.createElement('img');
            const pieceType = pieceLetterToPiece[piece.charAt(1)]
            pieceEl.src = `assets/${letterToColour[piece.charAt(0)]}_${pieceType}.png`;
            pieceEl.classList.add('piece');
            if (pieceType === 'pawn') {
                pieceEl.style.marginLeft = '-3px';
            }
            if (pieceType === 'rook') {
                pieceEl.style.marginLeft = '-2px';
            }
            pieceWrapper.classList.add('piece-wrapper');
            pieceWrapper.append(pieceEl);
            squares[i][j].append(pieceWrapper);
        })
    });
}

async function createGame() {
    try {
        const res = await fetch(apiUrl + 'create-game', {
            method: "POST",
            headers: {
                'content-type': "application/json"
            },
        });
        if (!res.ok) throw Error(res.statusText);
        const data = await res.json();
        updateBoard(data.board);
    } catch (err) {
        console.log(err);
    }
}

createGame().then(() => {
    $(function() {
        $('.piece-wrapper').draggable({
            containment: '.ui-elements-wrapper',
            cursor: 'grabbing',
        });
        $('.square').droppable({
            drop: function (event, ui) {
                const pieceWrapperInSquare = $(this).find('.piece-wrapper');
                if (pieceWrapperInSquare.length > 0 && !pieceWrapperInSquare.first().is(ui.draggable)) {
                    $(this).empty();
                }
                ui.draggable.detach().appendTo($(this));
                ui.draggable.css({
                    top: "0px",
                    left: "0px"
                });
            }
        })
        $('.ui-elements-wrapper').droppable({
            drop: function (event, ui) {
                ui.draggable.animate({
                    top: "0px",
                    left: "0px"
                });
            }
        })
    });
});