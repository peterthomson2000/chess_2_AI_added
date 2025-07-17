from typing import Dict, List, Optional, Tuple

RESET = "\033[0m"

# Base square colors
BG_LIGHT = "\033[48;5;230m"   # tan
BG_DARK = "\033[48;5;22m"     # forest green

# Highlighting
HIGHLIGHT_LIGHT = "\033[48;5;229m"  # yellow
HIGHLIGHT_DARK = "\033[48;5;120m"   # light green
SELECTED_BG = "\033[48;5;220m"      # gold

# Purple for promotion, castling, and en passant
PROMO_LIGHT = "\033[48;5;183m"
PROMO_DARK = "\033[48;5;91m"

COLS = "abcdefgh"

def setup_board() -> Dict[str, str]:
    board = {}
    for col in COLS:
        board[col + "2"] = "wp"
        board[col + "7"] = "bp"
    board.update({
        'a1': 'wr', 'b1': 'wn', 'c1': 'wb', 'd1': 'wq', 'e1': 'wk', 'f1': 'wb', 'g1': 'wn', 'h1': 'wr',
        'a8': 'br', 'b8': 'bn', 'c8': 'bb', 'd8': 'bq', 'e8': 'bk', 'f8': 'bb', 'g8': 'bn', 'h8': 'br',
    })
    return board

def inside_board(c: str, r: int) -> bool:
    return 'a' <= c <= 'h' and 1 <= r <= 8

def is_path_clear(board: Dict[str, str], squares: List[str]) -> bool:
    return all(sq not in board for sq in squares)

def get_king_square(board: Dict[str, str], color: str) -> Optional[str]:
    for square, piece in board.items():
        if piece == color + 'k':
            return square
    return None

def is_square_attacked(board: Dict[str, str], square: str, attacker_color: str) -> bool:
    for sq, piece in board.items():
        if piece[0] != attacker_color:
            continue
        if square in generate_legal_moves(board, sq, ignore_castling=True, ignore_check=True):
            return True
    return False

def is_in_check(board: Dict[str, str], color: str) -> bool:
    king_sq = get_king_square(board, color)
    if not king_sq:
        return False
    return is_square_attacked(board, king_sq, 'b' if color == 'w' else 'w')

def is_checkmate(board: Dict[str, str], color: str) -> bool:
    for square, piece in board.items():
        if piece[0] != color:
            continue
        legal = generate_legal_moves(board, square)
        if legal:
            return False
    return is_in_check(board, color)

def generate_legal_moves(board: Dict[str, str], square: str,
                         ignore_castling: bool = False,
                         ignore_check: bool = False,
                         last_move: Optional[Tuple[str, str]] = None) -> List[str]:
    piece = board.get(square)
    if not piece:
        return []

    color, ptype = piece[0], piece[1]
    row = int(square[1])
    col = square[0]
    directions = []
    moves = []
    enemy = 'b' if color == 'w' else 'w'

    if ptype == 'p':
        step = 1 if color == 'w' else -1
        fwd = col + str(row + step)
        # Move forward 1 square if empty
        if inside_board(col, row + step) and fwd not in board:
            moves.append(fwd)
            # Move forward 2 squares from starting position
            if (color == 'w' and row == 2) or (color == 'b' and row == 7):
                fwd2 = col + str(row + 2 * step)
                if fwd2 not in board and fwd not in board:
                    moves.append(fwd2)

        # Captures
        for dcol in [-1, 1]:
            nc = chr(ord(col) + dcol)
            target = nc + str(row + step)
            if inside_board(nc, row + step):
                # Normal capture (diagonal onto enemy piece)
                if target in board and board[target][0] == enemy:
                    moves.append(target)

                # En passant capture:
                if last_move:
                    start_sq, end_sq = last_move
                    if end_sq in board:
                        last_piece = board[end_sq]
                        if last_piece[0] == enemy and last_piece[1] == 'p':
                            start_row = int(start_sq[1])
                            end_row = int(end_sq[1])
                            # Must be a two-square pawn move adjacent horizontally
                            if abs(start_row - end_row) == 2 and end_row == row:
                                if ord(end_sq[0]) == ord(col) + dcol:
                                    en_passant_sq = end_sq[0] + str(row + step)
                                    if en_passant_sq not in board:
                                        moves.append(en_passant_sq)

    elif ptype == 'r':
        directions = [(1,0), (-1,0), (0,1), (0,-1)]
    elif ptype == 'b':
        directions = [(1,1), (1,-1), (-1,1), (-1,-1)]
    elif ptype == 'q':
        directions = [(1,0), (-1,0), (0,1), (0,-1), (1,1), (1,-1), (-1,1), (-1,-1)]
    elif ptype == 'k':
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == dy == 0: continue
                nc = chr(ord(col) + dx)
                nr = row + dy
                target = nc + str(nr)
                if inside_board(nc, nr):
                    if target not in board or board[target][0] != color:
                        moves.append(target)
        if not ignore_castling and board.get(square) == color + 'k':
            if color == 'w' and square == 'e1':
                if 'h1' in board and board['h1'] == 'wr' and is_path_clear(board, ['f1', 'g1']):
                    if not any(is_square_attacked(board, sq, 'b') for sq in ['e1', 'f1', 'g1']):
                        moves.append('g1')
                if 'a1' in board and board['a1'] == 'wr' and is_path_clear(board, ['b1', 'c1', 'd1']):
                    if not any(is_square_attacked(board, sq, 'b') for sq in ['e1', 'd1', 'c1']):
                        moves.append('c1')
            elif color == 'b' and square == 'e8':
                if 'h8' in board and board['h8'] == 'br' and is_path_clear(board, ['f8', 'g8']):
                    if not any(is_square_attacked(board, sq, 'w') for sq in ['e8', 'f8', 'g8']):
                        moves.append('g8')
                if 'a8' in board and board['a8'] == 'br' and is_path_clear(board, ['b8', 'c8', 'd8']):
                    if not any(is_square_attacked(board, sq, 'w') for sq in ['e8', 'd8', 'c8']):
                        moves.append('c8')

    elif ptype == 'n':
        for dx, dy in [(2,1),(1,2),(-1,2),(-2,1),(-2,-1),(-1,-2),(1,-2),(2,-1)]:
            nc = chr(ord(col) + dx)
            nr = row + dy
            target = nc + str(nr)
            if inside_board(nc, nr):
                if target not in board or board[target][0] != color:
                    moves.append(target)

    for dc, dr in directions:
        step = 1
        while True:
            nc = chr(ord(col) + dc * step)
            nr = row + dr * step
            target = nc + str(nr)
            if not inside_board(nc, nr):
                break
            if target in board:
                if board[target][0] != color:
                    moves.append(target)
                break
            moves.append(target)
            step += 1

    # Filter moves that leave king in check unless ignoring check
    if not ignore_check:
        legal = []
        for move in moves:
            temp = board.copy()
            # Handle en passant capture on temporary board
            if ptype == 'p' and last_move:
                start_sq, end_sq = last_move
                # If move is en passant capture square:
                if move not in board and abs(ord(move[0]) - ord(col)) == 1 and move[1] != square[1]:
                    # Remove captured pawn from temp board
                    temp.pop(end_sq, None)

            temp[move] = temp[square]
            del temp[square]
            if not is_in_check(temp, color):
                legal.append(move)
        return legal
    return moves

