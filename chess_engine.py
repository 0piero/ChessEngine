from abc import ABC, abstractmethod

class Board():
	def __init__(self, custom_board = None):
		if not custom_board:
			self.board = [[None for _ in range(8)] for _ in range(8)] 
			for rank in range(8):
				for file in range(8):
					dark_square = (file + rank)%2 != 0
					if dark_square: 
						self.board[rank][file] = Square(1, sqr_name = f'{chr(97+file)}{8-rank}')
					else:
						self.board[rank][file] = Square(0, sqr_name = f'{chr(97+file)}{8-rank}')

			for rank_w, rank_b in zip(self.board[6:8], reversed(self.board[0:2])):
				for file_w, file_b, piece in zip(rank_w, rank_b, ['R','N','B','Q','K','B','N','R']):
					if file_w.sqr_name[1] == '1':
						file_w.piece = Piece.instantiate(piece, 'w', file_w.sqr_name)
						file_b.piece = Piece.instantiate(piece, 'b', file_b.sqr_name)
					else:
						file_w.piece = Piece.instantiate('P', 'w', file_w.sqr_name)
						file_b.piece = Piece.instantiate('P', 'b', file_b.sqr_name)
		else: self.board = custom_board
	@classmethod
	def mk_custom_board(cls, *pieces: 'Piece') -> []:
		custom_board = [[None for _ in range(8)] for _ in range(8)]
		for rank in range(8):
			for file in range(8):
				dark_square = (file + rank)%2 != 0
				if dark_square: 
					custom_board[rank][file] = Square(1, sqr_name = f'{chr(97+file)}{8-rank}')
				else:
					custom_board[rank][file] = Square(0, sqr_name = f'{chr(97+file)}{8-rank}')
		for p in pieces:
			custom_board[-int(p.sqr_pos[1])][ord(p.sqr_pos[0]) - 97].piece = p   
		return custom_board
	

class Piece(ABC):
	@classmethod
	def instantiate(cls, piece_type: str, color: str, pos: str):
		if piece_type == 'R':
			return Rook(piece_type, color, pos)
		elif piece_type == 'N':
			return Knight(piece_type, color, pos)
		elif piece_type == 'B':
			return Bishop(piece_type, color, pos)
		elif piece_type == 'Q':
			return Queen(piece_type, color, pos)
		elif piece_type == 'K':
			return King(piece_type, color, pos)
		else:
			return Pawn(piece_type, color, pos)

	@abstractmethod
	def move_piece(self, game_state: 'GameState', move: str):
		pass
	@abstractmethod
	def check_all_moves(self, game_state: 'GameState'):
		pass
