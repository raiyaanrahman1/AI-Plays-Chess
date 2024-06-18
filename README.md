# AI Plays Chess - Raiyaan Rahman

A simple chess AI in Python, using a recursive tree algorithm to search branches of possible move sequences and selecting the one that leads to the best position determined using an evaluation function. It assumes best play from both sides and prunes suboptimal branches based on this.

Tech stack: (mostly) vanilla web front-end with jQuery and a Django back-end.

Check it out here: https://ai-plays-chess-production.up.railway.app/

Evaluation Function: The AI evaluates a position based on the material of each side (the amount of points based on pieces remaining on the board), and board control. For each player, it quantifies their board control as their total number of legal moves in the given position. The player with more legal moves in a certain position is considered to have an advantage in terms of board control. Material is given a higher significance than board control in the evaluation function.

Testing: The game engine, the backbone behind the AI which calculates the legal moves of each side after each, has been tested against 100,000 real human games played on the Lichess platform in January 2013. Lichess is an open-source chess website, and it has an [archive of publicly available games](https://database.lichess.org/) played on the platform since 2013. The tester I wrote that uses these games is contained in the `backend/ai_django/app/test_via_pgn.py` file. For each Lichess game (stored in the standardized PGN format), a new `Game()` instance is created from my chess engine, and each move that was played in the game is checked to be present in the engine's legal moves for the respective player, and that move is inputted as the next move made. This tester was run on a Google Cloud Compute Engine/Virtual Machine against 100,000 Lichess games from January 2013 and passed all tests. 
