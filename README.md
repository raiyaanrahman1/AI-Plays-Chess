# AI Plays Chess - Raiyaan Rahman

A simple chess AI in Python, using a recursive tree algorithm to search branches of possible move sequences and selecting the one that leads to the best position determined using an evaluation function. It assumes best play from both sides and prunes suboptimal branches based on this.

Tech stack: (mostly) vanilla web front-end with jQuery and a Django back-end.

Check it out here: https://ai-plays-chess-production.up.railway.app/

Evaluation Function: The AI evaluates a position based on the material of each side (the amount of points based on pieces remaining on the board), and board control. For each player, it quantifies their board control as their total number of legal moves in the given position. The player with more legal moves in a certain position is considered to have an advantage in terms of board control. Material is given a higher significance than board control in the evaluation function.