class Pawn(Piece):
	def __init__(self, piece_type: str, color: str, pos: 'Square'):
		self.piece_type = piece_type
		self.piece_color = color
		self.sqr_pos = pos
		self.has_moved = False
		self.moved_2square = False
		self.passant_flag = False # either is setted to False or equal to the 2square move that was made 

	# move:	(a-h)(1-8)
	# move: (a-h)(x)(a-h)(1-8)
	# move: (a-h)(x)(a-h)(E) - (en-passant)
	# move: (a-h)(1-8)(=)(Q, B, N, R)
	# move: (a-h)x(a-h)(1-8)(=)(Q, B, N, R)
	def en_passant(self, game_state: 'GameState', piece_xy: ()):
		pass
	def move_piece(self, game_state: 'GameState', move: str):
		if self.piece_color == game_state.color_to_move:
			if move in game_state.legal_moves:
				get_row = - int(self.sqr_pos[1])
				get_file = ord(self.sqr_pos[0]) - 97
				moved_piece = game_state.board_state[get_row][get_file].piece
				game_state.board_state[get_row][get_file].piece = None
				if 'x' in move and 'E' in move:
					captured_piece = game_state.board_state[get_row][ord(move[2]) - 97].piece
					game_state.board_state[get_row][get_file].piece = None
					game_state.board_state[get_row][ord(move[2]) - 97].piece = None
					if self.piece_color == 'w':
												
						game_state.board_state[get_row - 1][ord(move[2]) - 97].add_piece(self)
	
						if Square.check_sqr_threat(game_state, - int(game_state.w_king_sqr[1]), ord(game_state.w_king_sqr[0]) - 97, 'b'):
							game_state.undo_move([(get_row, get_file),(get_row - 1, ord(move[2]) - 97), moved_piece],
							piece_captured = captured_piece, ep = True)
							game_state.legal_moves.remove(move)
						else:
							in_chk = False
							if Square.check_sqr_threat(game_state, - int(game_state.b_king_sqr[1]), ord(game_state.b_king_sqr[0]) - 97, 'w'):
								in_chk = True
							game_state.update('b', move, b_captured = 1, b_check = in_chk)
	
					else:
						
						game_state.board_state[get_row + 1][ord(move[2]) - 97].add_piece(self)

						if Square.check_sqr_threat(game_state, - int(game_state.b_king_sqr[1]), ord(game_state.b_king_sqr[0]) - 97, 'w'):
							game_state.undo_move([(get_row, get_file),(get_row + 1, ord(move[2]) - 97 ), moved_piece],
							piece_captured = captured_piece, ep = True)
							game_state.legal_moves.remove(move)
						else:
							in_chk = False
							if Square.check_sqr_threat(game_state, - int(game_state.b_king_sqr[1]), ord(game_state.b_king_sqr[0]) - 97, 'b'):
								in_chk = True
							game_state.update('w', move, w_captured = 1, w_check = in_chk)
				elif '=' in move:
					if 'x' in move:

						if self.piece_color == 'w':
							captured_piece = game_state.board_state[get_row - 1][ord(move[2]) - 97].piece
							game_state.board_state[get_row - 1][ord(move[2]) - 97].add_piece(Piece.instantiate(f'{move[-1]}', 'w', move[2]+'8'))

							if Square.check_sqr_threat(game_state, - int(game_state.w_king_sqr[1]), ord(game_state.w_king_sqr[0]) - 97, 'b'):

								game_state.undo_move([(get_row, get_file),(get_row - 1, ord(move[2]) - 97 ), moved_piece],
								piece_captured = captured_piece)

								game_state.legal_moves.remove(move)
							else:
								in_chk = False
								if Square.check_sqr_threat(game_state, - int(game_state.b_king_sqr[1]), ord(game_state.b_king_sqr[0]) - 97, 'w'):
									in_chk = True
								game_state.update('b', move, b_captured = 1, b_check = in_chk)
						else:
							captured_piece = game_state.board_state[get_row + 1][ord(move[2]) - 97].piece
							game_state.board_state[get_row + 1][ord(move[2]) - 97].add_piece(Piece.instantiate(f'{move[-1]}', 'b', move[2]+'1'))

							if Square.check_sqr_threat(game_state, - int(game_state.b_king_sqr[1]), ord(game_state.b_king_sqr[0]) - 97, 'w'):
								game_state.undo_move([(get_row, get_file),(get_row + 1, ord(move[2]) - 97 ), moved_piece],
								piece_captured = captured_piece)
								game_state.legal_moves.remove(move)
							else:
								in_chk = False
								if Square.check_sqr_threat(game_state, - int(game_state.w_king_sqr[1]), ord(game_state.w_king_sqr[0]) - 97, 'b'):
									in_chk = True
								game_state.update('w', move, w_captured = 1, w_check = in_chk)
					else:
						# move: (a-h)(1-8)(=)(Q, B, N, R)
						if self.piece_color == 'w':
							game_state.board_state[get_row - 1][get_file].add_piece(Piece.instantiate(f'{move[-1]}', 'w', self.sqr_pos[0]+'8'))
							
							if Square.check_sqr_threat(game_state, - int(game_state.w_king_sqr[1]), ord(game_state.w_king_sqr[0]) - 97, 'b'):

								game_state.undo_move([(get_row, get_file),(get_row - 1, get_file), moved_piece])

								game_state.legal_moves.remove(move)
							else:
								in_chk = False
								if Square.check_sqr_threat(game_state, - int(game_state.b_king_sqr[1]), ord(game_state.b_king_sqr[0]) - 97, 'w'):
									in_chk = True
								game_state.update('b', move, b_check = in_chk)	
						else:
							game_state.board_state[get_row + 1][get_file].add_piece(Piece.instantiate(f'{move[-1]}', 'b', self.sqr_pos[0]+'1'))

							if Square.check_sqr_threat(game_state, - int(game_state.b_king_sqr[1]), ord(game_state.b_king_sqr[0]) - 97, 'w'):

								game_state.undo_move([(get_row, get_file),(get_row + 1, get_file), moved_piece])
								game_state.legal_moves.remove(move)
							else:
								in_chk = False
								if Square.check_sqr_threat(game_state, - int(game_state.w_king_sqr[1]), ord(game_state.w_king_sqr[0]) - 97, 'b'):
									in_chk = True
								game_state.update('w', move, w_check = in_chk)	


				# simple capture
				elif 'x' in move:

					captured_piece = game_state.board_state[- int(move[3])][ord(move[2]) - 97].piece
					game_state.board_state[- int(move[3])][ord(move[2]) - 97].add_piece(self)
					if self.piece_color == 'w':

						if Square.check_sqr_threat(game_state, - int(game_state.w_king_sqr[1]), ord(game_state.w_king_sqr[0]) - 97, 'b'):

							game_state.undo_move([(get_row, get_file),(-(int(move[3])), ord(move[2]) - 97 ), moved_piece],
							piece_captured = captured_piece)

							game_state.legal_moves.remove(move)
						else:
							in_chk = False
							if Square.check_sqr_threat(game_state, - int(game_state.b_king_sqr[1]), ord(game_state.b_king_sqr[0]) - 97, 'w'):
								in_chk = True
							game_state.update('b', move, b_captured = 1, b_check = in_chk)
							if self.has_moved == False: self.has_moved = True
					else:  
						if Square.check_sqr_threat(game_state, - int(game_state.b_king_sqr[1]), ord(game_state.b_king_sqr[0]) - 97, 'w'):
							game_state.undo_move([(get_row, get_file),(-(int(move[3])), ord(move[2]) - 97 ), moved_piece],
							piece_captured = captured_piece)
							game_state.legal_moves.remove(move)
						else:
							in_chk = False
							if Square.check_sqr_threat(game_state, - int(game_state.w_king_sqr[1]), ord(game_state.w_king_sqr[0]) - 97, 'b'):
								in_chk = True
							game_state.update('w', move, w_captured = 1, w_check = in_chk)
							if self.has_moved == False: self.has_moved = True
		
				# straight move
				else:
					if abs(int(self.sqr_pos[1]) - int(move[1])) == 2:
						self.moved_2square = True
						self.passant_flag = move

					game_state.board_state[- int(move[1])][ord(move[0]) - 97].add_piece(self)
					if self.piece_color == 'w':

						if Square.check_sqr_threat(game_state, - int(game_state.w_king_sqr[1]), ord(game_state.w_king_sqr[0]) - 97, 'b'):
							game_state.undo_move([(get_row, get_file), (-int(move[1]), ord(move[0]) - 97 ), moved_piece])
							game_state.legal_moves.remove(move)
						else:
							in_chk = False
							if Square.check_sqr_threat(game_state, - int(game_state.b_king_sqr[1]), ord(game_state.b_king_sqr[0]) - 97, 'w'):
								in_chk = True
							game_state.update('b', move, b_check = in_chk)
							if self.has_moved == False: self.has_moved = True
					else:
						if Square.check_sqr_threat(game_state, - int(game_state.b_king_sqr[1]), ord(game_state.b_king_sqr[0]) - 97, 'w'):
							game_state.undo_move([(get_row, get_file),(-(int(move[1])), ord(move[0]) - 97 ), moved_piece])
							game_state.legal_moves.remove(move)
						else:
							in_chk = False
							if Square.check_sqr_threat(game_state, - int(game_state.w_king_sqr[1]), ord(game_state.w_king_sqr[0]) - 97, 'b'):
								in_chk = True
							game_state.update('w', move, w_check = in_chk)
							if self.has_moved == False: self.has_moved = True

	def check_all_moves(self, game_state: 'GameState'):		
		get_row = - int(self.sqr_pos[1])
		get_file = ord(self.sqr_pos[0]) - 97
		
		next_file = get_file + 1
		prev_file = get_file - 1

		if self.piece_color == 'w':
			next_row = get_row - 1
			next_2row = get_row - 2
			# straight moves
			if next_row > -9:
				if next_row != -8 and game_state.board_state[next_row][get_file].piece == None:
					game_state.legal_moves.add(chr(get_file + 97)+str(-next_row))

					if self.moved_2square == False and self.has_moved == False and game_state.board_state[next_2row][get_file].piece == None:
						game_state.legal_moves.add(chr(get_file + 97)+str(-next_2row))
				elif next_row == -8 and game_state.board_state[next_row][get_file].piece == None:
					prom = ['N', 'B', 'R', 'Q']
					for p in prom:
						game_state.legal_moves.add(chr(get_file + 97)+str(-next_row)+'='+f'{p}')
	
				if next_file < 8:
					# simple captures
					if next_row != -8 and game_state.board_state[next_row][next_file].piece and game_state.board_state[next_row][next_file].piece.piece_color != self.piece_color:
						game_state.legal_moves.add(chr(get_file + 97)+'x'+chr(next_file + 97)+str(-next_row))

					elif next_row == -8 and game_state.board_state[next_row][next_file].piece and game_state.board_state[next_row][next_file].piece.piece_color != self.piece_color:
						prom = ['N', 'B', 'R', 'Q']
						for p in prom:
							game_state.legal_moves.add(chr(get_file + 97)+'x'+chr(next_file + 97)+str(-next_row)+'='+f'{p}')

					# en-passant
					if (game_state.board_state[get_row][next_file].piece and
					game_state.board_state[get_row][next_file].piece.piece_color == 'b' and
					game_state.board_state[get_row][next_file].piece.piece_type == 'P' and
					game_state.board_state[get_row][next_file].piece.passant_flag == game_state.move_list[-1]):
						game_state.legal_moves.add(chr(get_file + 97)+'x'+chr(next_file + 97)+'E')
				if prev_file > -1:
					# simple captures
					if next_row != -8 and game_state.board_state[next_row][prev_file].piece and game_state.board_state[next_row][prev_file].piece.piece_color != self.piece_color:
						game_state.legal_moves.add(chr(get_file + 97)+'x'+chr(prev_file + 97)+str(-next_row))

					elif next_row == -8 and game_state.board_state[next_row][prev_file].piece and game_state.board_state[next_row][prev_file].piece.piece_color != self.piece_color:
						prom = ['N', 'B', 'R', 'Q']
						for p in prom:
							game_state.legal_moves.add(chr(get_file + 97)+'x'+chr(prev_file + 97)+str(-next_row)+'='+f'{p}')
					# en-passant 
					if (game_state.board_state[get_row][prev_file].piece and
					game_state.board_state[get_row][prev_file].piece.piece_color == 'b' and 
					game_state.board_state[get_row][prev_file].piece.piece_type == 'P' and
					game_state.board_state[get_row][prev_file].piece.passant_flag == game_state.move_list[-1]):
						game_state.legal_moves.add(chr(get_file + 97)+'x'+chr(prev_file + 97)+'E')
			
		else:
			next_row = get_row + 1
			next_2row = get_row + 2

			if next_row < 0:
				# straight moves
				if next_row != -1 and game_state.board_state[next_row][get_file].piece == None:
					game_state.legal_moves.add(chr(get_file + 97)+str(-next_row))
	
					if self.moved_2square == False and self.has_moved == False and game_state.board_state[next_2row][get_file].piece == None:
						game_state.legal_moves.add(chr(get_file + 97)+str(-next_2row))
				elif next_row == -1 and game_state.board_state[next_row][get_file].piece == None:
					prom = ['N', 'B', 'R', 'Q']
					for p in prom:
						game_state.legal_moves.add(chr(get_file + 97)+str(-next_row)+'='+f'{p}')
				if next_file < 8: 
					# simple captures
					if next_row != -1 and game_state.board_state[next_row][next_file].piece and game_state.board_state[next_row][next_file].piece.piece_color != self.piece_color:
						game_state.legal_moves.add(chr(get_file + 97)+'x'+chr(next_file + 97)+str(-next_row))

					elif next_row == -1 and game_state.board_state[next_row][next_file].piece and game_state.board_state[next_row][next_file].piece.piece_color != self.piece_color:
						prom = ['N', 'B', 'R', 'Q']
						for p in prom:
							game_state.legal_moves.add(chr(get_file + 97)+'x'+chr(next_file + 97)+'='+ f'{p}')
					# en-passant
					if (game_state.board_state[get_row][next_file].piece and
					game_state.board_state[get_row][next_file].piece.piece_color == 'w' and
					game_state.board_state[get_row][next_file].piece.piece_type == 'P' and
					game_state.board_state[get_row][next_file].piece.passant_flag == game_state.move_list[-1]):
						game_state.legal_moves.add(chr(get_file + 97)+'x'+chr(next_file + 97)+'E')
				if prev_file > -1:
					if next_row != -1 and game_state.board_state[next_row][prev_file].piece and game_state.board_state[next_row][prev_file].piece.piece_color != self.piece_color:
						game_state.legal_moves.add(chr(get_file + 97)+'x'+chr(prev_file + 97)+str(-next_row))

					elif next_row == -1 and game_state.board_state[next_row][prev_file].piece and game_state.board_state[next_row][prev_file].piece.piece_color != self.piece_color:
						prom = ['N', 'B', 'R', 'Q']
						for p in prom:
							game_state.legal_moves.add(chr(get_file + 97)+'x'+chr(next_file + 97)+'='+f'{p}')
					# en-passant	
					if (game_state.board_state[get_row][prev_file].piece and
					game_state.board_state[get_row][prev_file].piece.piece_color == 'w' and
					game_state.board_state[get_row][prev_file].piece.piece_type == 'P' and
					game_state.board_state[get_row][prev_file].piece.passant_flag == game_state.move_list[-1]):
						game_state.legal_moves.add(chr(get_file + 97)+'x'+chr(prev_file + 97)+'E')

