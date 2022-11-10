const boardElement = document.getElementById('board');
const baseUrl = window.location.protocol + "//" + window.location.hostname;
const apiUrl = baseUrl + ':8000/api/';

const squares = Array(8);
let legalMoves = {};
let boardData = [];
let material = {};
let moveHistory = [];

for (let i = 7; i >= 0; i--) {
    const boardRowEl = document.createElement('div');
    const boardRow = [];
    boardRowEl.classList.add('board-row');
    for (let j = 0; j < 8; j++) {
        const colour = i % 2 == j % 2 ? 'dark' : 'light';
        const square = document.createElement('div');
        square.classList.add('square', `${colour}-square`);
        square.id = `${i},${j}`
        boardRowEl.append(square);
        boardRow.push(square);
    }
    boardElement.append(boardRowEl);
    squares[i] = boardRow;
}

function letterToColour(letter) {
    const letterToColour = {'W': 'white', 'B': 'black'};
    return letterToColour[letter];
}

function updateBoard(board) {
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
            squares[i][j].innerHTML = '';
            if (piece === '') {
                return;
            }
            const pieceWrapper = document.createElement('div');
            const pieceEl = document.createElement('img');
            const pieceType = pieceLetterToPiece[piece.charAt(1)]
            pieceEl.src = `assets/${letterToColour(piece.charAt(0))}_${pieceType}.png`;
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

function updateGameState(data) {
    boardData = data.board;
    legalMoves = data.legal_moves;
    material = data.material;
    moveHistory = data.move_history;
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
        updateGameState(data);
    } catch (err) {
        console.log(err);
    }
}

function arraysEqual(a, b) {
    if (a === b) return true;
    if (a == null || b == null) return false;
    if (a.length !== b.length) return false;
  
    for (let i = 0; i < a.length; ++i) {
      if (a[i] !== b[i]) return false;
    }
    return true;
}

function squareIdToLoc(id) {
    return [Number(id.charAt(0)), Number(id.charAt(2))];
}

function locToPieceInfo(loc) {
    if (boardData[loc[0]][loc[1]] === '') return null;

    const colour = letterToColour(boardData[loc[0]][loc[1]].charAt(0));
    const pieceType = boardData[loc[0]][loc[1]].charAt(1);
    return {colour, pieceType};
}

function moveIsLegal(fromLoc, toLoc, fromLocPieceInfo) {
    const { colour, pieceType } = fromLocPieceInfo;
    const turn = moveHistory.length % 2 === 0 ? 'white' : 'black';

    if (turn !== colour) return false;

    for (let piece of legalMoves[colour][pieceType]) {
        for (let move of piece) {
            if (
                arraysEqual(move.from_loc, fromLoc)
                && arraysEqual(move.to_loc, toLoc)
            ) {
                return true;
            }
        }
    }

    return false;
}

function makeMove(fromLoc, toLoc, specialMove = null) {
    return;
}

let selectedSquareId = null;

function moveEvent(focusedSquare, dragged) {
    if (selectedSquareId === focusedSquare.id) {
        if (dragged) return false;
        selectedSquareId = null;
        focusedSquare.classList.remove('selected');
        return false;
    }
    
    if (selectedSquareId !== null) {
        const fromLoc = squareIdToLoc(selectedSquareId);
        const pieceInfo = locToPieceInfo(fromLoc);
        const toLoc = squareIdToLoc(focusedSquare.id);
        const toLocPieceInfo = locToPieceInfo(toLoc);

        // TODO: rewrite this stuff so that moveIsLegal passes the move if it's legal so I don't have to check
        // for en-passent
        const { pieceType, colour } = pieceInfo;
        if (
            pieceType === 'K'
            && toLoc[0] === fromLoc[0]
            && (
                toLoc[1] === fromLoc[1] + 2
                || (
                    toLocPieceInfo.pieceType === 'R'
                    && toLoc[1] === fromLoc[1] + 3
                )
            )
            && moveIsLegal(fromLoc, [fromLoc[0], fromLoc[1] + 2], pieceInfo)
        ) {
            makeMove(fromLoc, [fromLoc[0], fromLoc[1] + 2], 'O-O');
            return true;
        } else if (
            pieceType === 'K'
            && toLoc[0] === fromLoc[0]
            && (
                toLoc[1] === fromLoc[1] - 2
                || (
                    toLocPieceInfo.pieceType === 'R'
                    && toLoc[1] === fromLoc[1] - 4
                )
            )
            && moveIsLegal(fromLoc, [fromLoc[0], fromLoc[1] - 2], pieceInfo)
        ) {
            makeMove(fromLoc, [fromLoc[0], fromLoc[1] - 2], 'O-O-O');
            return true;
        } else if (toLocPieceInfo !== null && toLocPieceInfo.colour === colour && !dragged) {
            document.getElementById(selectedSquareId).classList.remove('selected');
            selectedSquareId = focusedSquare.id;
            focusedSquare.classList.add('selected');
            return false;
        }

        if (moveIsLegal(fromLoc, toLoc, pieceInfo)) {
            console.log('make move');
            makeMove(fromLoc, toLoc);
            document.getElementById(selectedSquareId).classList.remove('selected');
            selectedSquareId = null;
            return true;
        }
    } else {
        const loc = squareIdToLoc(focusedSquare.id);
        const pieceInfo = locToPieceInfo(loc);
        if (pieceInfo === null) return false;
        selectedSquareId = focusedSquare.id;
        focusedSquare.classList.add('selected');
    }
}

let mouseX = null, mouseY = null;
// TODO: when dragging a piece over a square, highlight the square with
// an outline so you know exactly which square your mouse is over
// sometimes you can't tell which one if your near the edge
// see chess.com behaviour
createGame().then(() => {
    $(function() {
        $('.piece-wrapper').draggable({
            containment: '.ui-elements-wrapper',
            start: function(event, ui) {
                const dragged = true;
                moveEvent(this.closest('.square'), dragged);
            }
        });
        $('.piece-wrapper').mousedown(function (e) {
            const wrapper = e.target.closest('.piece-wrapper');
            const rect = wrapper.getBoundingClientRect();
            $(this).css({
                left: (e.clientX - rect.left) - (rect.width / 2) + 'px',
                top: (e.clientY - rect.top) - (rect.height / 2) + 'px'
            });
            mouseX = e.clientX;
            mouseY = e.clientY;
        });
        $('.piece-wrapper').mouseup(function (e) {
            if (e.clientX === mouseX && e.clientY === mouseY) {
                $(this).css({
                    left: 0,
                    top: 0
                });
            }
            mouseX = null, mouseY = null;
        })
        $('.square').droppable({
            drop: function (event, ui) {
                const dragged = true;
                const madeMove = moveEvent(this, dragged);
                
                if (!madeMove) {
                    ui.draggable.animate({
                        top: "0px",
                        left: "0px"
                    });
                    return;
                }
                
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
        $('.square').click(function () {
            const dragged = false;
            moveEvent(this, dragged);
        });
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