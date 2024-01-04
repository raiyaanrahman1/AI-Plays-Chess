const boardElement = document.getElementById('board');
const baseUrl = window.location.protocol + "//" + window.location.hostname;
const apiUrl = baseUrl + '/api/'; // FOR PRODUCTION
// const apiUrl = baseUrl + ':8000/api/'; // FOR DEVELOPMENT


const squares = Array(8);
let legalMoves = {};
let boardData = [];
let material = {};
let moveHistory = [];
let gameStatus = {};
// let updateMoveTreePromise = null;

const modes = {
    'ai-2': {is_ai: true, depth: 2},
    'ai-3': {is_ai: true, depth: 3},
    'self-play': {is_ai: false}
};

let selectedMode = modes["ai-2"];

const captureSound = new Audio('static/assets/sounds/Capture.mp3');
const standardMoveSound = new Audio('static/assets/sounds/StandardMove.mp3');
const gameFinishedSound = new Audio('static/assets/sounds/GenericNotify.mp3');

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
            pieceEl.src = `static/assets/pieces/${letterToColour(piece.charAt(0))}_${pieceType}.png`;
            pieceEl.classList.add('piece');
            if (pieceType === 'pawn') {
                pieceEl.style.marginLeft = '-3px';
            }
            if (pieceType === 'rook') {
                pieceEl.style.marginLeft = '-2px';
            }
            pieceWrapper.classList.add('piece-wrapper');

            if (piece === 'WK' && gameStatus.white_in_check) {
                $(pieceWrapper).addClass('check');
            } else if (piece === 'BK' && gameStatus.black_in_check) {
                $(pieceWrapper).addClass('check');
            } else if ((piece === 'WK' || piece === 'BK') && $(pieceWrapper).hasClass('check')) {
                $(pieceWrapper).removeClass('check');
            } 

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
    gameStatus = data.game_status;
    // console.log(boardData, legalMoves, gameStatus, moveHistory);
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
        updateGameState(data);
        updateBoard(data.board);
        // updateMoveTree();
    } catch (err) {
        console.log(err);
    }
}

function updateMoveHistory() {
    const moveHistoryEl = $('#move-history');

    if (moveHistory.length % 2 !== 0) {
        const moveEl = $('<div>', {class: 'move'});
        const plyEl = $('<div>', {class:'ply'}).text(`${(moveHistory.length + 1) / 2}. ${moveHistory[moveHistory.length - 1]}`);
        moveEl.append(plyEl);
        moveHistoryEl.append(moveEl);
    } else {
        const moveEl = moveHistoryEl.children().last();
        // console.log(moveEl);
        const plyEl = $('<div>', {class:'ply'}).text(moveHistory[moveHistory.length - 1]);
        moveEl.append(plyEl);
        moveHistoryEl.append(moveEl);
    }
    moveHistoryEl[0].scrollTop = moveHistoryEl[0].scrollHeight;
}

async function submitMove({from_loc, to_loc, special_move}) {
    try {
        // if (updateMoveTreePromise !== null) {
        //     await updateMoveTreePromise;
        // } 
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
        updateGameState(data);
        updateBoard(data.board);
        
        if (gameStatus.last_move_was_capture) {
            captureSound.play();
        } else {
            standardMoveSound.play();
        }

        if (gameStatus.game_finished) {
            gameFinishedSound.play();
        }

        updateMoveHistory();
        if (selectedMode.is_ai && moveHistory.length % 2 == 1) {
            await playAiMove();
            // updateMoveTree();
        }
    } catch (err) {
        console.log(err);
    }
}

async function playAiMove() {
    // const res = await updateMoveTreePromise;
    // updateMoveTreePromise = null;
    // if (!res.ok) throw Error(res.statusText);
    // const data = await res.json();

    try {
        console.log('Fetching AI Move');
        $('#game-mode-select').attr('disabled', true);
        const start = Date.now();
        const res2 = await fetch(
            apiUrl + 'play-best-move?' + new URLSearchParams({depth: selectedMode.depth}),
            {
                method: "POST",
                headers: {
                    'content-type': "application/json"
                },
            }
        );
        if (!res2.ok) throw Error(res2.statusText);
        const data = await res2.json();
        console.log(`Got AI Move, took ${(Date.now() - start) / 1000} seconds`);
        // console.log(data.from_loc);

        const promises = animateMove({from_loc: data.from_loc, to_loc: data.to_loc, special_move: data.special_move}, squares[data.from_loc[0]][data.from_loc[1]], false);
        await Promise.all(promises);

        updateGameState(data);
        updateBoard(data.board);
        
        if (gameStatus.last_move_was_capture) {
            captureSound.play();
        } else {
            standardMoveSound.play();
        }

        if (gameStatus.game_finished) {
            gameFinishedSound.play();
        }

        updateMoveHistory();
        $('#game-mode-select').attr('disabled', false);
        // console.log(squares)
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

    for (let piece of legalMoves[colour][pieceType]) {
        for (let move of piece) {
            if (
                arraysEqual(move.from_loc, fromLoc)
                && arraysEqual(move.to_loc, toLoc)
            ) {
                return move;
            }
        }
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

function animateMove(move, focusedSquare, dragged) {
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
            const $piece = $("<img>", {"class": "piece", "src": `static/assets/pieces/${colour}_${pieceName}.png`});
            $ppieceWrapper.append($piece);
            $square.append($ppieceWrapper);
            $promotionWrapper.append($square);
        });
        // console.log(promotionWrapperLoc);
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
        promises = animateMove(move, focusedSquare, dragged);
    }
    await Promise.all(promises);
    await submitMove(move);
}