class Rook(Piece):
	def __init__(self, piece_type: str, color: str, pos: str):
		self.piece_type = piece_type
		self.piece_color = color
		self.sqr_pos = pos
		self.has_moved = False
	#R(a-h)(1-8)(a-h)(1-8)
	#R(a-h)(1-8)x(a-h)(1-8)
	def move_piece(self, game_state: 'GameState', move: str):
		if self.piece_color == game_state.color_to_move:
			if move in game_state.legal_moves:
				get_row = - int(self.sqr_pos[1])
				get_file = ord(self.sqr_pos[0]) - 97
				end_row = - int(move[-1])
				end_file = ord(move[-2]) - 97
				moved_piece = game_state.board_state[get_row][get_file].piece
				if 'x' in move:
					captured_piece = game_state.board_state[end_row][end_file].piece

					game_state.board_state[end_row][end_file].add_piece(moved_piece)
					game_state.board_state[get_row][get_file].piece = None
					if self.piece_color == 'w':
						if Square.check_sqr_threat(game_state, - int(game_state.w_king_sqr[1]), ord(game_state.w_king_sqr[0]) - 97, 'b'):
							game_state.undo_move([(get_row, get_file), (end_row, end_file), moved_piece], piece_captured = captured_piece)
							game_state.legal_moves.remove(move)

						else:
							in_chk = False
							if Square.check_sqr_threat(game_state, - int(game_state.b_king_sqr[1]), ord(game_state.b_king_sqr[0]) - 97, 'w'):
								in_chk = True
							game_state.update('b', move, b_captured = 1, b_check = in_chk)
							if self.has_moved == False: self.has_moved = True

					else:
						if Square.check_sqr_threat(game_state, - int(game_state.b_king_sqr[1]), ord(game_state.b_king_sqr[0]) - 97, 'w'):
							game_state.undo_move([(get_row, get_file), (end_row, end_file), moved_piece], piece_captured = captured_piece)
							game_state.legal_moves.remove(move)

						else:
							in_chk = False
							if Square.check_sqr_threat(game_state, - int(game_state.w_king_sqr[1]), ord(game_state.w_king_sqr[0]) - 97, 'b'):
								in_chk = True
							game_state.update('w', move, w_captured = 1, w_check = in_chk)
							if self.has_moved == False: self.has_moved = True
				else:
					game_state.board_state[end_row][end_file].add_piece(moved_piece)
					game_state.board_state[get_row][get_file].piece = None
					if self.piece_color == 'w':
						if Square.check_sqr_threat(game_state, - int(game_state.w_king_sqr[1]), ord(game_state.w_king_sqr[0]) - 97, 'b'):
							game_state.undo_move([(get_row, get_file), (end_row, end_file), moved_piece])
							game_state.legal_moves.remove(move)

						else:
							in_chk = False
							if Square.check_sqr_threat(game_state, - int(game_state.b_king_sqr[1]), ord(game_state.b_king_sqr[0]) - 97, 'w'):
								in_chk = True
							game_state.update('b', move, b_check = in_chk)
							if self.has_moved == False: self.has_moved = True	

					else:		
						if Square.check_sqr_threat(game_state, - int(game_state.b_king_sqr[1]), ord(game_state.b_king_sqr[0]) - 97, 'w'):
							game_state.undo_move([(get_row, get_file), (end_row, end_file), moved_piece])
							game_state.legal_moves.remove(move)

						else:
							in_chk = False
							if Square.check_sqr_threat(game_state, - int(game_state.w_king_sqr[1]), ord(game_state.w_king_sqr[0]) - 97, 'b'):
								in_chk = True
							game_state.update('w', move, w_check = in_chk)
							if self.has_moved == False: self.has_moved = True	



	def check_all_moves(self, game_state: 'GameState'):
		get_row = - int(self.sqr_pos[1])
		get_file = ord(self.sqr_pos[0]) - 97

		# R(a-h)(1-8)(a-h)(1-8)
		# R(a-h)(1-8)(a-h)(1-8)
		Rxu_moves = [get_row - r for r in range(1, get_row + 8 + 1)]
		Rxd_moves = [get_row + r for r in range(1, -get_row)]
		Ryr_moves = [get_file + f for f in range(1, 7 - get_file  + 1)]
		Ryl_moves = [get_file - f for f in range(1, get_file + 1)]
		
		self.check_rows(game_state, get_file, get_row, Rxu_moves)
		self.check_rows(game_state, get_file, get_row, Rxd_moves)
		self.check_files(game_state, get_file, get_row, Ryr_moves)
		self.check_files(game_state, get_file, get_row, Ryl_moves)

	def check_rows(self, game_state: 'GameState', get_file: int, get_row: int, moves: []):
		for r in moves:
			if game_state.board_state[r][get_file].piece == None:
				game_state.legal_moves.add('R'+chr(get_file + 97)+str(-get_row)+chr(get_file + 97)+str(-r))

			elif game_state.board_state[r][get_file].piece.piece_color != self.piece_color:
				game_state.legal_moves.add('R'+chr(get_file + 97)+str(-get_row)+'x'+chr(get_file + 97)+str(-r))
				break
			else:
				break
	def check_files(self, game_state: 'GameState', get_file: int, get_row: int, moves: []):
		for f in moves:
			if game_state.board_state[get_row][f].piece == None:
				game_state.legal_moves.add('R'+chr(get_file + 97)+str(-get_row)+chr(f + 97)+str(-get_row))

			elif game_state.board_state[get_row][f].piece.piece_color != self.piece_color:
				game_state.legal_moves.add('R'+chr(get_file + 97)+str(-get_row)+'x'+chr(f + 97)+str(-get_row))
				break
			else:
				break