def can_promote(piece: str, square: str) -> bool:
    if piece not in ('wp', 'bp'):
        return False
    rank = int(square[1])
    return (piece == 'wp' and rank == 8) or (piece == 'bp' and rank == 1)

def promote_pawn(board: Dict[str, str], square: str, new_piece_type: str) -> None:
    color = board[square][0]
    board[square] = color + new_piece_type

def move_piece(board: Dict[str, str], start: str, end: str, last_move: Optional[Tuple[str, str]] = None) -> bool:
    piece = board.get(start)
    if not piece:
        return False

    legal = generate_legal_moves(board, start, last_move=last_move)
    if end not in legal:
        return False

    # Castling rook move
    if piece[1] == 'k' and abs(ord(end[0]) - ord(start[0])) == 2:
        if end[0] == 'g':
            rook_start, rook_end = 'h' + start[1], 'f' + start[1]
        else:
            rook_start, rook_end = 'a' + start[1], 'd' + start[1]
        board[rook_end] = board[rook_start]
        del board[rook_start]

    # En passant capture removal (only when capturing on empty square diagonally)
    if piece[1] == 'p' and last_move:
        start_sq, end_sq = last_move
        if abs(ord(end[0]) - ord(start[0])) == 1 and end[1] != start[1] and end not in board:
            ep_capture_sq = end[0] + start[1]
            if ep_capture_sq in board and board[ep_capture_sq][1] == 'p' and board[ep_capture_sq][0] != piece[0]:
                del board[ep_capture_sq]

    board[end] = piece
    del board[start]
    return True

def print_board(board: Dict[str, str], legal_moves: Optional[List[str]] = None,
                promotion_squares: Optional[List[str]] = None,
                castling_squares: Optional[List[str]] = None,
                en_passant_squares: Optional[List[str]] = None,
                selected_square: Optional[str] = None) -> None:

    col_indices = {c: i for i, c in enumerate(COLS)}
    print()
    print("       " + "         ".join(COLS))
    print("  ⌜" + "─────────┬" * 7 + "─────────⌝")

    purple_squares = set(promotion_squares or []) | set(castling_squares or []) | set(en_passant_squares or [])

    for r in reversed("12345678"):
        for line in ["top", "mid", "bot"]:
            print(f"{r if line == 'top' else ' '} │", end="")

            for c in COLS:
                sq = c + r
                idx_sum = col_indices[c] + int(r)
                base_bg = BG_LIGHT if idx_sum % 2 == 0 else BG_DARK
                highlight_bg = HIGHLIGHT_LIGHT if idx_sum % 2 == 0 else HIGHLIGHT_DARK
                promo_bg = PROMO_LIGHT if idx_sum % 2 == 0 else PROMO_DARK

                bg = base_bg
                if sq in purple_squares:
                    bg = promo_bg
                elif legal_moves and sq in legal_moves:
                    bg = highlight_bg
                if selected_square == sq:
                    bg = SELECTED_BG

                piece = board.get(sq, "")
                content = piece.center(5) if piece else "     "

                if line == "top" or line == "bot":
                    print(bg + "         " + RESET, end="│")
                else:
                    print(bg + f"  {content}  " + RESET, end="│")

            if line == "mid":
                print(f" {r}")
            else:
                print()
        if r != "1":
            print("  ├" + "─────────┼" * 7 + "─────────┤")
    print("  ⌞" + "─────────┴" * 7 + "─────────⌟")
