import pygame as p
import chess_engine 

IMAGES = {}
HEIGHT = WIDTH = 512
DIMENSION = 8
SQ_SIZE = HEIGHT//DIMENSION
MAX_FPS = 15

def load_images():
	pieces = ['wP', 'wR', 'wN', 'wB', 'wQ', 'wK',
	 'bP', 'bR', 'bN', 'bB', 'bQ', 'bK']
	for piece in pieces:
		IMAGES[piece] = p.transform.scale(p.image.load("chess_pieces/" + piece + ".png"), (SQ_SIZE,SQ_SIZE))

def draw_Board(screen):
	for r in range(DIMENSION):
		for f in range(DIMENSION):
			dark_square = (f + r)%2 != 0
			if dark_square:
				p.draw.rect(screen, p.Color("LightSlateGrey"), p.Rect(f*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
			else:
				p.draw.rect(screen, p.Color("MintCream"), p.Rect(f*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def draw_Pieces(screen, board):
	for r in range(DIMENSION):
		for f in range(DIMENSION):
			piece = board[r][f].piece
			if piece:
				screen.blit(IMAGES[piece.piece_color+piece.piece_type], p.Rect(f*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))





def draw_GameState(screen, game_state):
	draw_Board(screen)
	draw_Pieces(screen, game_state.board_state)


if __name__ == '__main__':
	p.init()
	screen = p.display.set_mode((WIDTH, HEIGHT))
	clock = p.time.Clock()
	screen.fill(p.Color("coral"))
	#game_state = chess_engine.GameState(chess_engine.Board(chess_engine.Board.mk_custom_board(chess_engine.Piece.instantiate('K', 'w', 'h2'), chess_engine.Piece.instantiate('P', 'w', 'g2'),
	#	chess_engine.Piece.instantiate('P', 'w', 'f2'), chess_engine.Piece.instantiate('P', 'w', 'h3'), chess_engine.Piece.instantiate('P', 'w', 'a2'), chess_engine.Piece.instantiate('P', 'w', 'c4'),
	#	chess_engine.Piece.instantiate('Q', 'w', 'b5'), chess_engine.Piece.instantiate('R', 'w', 'd8'), chess_engine.Piece.instantiate('P', 'b', 'b7'), chess_engine.Piece.instantiate('P', 'b', 'f7'),
	#	chess_engine.Piece.instantiate('P', 'b', 'g7'), chess_engine.Piece.instantiate('P', 'b', 'h6'), chess_engine.Piece.instantiate('K', 'b', 'g8'), chess_engine.Piece.instantiate('Q', 'b', 'c2'),
	#	chess_engine.Piece.instantiate('R', 'b', 'e2'))), mv = 'b', wk_sqr = 'h2', bk_sqr = 'g8')
	
	game_state = chess_engine.GameState(chess_engine.Board())

	#game_state = chess_engine.GameState(chess_engine.Board(chess_engine.Board.mk_custom_board(chess_engine.Piece.instantiate('K', 'w', 'e1'), chess_engine.Piece.instantiate('K', 'b', 'e8'),
	#	chess_engine.Piece.instantiate('R', 'w', 'a1'), chess_engine.Piece.instantiate('B', 'w', 'c2'), chess_engine.Piece.instantiate('R', 'w', 'h1'))))
	load_images()
	running = True
	sq_selected = ()
	clicks = []
	while running:
		for e in p.event.get():
			if e.type == p.QUIT:			
				running = False
			elif e.type == p.MOUSEBUTTONDOWN:
				location = p.mouse.get_pos()
				file = location[0]//SQ_SIZE
				row = location[1]//SQ_SIZE

				if sq_selected == (row, file): 
					sq_selected = ()
					clicks = []
				else:
					sq_selected = (row, file)
					clicks.append(sq_selected)
					if len(clicks) == 1:
						if game_state.board_state[clicks[0][0]][clicks[0][1]].piece:
							moving_piece = game_state.board_state[clicks[0][0]][clicks[0][1]].piece.piece_type
							sqr = game_state.board_state[clicks[0][0]][clicks[0][1]].sqr_name
						else:
							sq_selected = ()
							clicks = []						
				if len(clicks) == 2:
					end_sqr = game_state.board_state[clicks[1][0]][clicks[1][1]].sqr_name
					if game_state.board_state[clicks[1][0]][clicks[1][1]].piece:
						if moving_piece == 'P':
							if end_sqr[1] == '8' or end_sqr[1] == '1':
								get_key = True
								while get_key:
									for event in p.event.get():
										if event.type == p.KEYDOWN:
											if event.key == p.K_q:
												promoted = 'Q'
											elif event.key == p.K_n:
												promoted = 'N'
											elif event.key == p.K_b:
												promoted = 'B'
											elif event.key == p.K_r:
												promoted = 'R'
											get_key = False
										elif event.type == p.MOUSEBUTTONDOWN:
											get_key = False
											promoted = False
								if promoted:
									move = sqr[0]+'x'+end_sqr[0]+end_sqr[1]+'='+promoted
									game_state.board_state[clicks[0][0]][clicks[0][1]].piece.move_piece(game_state, move)
							else:
								move = sqr[0]+'x'+end_sqr
								game_state.board_state[clicks[0][0]][clicks[0][1]].piece.move_piece(game_state, move)
						elif moving_piece != 'K':
							move = moving_piece+sqr+'x'+end_sqr
							game_state.board_state[clicks[0][0]][clicks[0][1]].piece.move_piece(game_state, move)
						else:
							move = 'K'+'x'+end_sqr
							game_state.board_state[clicks[0][0]][clicks[0][1]].piece.move_piece(game_state, move)

					else:
						if moving_piece == 'P':
							if end_sqr[1] == '8' or end_sqr[1] == '1':
								get_key = True
								while get_key:
									for event in p.event.get():
										if event.type == p.KEYDOWN:
											if event.key == p.K_q:
												promoted = 'Q'
											elif event.key == p.K_n:
												promoted = 'N'
											elif event.key == p.K_b:
												promoted = 'B'
											elif event.key == p.K_r:
												promoted = 'R'
											get_key = False
										elif event.type == p.MOUSEBUTTONDOWN:
											get_key = False
											promoted = False
								if promoted:
									move = sqr[0]+end_sqr[1]+'='+promoted
									game_state.board_state[clicks[0][0]][clicks[0][1]].piece.move_piece(game_state, move)
							elif end_sqr[0] != sqr[0]:
								move = sqr[0]+'x'+end_sqr[0]+'E'
								game_state.board_state[clicks[0][0]][clicks[0][1]].piece.move_piece(game_state, move)
							else:
								move = end_sqr
								game_state.board_state[clicks[0][0]][clicks[0][1]].piece.move_piece(game_state, move)
						elif moving_piece != 'K':
							move = moving_piece+sqr+end_sqr
							game_state.board_state[clicks[0][0]][clicks[0][1]].piece.move_piece(game_state, move)
						else:
							if sqr[0] == 'e' and end_sqr[0] == 'c':
								move = 'O-O-O'
								game_state.board_state[clicks[0][0]][clicks[0][1]].piece.move_piece(game_state, move)
							elif sqr[0] == 'e' and end_sqr[0] == 'g':
								move = 'O-O'
								game_state.board_state[clicks[0][0]][clicks[0][1]].piece.move_piece(game_state, move)
							else:
								move = 'K'+end_sqr
								game_state.board_state[clicks[0][0]][clicks[0][1]].piece.move_piece(game_state, move)
					sq_selected = ()
					clicks = []	
					print(move)
					print(game_state.w_king_sqr , game_state.b_king_sqr)
					print(game_state.color_to_move)
					print(game_state.legal_moves)
		draw_GameState(screen, game_state)	 
		clock.tick(MAX_FPS)
		p.display.flip()


















