class Knight(Piece):
	def __init__(self, piece_type: str, color: str, pos: str):
		self.piece_type = piece_type
		self.piece_color = color
		self.sqr_pos = pos
	#N(a-h)(1-8)(a-h)(1-8)
	#N(a-h)(1-8)'x'(a-h)(1-8)
	def move_piece(self, game_state: 'GameState', move: str):
		if self.piece_color == game_state.color_to_move:
			if move in game_state.legal_moves:
				get_row = - int(self.sqr_pos[1])
				get_file = ord(self.sqr_pos[0]) - 97
				end_row = - int(move[-1])
				end_file = ord(move[-2]) - 97
				moved_piece = game_state.board_state[get_row][get_file].piece
				if 'x' in move:
					captured_piece = game_state.board_state[end_row][end_file].piece

					game_state.board_state[end_row][end_file].add_piece(moved_piece)
					game_state.board_state[get_row][get_file].piece = None
					if self.piece_color == 'w':
						if Square.check_sqr_threat(game_state, - int(game_state.w_king_sqr[1]), ord(game_state.w_king_sqr[0]) - 97, 'b'):
							game_state.undo_move([(get_row, get_file), (end_row, end_file), moved_piece], piece_captured = captured_piece)
							game_state.legal_moves.remove(move)

						else:
							in_chk = False
							if Square.check_sqr_threat(game_state, - int(game_state.b_king_sqr[1]), ord(game_state.b_king_sqr[0]) - 97, 'w'):
								in_chk = True
							game_state.update('b', move, b_captured = 1, b_check = in_chk)


					else:
						if Square.check_sqr_threat(game_state, - int(game_state.b_king_sqr[1]), ord(game_state.b_king_sqr[0]) - 97, 'w'):
							game_state.undo_move([(get_row, get_file), (end_row, end_file), moved_piece], piece_captured = captured_piece)
							game_state.legal_moves.remove(move)

						else:
							in_chk = False
							if Square.check_sqr_threat(game_state, - int(game_state.w_king_sqr[1]), ord(game_state.w_king_sqr[0]) - 97, 'b'):
								in_chk = True
							game_state.update('w', move, w_captured = 1, w_check = in_chk)

				else:
					game_state.board_state[end_row][end_file].add_piece(moved_piece)
					game_state.board_state[get_row][get_file].piece = None

					if self.piece_color == 'w':
						if Square.check_sqr_threat(game_state, - int(game_state.w_king_sqr[1]), ord(game_state.w_king_sqr[0]) - 97, 'b'):

							game_state.undo_move([(get_row, get_file), (end_row, end_file), moved_piece])
							game_state.legal_moves.remove(move)

						else:
							in_chk = False
							if Square.check_sqr_threat(game_state, - int(game_state.b_king_sqr[1]), ord(game_state.b_king_sqr[0]) - 97, 'w'):
								in_chk = True
							game_state.update('b', move, b_check = in_chk)
	

					else:	

						if Square.check_sqr_threat(game_state, - int(game_state.b_king_sqr[1]), ord(game_state.b_king_sqr[0]) - 97, 'w'):

							game_state.undo_move([(get_row, get_file), (end_row, end_file), moved_piece])
							game_state.legal_moves.remove(move)

						else:
							in_chk = False
							if Square.check_sqr_threat(game_state, - int(game_state.w_king_sqr[1]), ord(game_state.w_king_sqr[0]) - 97, 'b'):
								in_chk = True
							game_state.update('w', move, w_check = in_chk)

	def check_all_moves(self, game_state: 'GameState'):
		get_row = - int(self.sqr_pos[1])
		get_file = ord(self.sqr_pos[0]) - 97

		# get [x][y]: Nx[0-1] w/ Ny[0-1] and Nx[2-3] w/ Ny[2-3]
		Nx_moves = [get_row - 1, get_row + 1, get_row - 2, get_row + 2]
		Ny_moves = [get_file - 2, get_file + 2, get_file - 1, get_file + 1] 

		for r in Nx_moves[0:2]:
			for f in Ny_moves[0:2]:
				if ((-9 < r < 0) and (-1 < f < 8)):
					if game_state.board_state[r][f].piece == None:
						game_state.legal_moves.add('N'+chr(get_file + 97)+str(-get_row)+chr(f + 97)+str(-r))
					
					elif game_state.board_state[r][f].piece.piece_color != self.piece_color:
						game_state.legal_moves.add('N'+chr(get_file + 97)+str(-get_row)+'x'+chr(f + 97)+str(-r))
		for r in Nx_moves[2:4]:
			for f in Ny_moves[2:4]:
				if ((-9 < r < 0) and (-1 < f < 8)):
					if game_state.board_state[r][f].piece == None:
						game_state.legal_moves.add('N'+chr(get_file + 97)+str(-get_row)+chr(f + 97)+str(-r))
					
					elif game_state.board_state[r][f].piece.piece_color != self.piece_color:
						game_state.legal_moves.add('N'+chr(get_file + 97)+str(-get_row)+'x'+chr(f + 97)+str(-r))

