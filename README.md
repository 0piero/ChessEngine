# ChessEngine
Chess game + graphic interface + greedy algorithm 

The entire game and also the interface are working. The GameState class has a legal_moves set() attribute that contains all the possible moves for a given round,
illegal moves that let the own king in check also are present in that set, once that type of illegal move is called, this move will be removed from the legal_moves set and
will not be allowed. Next step is to implement the recursively min-max algorithm and determine heuristic conditions for a given position.