let selectedSquareId = null;

async function moveEvent(focusedSquare, dragged, dropped = false) {
    if (selectedMode.is_ai && moveHistory.length % 2 != 0) {
        return;
    }

    if (selectedSquareId === focusedSquare.id) {
        if (dragged) return;
        selectedSquareId = null;
        focusedSquare.classList.remove('selected');
        return;
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
            document.getElementById(selectedSquareId).classList.remove('selected');
            selectedSquareId = null;
            await makeMove(move, pieceType, colour, focusedSquare, dragged);
            return;
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
            document.getElementById(selectedSquareId).classList.remove('selected');
            selectedSquareId = null;
            await makeMove(move, pieceType, colour, focusedSquare, dragged);
            return;
        } else if (toLocPieceInfo !== null && toLocPieceInfo.colour === colour && !dropped) {
            document.getElementById(selectedSquareId).classList.remove('selected');
            selectedSquareId = focusedSquare.id;
            focusedSquare.classList.add('selected');
            return;
        }

        move = moveIsLegal(fromLoc, toLoc, pieceInfo);
        if (move !== null) {
            document.getElementById(selectedSquareId).classList.remove('selected');
            selectedSquareId = null;
            await makeMove(move, pieceType, colour, focusedSquare, dragged);
            return;
        } else if (toLocPieceInfo !== null && toLocPieceInfo.colour !== colour && !dropped) {
            document.getElementById(selectedSquareId).classList.remove('selected');
            selectedSquareId = focusedSquare.id;
            focusedSquare.classList.add('selected');
            return;
        }
    } else {
        const loc = squareIdToLoc(focusedSquare.id);
        const pieceInfo = locToPieceInfo(loc);
        if (pieceInfo === null) return;
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

// function updateMoveTree() {
//     try {
//         updateMoveTreePromise = fetch(apiUrl + 'update-move-tree?' + new URLSearchParams({
//             depth: selectedMode.depth
//         }), {
//             method: "POST",
//             headers: {
//                 'content-type': "application/json"
//             },
//         });
//     } catch (err) {
//         console.log(err);
//     }
// }

let mouseX = null, mouseY = null;
let resetPos = true;
let ui_drop_promise = new Promise((resolve) => resolve());
// TODO: when dragging a piece over a square, highlight the square with
// an outline so you know exactly which square your mouse is over
// sometimes you can't tell which one if your near the edge
// see chess.com behaviour
createGame().then(() => {
    $(function() {
        $('.square').droppable({
            drop: async function (event, ui) {
                const dragged = true;
                const dropped = true;
                ui_drop_promise = new Promise(async (resolve) => {
                    await moveEvent(this, dragged, dropped);
                    ui_drop_promise = new Promise((resolve) => resolve());
                    resolve();
                });
            }
        })
        $('.square').click(function () {
            const dragged = false;
            moveEvent(this, dragged);
        });
        $('#game-mode-select').change(async function () {
            const prevMode = selectedMode;
            selectedMode = modes[this.value];
            if (selectedMode.is_ai && !prevMode.is_ai && moveHistory.length % 2 == 1) {
                await playAiMove();
            }
            if (selectedMode.is_ai && selectedMode.depth == 3) {
                $('#depth-3-note').removeClass('hidden');
            } else {
                $('#depth-3-note').addClass('hidden');
            }
        });
        $('.ui-elements-wrapper').droppable({
            drop: function (event, ui) {
                ui_drop_promise.then(() => {
                    if (resetPos) {
                        ui.draggable.animate({
                            top: "0px",
                            left: "0px"
                        });
                    }
                })
            }
        })
    });
});