class Bishop(Piece):
	def __init__(self, piece_type: str, color: str, pos: str):
		self.piece_type = piece_type
		self.piece_color = color
		self.sqr_pos = pos
	def move_piece(self, game_state: 'GameState', move: str):
		if self.piece_color == game_state.color_to_move:
			if move in game_state.legal_moves:
				get_row = - int(self.sqr_pos[1])
				get_file = ord(self.sqr_pos[0]) - 97
				end_row = - int(move[-1])
				end_file = ord(move[-2]) - 97
				moved_piece = game_state.board_state[get_row][get_file].piece
				if 'x' in move:
					captured_piece = game_state.board_state[end_row][end_file].piece

					game_state.board_state[end_row][end_file].add_piece(moved_piece)
					game_state.board_state[get_row][get_file].piece = None
					if self.piece_color == 'w':
						if Square.check_sqr_threat(game_state, - int(game_state.w_king_sqr[1]), ord(game_state.w_king_sqr[0]) - 97, 'b'):
							game_state.undo_move([(get_row, get_file), (end_row, end_file), moved_piece], piece_captured = captured_piece)
							game_state.legal_moves.remove(move)

						else:
							in_chk = False
							if Square.check_sqr_threat(game_state, - int(game_state.b_king_sqr[1]), ord(game_state.b_king_sqr[0]) - 97, 'w'):
								in_chk = True
							game_state.update('b', move, b_captured = 1, b_check = in_chk)


					else:
						if Square.check_sqr_threat(game_state, - int(game_state.b_king_sqr[1]), ord(game_state.b_king_sqr[0]) - 97, 'w'):
							game_state.undo_move([(get_row, get_file), (end_row, end_file), moved_piece], piece_captured = captured_piece)
							game_state.legal_moves.remove(move)

						else:
							in_chk = False
							if Square.check_sqr_threat(game_state, - int(game_state.w_king_sqr[1]), ord(game_state.w_king_sqr[0]) - 97, 'b'):
								in_chk = True
							game_state.update('w', move, w_captured = 1, w_check = in_chk)

				else:
					game_state.board_state[end_row][end_file].add_piece(moved_piece)
					game_state.board_state[get_row][get_file].piece = None

					if self.piece_color == 'w':
						if Square.check_sqr_threat(game_state, - int(game_state.w_king_sqr[1]), ord(game_state.w_king_sqr[0]) - 97, 'b'):
							game_state.undo_move([(get_row, get_file), (end_row, end_file), moved_piece])
							game_state.legal_moves.remove(move)

						else:
							in_chk = False
							if Square.check_sqr_threat(game_state, - int(game_state.b_king_sqr[1]), ord(game_state.b_king_sqr[0]) - 97, 'w'):
								in_chk = True
							game_state.update('b', move, b_check = in_chk)
	

					else:		
						if Square.check_sqr_threat(game_state, - int(game_state.b_king_sqr[1]), ord(game_state.b_king_sqr[0]) - 97, 'w'):
							game_state.undo_move([(get_row, get_file), (end_row, end_file), moved_piece])
							game_state.legal_moves.remove(move)

						else:
							in_chk = False
							if Square.check_sqr_threat(game_state, - int(game_state.w_king_sqr[1]), ord(game_state.w_king_sqr[0]) - 97, 'b'):
								in_chk = True
							game_state.update('w', move, w_check = in_chk)
	def check_all_moves(self, game_state: 'GameState'):
		get_row = - int(self.sqr_pos[1])
		get_file = ord(self.sqr_pos[0]) - 97

		Bxy1_moves = [(get_row - sq, get_file + sq) for sq in range(1, min(8 + get_row, 7 - get_file) + 1)]
		Bxy2_moves = [(get_row - sq, get_file - sq) for sq in range(1, min(8 + get_row, get_file) + 1)]
		Bxy3_moves = [(get_row + sq, get_file - sq) for sq in range(1, min(-get_row -1, get_file) + 1)]
		Bxy4_moves = [(get_row + sq, get_file + sq) for sq in range(1, min(-get_row -1, 7 - get_file) + 1)]
		self.check_diagonals(game_state, get_file, get_row, Bxy1_moves)
		self.check_diagonals(game_state, get_file, get_row, Bxy2_moves)
		self.check_diagonals(game_state, get_file, get_row, Bxy3_moves)
		self.check_diagonals(game_state, get_file, get_row, Bxy4_moves)
	def check_diagonals(self, game_state: 'GameState', get_file: int, get_row: int, moves: []):
		for xy in moves:
			if game_state.board_state[xy[0]][xy[1]].piece == None:
				game_state.legal_moves.add('B'+chr(get_file + 97)+str(-get_row)+chr(xy[1] + 97)+str(- xy[0]))
			elif game_state.board_state[xy[0]][xy[1]].piece.piece_color != self.piece_color:
				game_state.legal_moves.add('B'+chr(get_file + 97)+str(-get_row)+'x'+chr(xy[1] + 97)+str(- xy[0]))
				break
			else:
				break

class Queen(Piece):
	def __init__(self, piece_type: str, color: str, pos: str):
		self.piece_type = piece_type
		self.piece_color = color
		self.sqr_pos = pos
	def move_piece(self, game_state: 'GameState', move: str):
		if self.piece_color == game_state.color_to_move:
			if move in game_state.legal_moves:
				get_row = - int(self.sqr_pos[1])
				get_file = ord(self.sqr_pos[0]) - 97
				end_row = - int(move[-1])
				end_file = ord(move[-2]) - 97
				moved_piece = game_state.board_state[get_row][get_file].piece
				if 'x' in move:
					captured_piece = game_state.board_state[end_row][end_file].piece

					game_state.board_state[end_row][end_file].add_piece(moved_piece)
					game_state.board_state[get_row][get_file].piece = None
					if self.piece_color == 'w':
						if Square.check_sqr_threat(game_state, - int(game_state.w_king_sqr[1]), ord(game_state.w_king_sqr[0]) - 97, 'b'):
							game_state.undo_move([(get_row, get_file), (end_row, end_file), moved_piece], piece_captured = captured_piece)
							game_state.legal_moves.remove(move)

						else:
							in_chk = False
							if Square.check_sqr_threat(game_state, - int(game_state.b_king_sqr[1]), ord(game_state.b_king_sqr[0]) - 97, 'w'):
								in_chk = True
							game_state.update('b', move, b_captured = 1, b_check = in_chk)


					else:
						if Square.check_sqr_threat(game_state, - int(game_state.b_king_sqr[1]), ord(game_state.b_king_sqr[0]) - 97, 'w'):
							game_state.undo_move([(get_row, get_file), (end_row, end_file), moved_piece], piece_captured = captured_piece)
							game_state.legal_moves.remove(move)

						else:
							in_chk = False
							if Square.check_sqr_threat(game_state, - int(game_state.w_king_sqr[1]), ord(game_state.w_king_sqr[0]) - 97, 'b'):
								in_chk = True
							game_state.update('w', move, w_captured = 1, w_check = in_chk)

				else:
					game_state.board_state[end_row][end_file].add_piece(moved_piece)
					game_state.board_state[get_row][get_file].piece = None
					if self.piece_color == 'w':
						if Square.check_sqr_threat(game_state, - int(game_state.w_king_sqr[1]), ord(game_state.w_king_sqr[0]) - 97, 'b'):
							game_state.undo_move([(get_row, get_file), (end_row, end_file), moved_piece])
							game_state.legal_moves.remove(move)

						else:
							in_chk = False
							if Square.check_sqr_threat(game_state, - int(game_state.b_king_sqr[1]), ord(game_state.b_king_sqr[0]) - 97, 'w'):
								in_chk = True
							game_state.update('b', move, b_check = in_chk)
	

					else:		
						if Square.check_sqr_threat(game_state, - int(game_state.b_king_sqr[1]), ord(game_state.b_king_sqr[0]) - 97, 'w'):
							game_state.undo_move([(get_row, get_file), (end_row, end_file), moved_piece])
							game_state.legal_moves.remove(move)

						else:
							in_chk = False
							if Square.check_sqr_threat(game_state, - int(game_state.w_king_sqr[1]), ord(game_state.w_king_sqr[0]) - 97, 'b'):
								in_chk = True
							game_state.update('w', move, w_check = in_chk)
	def check_all_moves(self, game_state: 'GameState'):
		get_row = - int(self.sqr_pos[1])
		get_file = ord(self.sqr_pos[0]) - 97

		Qxy1_moves = [(get_row - sq, get_file + sq) for sq in range(1, min(8 + get_row, 7 - get_file) + 1)]
		Qxy2_moves = [(get_row - sq, get_file - sq) for sq in range(1, min(8 + get_row, get_file) + 1)]
		Qxy3_moves = [(get_row + sq, get_file - sq) for sq in range(1, min(-get_row -1, get_file) + 1)]
		Qxy4_moves = [(get_row + sq, get_file + sq) for sq in range(1, min(-get_row -1, 7 - get_file) + 1)]

		Qxu_moves = [get_row - r for r in range(1, get_row + 8 + 1)]
		Qxd_moves = [get_row + r for r in range(1, -get_row)]
		Qyr_moves = [get_file + f for f in range(1, 7 - get_file + 1)]
		Qyl_moves = [get_file - f for f in range(1, get_file + 1)]
	
		for moves in (Qxy1_moves, Qxy2_moves, Qxy3_moves, Qxy4_moves):
			self.check_diagonals(game_state, get_file, get_row, moves)

		for moves in (Qxu_moves, Qxd_moves):
			self.check_rows(game_state, get_file, get_row, moves)

		for moves in (Qyr_moves, Qyl_moves):
			self.check_files(game_state, get_file, get_row, moves)

	def check_diagonals(self, game_state: 'GameState', get_file: int, get_row: int, moves: []):
		for xy in moves:
			if game_state.board_state[xy[0]][xy[1]].piece == None:
				game_state.legal_moves.add('Q'+chr(get_file + 97)+str(-get_row)+chr(xy[1] + 97)+str(- xy[0]))
			elif game_state.board_state[xy[0]][xy[1]].piece.piece_color != self.piece_color:
				game_state.legal_moves.add('Q'+chr(get_file + 97)+str(-get_row)+'x'+chr(xy[1] + 97)+str(- xy[0]))
				break
			else:
				break

	def check_rows(self, game_state: 'GameState', get_file: int, get_row: int, moves: []):
		for r in moves:
			if game_state.board_state[r][get_file].piece == None:
				game_state.legal_moves.add('Q'+chr(get_file + 97)+str(-get_row)+chr(get_file + 97)+str(-r))
			elif game_state.board_state[r][get_file].piece.piece_color != self.piece_color:
				game_state.legal_moves.add('Q'+chr(get_file + 97)+str(-get_row)+'x'+chr(get_file + 97)+str(-r))
				break
			else:
				break

	def check_files(self, game_state: 'GameState', get_file: int, get_row: int, moves: []):
		for f in moves:
			if game_state.board_state[get_row][f].piece == None:
				game_state.legal_moves.add('Q'+chr(get_file + 97)+str(-get_row)+chr(f + 97)+str(-get_row))
			elif game_state.board_state[get_row][f].piece.piece_color != self.piece_color:
				game_state.legal_moves.add('Q'+chr(get_file + 97)+str(-get_row)+'x'+chr(f + 97)+str(-get_row))
				break
			else:
				break

