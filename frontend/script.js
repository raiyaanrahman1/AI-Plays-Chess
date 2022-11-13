const boardElement = document.getElementById('board');
const baseUrl = window.location.protocol + "//" + window.location.hostname;
const apiUrl = baseUrl + ':8000/api/';

const squares = Array(8);
let legalMoves = {};
let boardData = [];
let material = {};
let moveHistory = [];

const SQUARE_LEN = parseInt(
    getComputedStyle(document.body).getPropertyValue('--square-len')
);

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
    setPieceWrapperEvents();
}

function updateGameState(data) {
    boardData = data.board;
    legalMoves = data.legal_moves;
    material = data.material;
    moveHistory = data.move_history;
    console.log(boardData, legalMoves);
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

async function submitMove({from_loc, to_loc, special_move}) {
    try {
        const res = await fetch(apiUrl + 'submit-move?' + new URLSearchParams({
            from_loc,
            to_loc,
            special_move
        }), {
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

    if (turn !== colour) return null;

    function checkPieceMoves(piece) {
        for (let move of piece) {
            if (
                arraysEqual(move.from_loc, fromLoc)
                && arraysEqual(move.to_loc, toLoc)
            ) {
                return move;
            }
        }
        return null;
    }

    if (pieceType === 'K') {
        return checkPieceMoves(legalMoves[colour][pieceType]);
    }

    for (let piece of legalMoves[colour][pieceType]) {
        const containsMove = checkPieceMoves(piece);
        if (containsMove !== null) return containsMove;
    }

    return null;
}

function animateMoveHelper(fromLoc, toLoc, pieceWrapperOverride = null) {
    const fromLocId = fromLoc.join(',');
    const fromSquare = document.getElementById(fromLocId);
    let pieceWrapper;
    
    if (pieceWrapperOverride === null) {
        pieceWrapper = $(fromSquare).find('.piece-wrapper')[0];
    } else {
        pieceWrapper = pieceWrapperOverride;
    }
    const top = (fromLoc[0] - toLoc[0]) * SQUARE_LEN + 'px';
    const leftStart = pieceWrapper.style.left === '' ? 0 : parseInt(pieceWrapper.style.left);
    const left = (leftStart + (toLoc[1] - fromLoc[1]) * SQUARE_LEN) + 'px';
    resetPos = false;

    return new Promise((resolve) => {
        $(pieceWrapper).animate({
            top,
            left,
        }, {
            done: function () {
                const toLocId = toLoc.join(',');
                const toSquare = document.getElementById(toLocId);
                if ($(toSquare).find('.piece-wrapper').length > 0) {
                    $(toSquare).empty();
                }
    
                $(pieceWrapper).detach().appendTo($(toSquare));
                $(pieceWrapper).css({
                    top: "0px",
                    left: "0px"
                });
                resetPos = true;
                resolve();
            }
        });
    })
}

function animateMove(move, pieceType, colour, focusedSquare, dragged) {
    const promises = [];
    if (!dragged) {
        promises.push(animateMoveHelper(move.from_loc, move.to_loc));
    }

    if (['O-O', 'O-O-O'].includes(move.special_move)) {
        const rookSquareCol = move.special_move === 'O-O' ? move.from_loc[1] + 3 : move.from_loc[1] - 4;
        const rookLoc = [move.from_loc[0], rookSquareCol];
        const toLocCol = move.special_move === 'O-O' ? move.from_loc[1] + 1 : move.from_loc[1] - 1;
        const toLoc = [move.from_loc[0], toLocCol];
        promises.push(animateMoveHelper(rookLoc, toLoc));

        if (dragged) {
            const focusedSquareLoc = squareIdToLoc(focusedSquare.id);
            const top = 0;
            const left = (focusedSquareLoc[1] - move.from_loc[1]) * SQUARE_LEN + 'px';
            const kingSquare = document.getElementById(move.from_loc.join(','));
            const king = $(kingSquare).find('.piece-wrapper')[0];
            $(king).css({
                top,
                left,
            });
            promises.push(animateMoveHelper(focusedSquareLoc, move.to_loc, king));
        }
    }

    return promises;
}

function getPromotionPiece(loc, colour) {
    const $promotionWrapper = $("<div>", {"class": "promotion-wrapper"});
    const pieceInfo = [['queen', 'Q'], ['rook', 'R'], ['bishop', 'B'], ['knight', 'N']];
    const promotionWrapperLoc = [loc[0], loc[1]];
    if (colour === 'black') {
        promotionWrapperLoc[0] += 3;
        pieceInfo.reverse();
    }
    return new Promise((resolve) => {
        $('#board').addClass('disable-pointer-events-for-promotion');
        pieceInfo.forEach(([pieceName, pieceType]) => {
            const $square = $("<div>", {"class": "square promotion-piece-square"});
            const $ppieceWrapper = $("<div>", {"class": "piece-wrapper promotion"});
            $ppieceWrapper.click(function () {
                $promotionWrapper.remove();
                promotionSquare.style.position = 'static';
                $('#board').removeClass('disable-pointer-events-for-promotion');
                resolve(`promote:${pieceType}`);
            });
            const $piece = $("<img>", {"class": "piece", "src": `assets/${colour}_${pieceName}.png`});
            $ppieceWrapper.append($piece);
            $square.append($ppieceWrapper);
            $promotionWrapper.append($square);
        });
        console.log(promotionWrapperLoc);
        const promotionSquare = document.getElementById(promotionWrapperLoc.join(','));
        promotionSquare.style.position = 'relative';
        $(promotionSquare).append($promotionWrapper[0]);
    })
}

async function makeMove(move, pieceType, colour, focusedSquare, dragged) {
    let promises = [];
    if (pieceType === 'P') {
        const backrank = colour === 'white' ? 7 : 0;
        if (move.to_loc[0] === backrank) {
            move.special_move = await getPromotionPiece(move.to_loc, colour);
        }

    }
    if (['O-O', 'O-O-O'].includes(move.special_move) || !dragged) {
        promises = animateMove(move, pieceType, colour, focusedSquare, dragged);
    }
    await Promise.all(promises);
    await submitMove(move);
}

let selectedSquareId = null;

async function moveEvent(focusedSquare, dragged) {
    if (selectedSquareId === focusedSquare.id) {
        if (dragged) return null;
        selectedSquareId = null;
        focusedSquare.classList.remove('selected');
        return null;
    }
    
    if (selectedSquareId !== null) {
        const fromLoc = squareIdToLoc(selectedSquareId);
        const pieceInfo = locToPieceInfo(fromLoc);
        const toLoc = squareIdToLoc(focusedSquare.id);
        const toLocPieceInfo = locToPieceInfo(toLoc);

        let move;
        const { pieceType, colour } = pieceInfo;
        if (
            pieceType === 'K'
            && toLoc[0] === fromLoc[0]
            && (
                toLoc[1] === fromLoc[1] + 2
                || (
                    toLocPieceInfo !== null
                    && toLocPieceInfo.pieceType === 'R'
                    && toLoc[1] === fromLoc[1] + 3
                )
            )
            && (move = moveIsLegal(fromLoc, [fromLoc[0], fromLoc[1] + 2], pieceInfo)) !== null
        ) {
            makeMove(move, pieceType, colour, focusedSquare, dragged);
            document.getElementById(selectedSquareId).classList.remove('selected');
            selectedSquareId = null;
            return move;
        } else if (
            pieceType === 'K'
            && toLoc[0] === fromLoc[0]
            && (
                toLoc[1] === fromLoc[1] - 2
                || (
                    toLocPieceInfo !== null
                    && toLocPieceInfo.pieceType === 'R'
                    && toLoc[1] === fromLoc[1] - 4
                )
            )
            && (move = moveIsLegal(fromLoc, [fromLoc[0], fromLoc[1] - 2], pieceInfo)) !== null
        ) {
            makeMove(move, pieceType, colour, focusedSquare, dragged);
            document.getElementById(selectedSquareId).classList.remove('selected');
            selectedSquareId = null;
            return move;
        } else if (toLocPieceInfo !== null && toLocPieceInfo.colour === colour && !dragged) {
            document.getElementById(selectedSquareId).classList.remove('selected');
            selectedSquareId = focusedSquare.id;
            focusedSquare.classList.add('selected');
            return null;
        }

        move = moveIsLegal(fromLoc, toLoc, pieceInfo);
        if (move !== null) {
            makeMove(move, pieceType, colour, focusedSquare, dragged);
            document.getElementById(selectedSquareId).classList.remove('selected');
            selectedSquareId = null;
            return move;
        }
    } else {
        const loc = squareIdToLoc(focusedSquare.id);
        const pieceInfo = locToPieceInfo(loc);
        if (pieceInfo === null) return null;
        selectedSquareId = focusedSquare.id;
        focusedSquare.classList.add('selected');
    }
}

function setPieceWrapperEvents() {
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
    });
}

let mouseX = null, mouseY = null;
let resetPos = true;
// TODO: when dragging a piece over a square, highlight the square with
// an outline so you know exactly which square your mouse is over
// sometimes you can't tell which one if your near the edge
// see chess.com behaviour
createGame().then(() => {
    $(function() {
        $('.square').droppable({
            drop: async function (event, ui) {
                const dragged = true;
                const move = await moveEvent(this, dragged);
                
                // if (move === null) {
                //     ui.draggable.animate({
                //         top: "0px",
                //         left: "0px"
                //     });
                //     return;
                // } else if (['O-O', 'O-O-O'].includes(move.special_move)) {
                //     return;
                // }
                
                // const pieceWrapperInSquare = $(this).find('.piece-wrapper');
                // if (pieceWrapperInSquare.length > 0 && !pieceWrapperInSquare.first().is(ui.draggable)) {
                //     $(this).empty();
                // }
                // ui.draggable.detach().appendTo($(this));
                // ui.draggable.css({
                //     top: "0px",
                //     left: "0px"
                // });

            }
        })
        $('.square').click(function () {
            const dragged = false;
            moveEvent(this, dragged);
        });
        $('.ui-elements-wrapper').droppable({
            drop: function (event, ui) {
                if (resetPos) {
                    ui.draggable.animate({
                        top: "0px",
                        left: "0px"
                    });
                }
            }
        })
    });
});