class King(Piece):
	def __init__(self, piece_type: str, color: str, pos: str):
		self.piece_type = piece_type
		self.piece_color = color
		self.sqr_pos = pos
		self.has_moved = False
	def move_piece(self, game_state: 'GameState', move: str):
		if self.piece_color == game_state.color_to_move:
			if move in game_state.legal_moves:
				get_row = - int(self.sqr_pos[1])
				get_file = ord(self.sqr_pos[0]) - 97
				if move != 'O-O' and move != 'O-O-O':
					end_row = - int(move[-1])
					end_file = ord(move[-2]) - 97
				elif move == 'O-O':
					end_row = get_row
					end_file = get_file + 2
				else:
					end_row = get_row
					end_file = get_file - 2
				moved_piece = game_state.board_state[get_row][get_file].piece
				if 'x' in move:
					captured_piece = game_state.board_state[end_row][end_file].piece

					game_state.board_state[end_row][end_file].add_piece(moved_piece)
					game_state.board_state[get_row][get_file].piece = None
					if self.piece_color == 'w':
						get_kng_sqr = game_state.w_king_sqr
						game_state.w_king_sqr = move[-2]+move[-1]
						if Square.check_sqr_threat(game_state, end_row, end_file, 'b'):
							game_state.undo_move([(get_row, get_file), (end_row, end_file), moved_piece], piece_captured = captured_piece)
							game_state.w_king_sqr = get_kng_sqr
							game_state.legal_moves.remove(move)

						else:
							in_chk = False
							if Square.check_sqr_threat(game_state, - int(game_state.b_king_sqr[1]), ord(game_state.b_king_sqr[0]) - 97, 'w'):
								in_chk = True
							game_state.update('b', move, b_captured = 1, b_check = in_chk, w_kng = move[-2]+move[-1])
							if self.has_moved == False: self.has_moved = True


					else:
						get_kng_sqr = game_state.b_king_sqr
						game_state.b_king_sqr = move[-2]+move[-1]
						if Square.check_sqr_threat(game_state, end_row, end_file, 'w'):
							game_state.undo_move([(get_row, get_file), (end_row, end_file), moved_piece], piece_captured = captured_piece)
							game_state.b_king_sqr = get_kng_sqr
							game_state.legal_moves.remove(move)

						else:
							in_chk = False
							if Square.check_sqr_threat(game_state, - int(game_state.w_king_sqr[1]), ord(game_state.w_king_sqr[0]) - 97, 'b'):
								in_chk = True
							game_state.update('w', move, w_captured = 1, w_check = in_chk, b_kng = move[-2]+move[-1])
							if self.has_moved == False: self.has_moved = True

				else:

					game_state.board_state[end_row][end_file].add_piece(moved_piece)
					game_state.board_state[get_row][get_file].piece = None
					if move == 'O-O':
						game_state.board_state[get_row][get_file + 1].add_piece(game_state.board_state[get_row][7].piece)
						game_state.board_state[get_row][7].piece = None
						game_state.board_state[get_row][get_file + 1].piece.has_moved = True
						if self.piece_color == 'w':
							in_chk = False
							if Square.check_sqr_threat(game_state, - int(game_state.b_king_sqr[1]), ord(game_state.b_king_sqr[0]) - 97, 'w'):
								in_chk = True
							game_state.update('b', move, b_check = in_chk, w_kng = 'g1')
							if self.has_moved == False: self.has_moved = True
						else:
							in_chk = False
							if Square.check_sqr_threat(game_state, - int(game_state.w_king_sqr[1]), ord(game_state.w_king_sqr[0]) - 97, 'b'):
								in_chk = True
							game_state.update('w', move, w_check = in_chk, b_kng = 'g8')
							if self.has_moved == False: self.has_moved = True
						#game_state.w_king_sqr = 'a6'
						#game_state.b_king_sqr = 'h6'
					elif move == 'O-O-O':
						game_state.board_state[get_row][get_file - 1].add_piece(game_state.board_state[get_row][0].piece)
						game_state.board_state[get_row][0].piece = None
						game_state.board_state[get_row][get_file - 1].piece.has_moved = True
						if self.piece_color == 'w':
							in_chk = False
							if Square.check_sqr_threat(game_state, - int(game_state.b_king_sqr[1]), ord(game_state.b_king_sqr[0]) - 97, 'w'):
								in_chk = True
							game_state.update('b', move, b_check = in_chk, w_kng = 'c1')
							if self.has_moved == False: self.has_moved = True
						else:
							in_chk = False
							if Square.check_sqr_threat(game_state, - int(game_state.w_king_sqr[1]), ord(game_state.w_king_sqr[0]) - 97, 'b'):
								in_chk = True
							game_state.update('w', move, w_check = in_chk, b_kng = 'c8')
							if self.has_moved == False: self.has_moved = True
						#game_state.w_king_sqr = 'a3'
						#game_state.b_king_sqr = 'h3'
					else:

						if self.piece_color == 'w':
							get_kng_sqr = game_state.w_king_sqr
							game_state.w_king_sqr = move[-2]+move[-1]
							if Square.check_sqr_threat(game_state, end_row, end_file, 'b'):
								game_state.undo_move([(get_row, get_file), (end_row, end_file), moved_piece])
								game_state.w_king_sqr = get_kng_sqr
								game_state.legal_moves.remove(move)	
							else:
								in_chk = False
								if Square.check_sqr_threat(game_state, - int(game_state.b_king_sqr[1]), ord(game_state.b_king_sqr[0]) - 97, 'w'):
									in_chk = True
								game_state.update('b', move, b_check = in_chk, w_kng = move[-2]+move[-1])
								if self.has_moved == False: self.has_moved = True
		
	
						else:
							get_kng_sqr = game_state.b_king_sqr	
							game_state.b_king_sqr = move[-2]+move[-1]
							if Square.check_sqr_threat(game_state, end_row, end_file, 'w'):
								game_state.undo_move([(get_row, get_file), (end_row, end_file), moved_piece])
								game_state.b_king_sqr = get_kng_sqr
								game_state.legal_moves.remove(move)	
							else:
								in_chk = False
								if Square.check_sqr_threat(game_state, - int(game_state.w_king_sqr[1]), ord(game_state.w_king_sqr[0]) - 97, 'b'):
									in_chk = True
								game_state.update('w', move, w_check = in_chk, b_kng = move[-2]+move[-1])
								if self.has_moved == False: self.has_moved = True

	def check_all_moves(self, game_state: 'GameState'):
		get_row = - int(self.sqr_pos[1])
		get_file = ord(self.sqr_pos[0]) - 97

		
		Kx_moves = [get_row + 1, get_row - 1]
		Ky_moves = [get_file + 1, get_file - 1]

		Kxy_moves = [(get_row - 1, get_file + 1), (get_row - 1, get_file - 1), (get_row + 1, get_file - 1),(get_row + 1, get_file + 1)]
		for r in reversed(Kx_moves):
			if  - 8 > r or r > - 1:
				Kx_moves.remove(r)
		for f in reversed(Ky_moves):
			if f > 7 or f < 0:
				Ky_moves.remove(f)
		for xy in reversed(Kxy_moves):
			if xy[0] not in Kx_moves or xy[1] not in Ky_moves:
				Kxy_moves.remove(xy)
		self.check_king_proximity(game_state, (get_row, get_file), Kx_moves, Ky_moves, Kxy_moves)
		castle_moves = self.check_castle(game_state, get_row, get_file)
		for mv in castle_moves:
			game_state.legal_moves.add(mv)

		
		
		for mv in reversed(Kx_moves):
			if 0 > mv > -9:
				if game_state.board_state[mv][get_file].piece == None:
					game_state.legal_moves.add('K'+chr(get_file + 97)+str(-mv))
				elif game_state.board_state[mv][get_file].piece.piece_color != self.piece_color:
					game_state.legal_moves.add('K'+'x'+chr(get_file + 97)+str(-mv))
			else: Kx_moves.remove(mv)

		for mv in reversed(Ky_moves):
			if -1 < mv < 8:
				if game_state.board_state[get_row][mv].piece == None:
					game_state.legal_moves.add('K'+chr(mv + 97)+str(- get_row))
				elif game_state.board_state[get_row][mv].piece.piece_color != self.piece_color:
					game_state.legal_moves.add('K'+'x'+chr(mv + 97)+str(- get_row))
			else: Ky_moves.remove(mv)
		for mv in reversed(Kxy_moves):
			if game_state.board_state[mv[0]][mv[1]].piece == None:
				game_state.legal_moves.add('K'+chr(mv[1] + 97)+str(- mv[0]))

			elif game_state.board_state[mv[0]][mv[1]].piece.piece_color != self.piece_color:
				game_state.legal_moves.add('K'+'x'+chr(mv[1] + 97)+str(- mv[0]))

	def check_king_proximity(self, game_state: 'GameState', pos: (), x_moves: [], y_moves: [], xy_moves: []):
		if self.piece_color == 'w': 
			enemy_king_get_row = - int(game_state.b_king_sqr[1])
			enemy_king_get_file = ord(game_state.b_king_sqr[0]) - 97
		else: 
			enemy_king_get_row = - int(game_state.w_king_sqr[1])
			enemy_king_get_file = ord(game_state.w_king_sqr[0]) - 97

		eKx_moves = [enemy_king_get_row + 1, enemy_king_get_row - 1]
		eKy_moves = [enemy_king_get_file + 1, enemy_king_get_file - 1]
		eKxy_moves = [(enemy_king_get_row - 1, enemy_king_get_file + 1), (enemy_king_get_row - 1, enemy_king_get_file - 1),
		(enemy_king_get_row + 1, enemy_king_get_file - 1),(enemy_king_get_row + 1, enemy_king_get_file + 1)]
		for r in reversed(eKx_moves):
			if  - 8 > r or r > - 1:
				eKx_moves.remove(r)
		for f in reversed(eKy_moves):
			if f > 7 or f < 0:
				eKy_moves.remove(f)
		for xy in reversed(eKxy_moves):
			if xy[0] not in eKx_moves or xy[1] not in eKy_moves:
				eKxy_moves.remove(xy)

		for x in reversed(x_moves): 
			if x in eKx_moves and abs(pos[1] - enemy_king_get_file) <= 1:
				x_moves.remove(x)
		for y in reversed(y_moves):
			if y in eKy_moves and abs(pos[0] - enemy_king_get_row) <= 1:
				y_moves.remove(y)
		for xy in reversed(xy_moves):
			if (xy in eKxy_moves or (xy[0] in eKx_moves and abs(xy[1] - enemy_king_get_file) <= 1) or (xy[1] in eKy_moves and abs(xy[0] - enemy_king_get_row) <= 1)):
				xy_moves.remove(xy)
	def check_castle(self, game_state: 'GameState', get_row: int, get_file: int):
		castle = []
		if self.has_moved == False:


			O_O_O = get_file - 2
			O_O = get_file + 2
		
			if self.piece_color == 'w': e_color = 'b'
			else: e_color = 'w'
			e_kng_sqr = getattr(game_state, e_color+'_king_sqr')
			e_get_row = - int(e_kng_sqr[1])
			e_get_file = ord(e_kng_sqr[0]) - 97
			if (game_state.board_state[get_row][0].piece and game_state.board_state[get_row][0].piece.piece_type == 'R'
			and game_state.board_state[get_row][0].piece.has_moved == False):
				
				st = [] 
				for f in range(O_O_O, 5):
					if Square.check_sqr_threat(game_state, get_row, f, e_color):
						st.extend(Square.check_sqr_threat(game_state, get_row, f, e_color))
				if not st:
					filled = False
					for f in range(O_O_O, get_file):
						if game_state.board_state[get_row][f].piece:
							filled = True
							break
					if filled == False and not self.kng_castle_proximity((get_row, O_O_O), (e_get_row, e_get_file)):
						castle.append('O-O-O')		
						

			if (game_state.board_state[get_row][7].piece and game_state.board_state[get_row][7].piece.piece_type == 'R'
			and game_state.board_state[get_row][7].piece.has_moved == False):
				st = []
				for f in range(get_file, O_O + 1):
					if Square.check_sqr_threat(game_state, get_row, f, e_color):
						st.extend(Square.check_sqr_threat(game_state, get_row, f, e_color))
				if not st:
					filled = False
					for f in range(get_file + 1, O_O + 1):
						if game_state.board_state[get_row][f].piece:
							filled = True
							break
					if filled == False and not self.kng_castle_proximity((get_row, O_O), (e_get_row, e_get_file)):	
						castle.append('O-O')	
						
		return castle
	def kng_castle_proximity(self, castle_sqr: (), e_kng_pos: ()):
		if abs(e_kng_pos[0] - castle_sqr[0]) <= 1:
			if abs(e_kng_pos[1] - castle_sqr[1]) <= 1:
				return True
		return False
class GameState():
	def __init__(self, Board: 'Board', mv = 'w', wk_sqr = 'e1', bk_sqr = 'e8'):
		self.board_state = Board.board
		self.color_to_move = mv
		self.move_list = []
		self.legal_moves = set()
		self.w_in_check = False
		self.b_in_check = False
		self.w_pieces = 16
		self.b_pieces = 16
		self.w_king_sqr = wk_sqr
		self.b_king_sqr = bk_sqr
		self.check_all_moves()

	def update(self, mv: str, last_mv: str, w_captured = 0, b_captured = 0, w_check = False, b_check = False, **kng_sqr: '{w_kng: , b_kng: }'):
		self.color_to_move = mv
		self.move_list.append(last_mv)
		self.w_in_check = w_check
		self.b_in_check = b_check
		self.w_pieces -= w_captured
		self.b_pieces -= b_captured
		for kng, sqr in kng_sqr.items():
			if kng == 'w_kng':
				self.w_king_sqr = kng_sqr['w_kng']
			elif kng == 'b_kng':	
				self.b_king_sqr = kng_sqr['b_kng']
		self.legal_moves.clear()
		self.check_all_moves()
	def undo_move(self, piece_moved: [], piece_captured = None, ep = False):
		if piece_captured != None:
			if ep:
				self.board_state[piece_moved[0][0]][piece_moved[0][1]].add_piece(piece_moved[2])
				self.board_state[piece_moved[1][0]][piece_moved[1][1]].piece =  None
				self.board_state[piece_moved[0][0]][piece_moved[1][1]].add_piece(piece_captured)
			else:
				self.board_state[piece_moved[0][0]][piece_moved[0][1]].add_piece(piece_moved[2])
				self.board_state[piece_moved[1][0]][piece_moved[1][1]].add_piece(piece_captured)
		else:
			
			self.board_state[piece_moved[0][0]][piece_moved[0][1]].add_piece(piece_moved[2])
			self.board_state[piece_moved[1][0]][piece_moved[1][1]].piece = None


	def check_all_moves(self):
		check_counter = 0
		class Checked(Exception): pass
		try:
			if self.color_to_move == 'b':
				for r in range(8):
					for f in range(8):
						if self.board_state[r][f].piece and self.board_state[r][f].piece.piece_color == self.color_to_move:
							self.board_state[r][f].piece.check_all_moves(self)
							check_counter += 1
						if check_counter == self.b_pieces:
							raise Checked
	
			else:
				for r in range(7, -1, -1):
					for f in range(8):
						if self.board_state[r][f].piece and self.board_state[r][f].piece.piece_color == self.color_to_move:
							self.board_state[r][f].piece.check_all_moves(self)
							check_counter += 1
						if check_counter == self.w_pieces:
							raise Checked
		except Checked:
			pass

class Square():
	def __init__(self, color: bool, sqr_name: str, piece = None):
		self.sqr_name = sqr_name
		self.color = color
		self.piece = piece
		
	def add_piece(self, piece: 'Piece'):
		self.piece = piece
		piece.sqr_pos = self.sqr_name

	@staticmethod
	def check_sqr_threat(game_state: 'GameState', get_row: int, get_file: int, enemy_color: str, search_dt = False):

		u_rows = [get_row - r for r in range(1, get_row + 8 + 1)]
		d_rows = [get_row + r for r in range(1, -get_row)]

		r_files = [get_file + f for f in range(1, 7 - get_file + 1)]
		l_files = [get_file - f for f in range(1, get_file + 1)] 
		
		xy1_diagonal = [(get_row - sq, get_file + sq) for sq in range(1, min(8 + get_row, 7 - get_file) + 1)]
		xy2_diagonal = [(get_row - sq, get_file - sq) for sq in range(1, min(8 + get_row, get_file) + 1)]
		xy3_diagonal = [(get_row + sq, get_file - sq) for sq in range(1, min(-get_row -1, get_file) + 1)]
		xy4_diagonal = [(get_row + sq, get_file + sq) for sq in range(1, min(-get_row -1, 7 - get_file) + 1)]
		xy_diagonal = [xy1_diagonal, xy2_diagonal, xy3_diagonal, xy4_diagonal]

 
		Nx = [get_row - 1, get_row + 1, get_row - 2, get_row + 2]
		Ny = [get_file - 2, get_file + 2, get_file - 1, get_file + 1]
		Nxy =[(x, y) for x in Nx[0:2] for y in Ny[0:2] if ((-9 < x < 0) and (8 > y > -1))]+[(x, y) for x in Nx[2:4] for y in Ny[2:4] if ((-9 < x < 0) and (8 > y > -1))]
		
		threats = []
		for sqr_xy in Nxy:
			N_t = Square.check_knight(game_state, enemy_color, sqr_xy)
			if N_t:
				threats.append(N_t)
				if search_dt == False: return threats
				break
		for sqr_xy in xy_diagonal:
			d_t = Square.check_diagonals(game_state, enemy_color, get_row, sqr_xy)
			if d_t:
				threats.append(d_t)
				if search_dt == False: return threats
				break
		if len(threats) == 2 and search_dt: return threats

		for r in [u_rows, d_rows]:
			r_t = Square.check_rows(game_state, get_file, enemy_color, r) 
			if r_t:
				threats.append(r_t)
				if search_dt == False: return threats
				break
		if len(threats) == 2 and search_dt: return threats

		for f in [r_files, l_files]:
			f_t = Square.check_files(game_state, get_row, enemy_color, f) 
			if f_t:
				threats.append(f_t)
				return threats
			
		

	@staticmethod
	def check_rows(game_state: 'GameState', get_file: int, enemy_color: str, rows: []):
		for r in rows:
			if game_state.board_state[r][get_file].piece == None:
				pass
			elif game_state.board_state[r][get_file].piece.piece_color != enemy_color:
				break
			elif game_state.board_state[r][get_file].piece.piece_type == 'R' or game_state.board_state[r][get_file].piece.piece_type == 'Q':
				return (r, get_file)
			else:
				break
	@staticmethod
	def check_files(game_state: 'GameState', get_row: int, enemy_color: str, files: []):
		for f in files:
			if game_state.board_state[get_row][f].piece == None:
				pass
			elif game_state.board_state[get_row][f].piece.piece_color != enemy_color:
				break
			elif game_state.board_state[get_row][f].piece.piece_type == 'R' or game_state.board_state[get_row][f].piece.piece_type == 'Q':
				return (get_row, f)
			else: 
				break
	@staticmethod
	def check_diagonals(game_state:'GameState', enemy_color: str, get_row: int, x_y: []):
		for xy in x_y:
			if game_state.board_state[xy[0]][xy[1]].piece == None:
				pass
			elif game_state.board_state[xy[0]][xy[1]].piece.piece_color != enemy_color:
				break
			elif game_state.board_state[xy[0]][xy[1]].piece.piece_type == 'B' or game_state.board_state[xy[0]][xy[1]].piece.piece_type == 'Q':
				return (xy[0], xy[1])
			elif game_state.board_state[xy[0]][xy[1]].piece.piece_type == 'P':
				if ((enemy_color == 'w' and get_row - xy[0] == -1) or (enemy_color == 'b' and get_row - xy[0] == 1)):
					return(xy[0], xy[1])
				else: 
					break
			else: 
				break

	@staticmethod
	def check_knight(game_state: 'GameState', enemy_color: str, x_y: ()):
		if game_state.board_state[x_y[0]][x_y[1]].piece == None:
			pass
		elif game_state.board_state[x_y[0]][x_y[1]].piece.piece_color != enemy_color:
			pass
		elif game_state.board_state[x_y[0]][x_y[1]].piece.piece_type == 'N':
			return (x_y[0], x_y[1])
		
	
	def __repr__(self):
		if self.piece != None:
			return f'({self.sqr_name} {self.color} {self.piece.piece_color,self.piece.piece_type})'
		else:
			return f'({self.sqr_name} {self.color} {None})'


if __name__ == '__main__':
	board = Board()
	#board = Board()
	gs = GameState(board)
	#gs.board_state[-2][4].piece.move_piece(gs, 'e4')
	print(board.board)
	print(gs.legal_moves)
	#print(board.board)
