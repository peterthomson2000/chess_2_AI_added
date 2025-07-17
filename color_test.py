import time
import sys
import threading
from color_board import (
    setup_board, print_board, generate_legal_moves,
    move_piece, is_in_check, is_checkmate,
    can_promote, promote_pawn
)
import random

def evaluate_board(board):
    values = {'p': 1, 'n': 3, 'b': 3, 'r': 5, 'q': 9, 'k': 0}
    score = 0
    for piece in board.values():
        val = values.get(piece[1], 0)
        score += val if piece[0] == 'w' else -val
    return score

def choose_ai_move(board, color, last_move):
    candidates = []
    for sq, piece in board.items():
        if piece[0] != color:
            continue
        moves = generate_legal_moves(board, sq, last_move=last_move)
        for move in moves:
            temp = board.copy()
            move_piece(temp, sq, move, last_move=last_move)
            score = evaluate_board(temp)
            candidates.append((score, sq, move))

    if not candidates:
        return None, None

    if color == 'b':
        best = min(candidates, key=lambda x: x[0])
    else:
        best = max(candidates, key=lambda x: x[0])

    return best[1], best[2]

def ai_thinking_animation(duration: float):
    thinking_messages = ["Thinking.", "Thinking..", "Thinking..."]
    start_time = time.time()
    i = 0
    while time.time() - start_time < duration:
        print(thinking_messages[i % 3], end="\r")
        time.sleep(0.5)
        i += 1
    print(" " * 20, end="\r")  # Clear line

def main():
    board = setup_board()
    current_turn = 'w'
    last_move = (None, None)

    ai_mode = ""
    while ai_mode not in ["1", "2"]:
        ai_mode = input("Choose mode:\n1. Player vs Player\n2. Player vs AI (1700 Sicilian Specialist)\n> ").strip()

    ai_color = 'b' if ai_mode == "2" else None

    while True:
        print_board(board)

        if is_in_check(board, current_turn):
            if is_checkmate(board, current_turn):
                print(f"\nCheckmate! {'Black' if current_turn == 'w' else 'White'} wins!")
                break
            print(f"\n{'White' if current_turn == 'w' else 'Black'} is in check!")

        print(f"\n{'White' if current_turn == 'w' else 'Black'} to move.")

        if ai_color == current_turn:
            is_check = is_in_check(board, current_turn)
            thinking_time = 1.0 if is_check else 3.0
            ai_done = threading.Event()

            def ai_thread_fn():
                ai_thinking_animation(thinking_time)
                nonlocal start_sq, end_sq
                start_sq, end_sq = choose_ai_move(board, current_turn, last_move)
                ai_done.set()

            start_sq, end_sq = None, None
            thread = threading.Thread(target=ai_thread_fn)
            thread.start()

            while not ai_done.is_set():
                time.sleep(0.1)

            if not start_sq or not end_sq:
                print("AI resigns. You win!")
                break
            print(f"AI plays {start_sq} to {end_sq}")
        else:
            selected_square = input("Select piece (e.g., e2) or 'quit': ").strip().lower()
            if selected_square == "quit":
                break

            if selected_square not in board or board[selected_square][0] != current_turn:
                print("Invalid selection or no piece of your color there.")
                continue

            legal_moves = generate_legal_moves(board, selected_square, last_move=last_move)
            if not legal_moves:
                print("No legal moves for that piece. Select another.")
                continue

            promotion_squares = [sq for sq in legal_moves if can_promote(board[selected_square], sq)]
            castling_squares = [sq for sq in legal_moves if board[selected_square][1] == 'k' and abs(ord(sq[0]) - ord(selected_square[0])) == 2]
            en_passant_squares = []
            for sq in legal_moves:
                if sq not in board and board[selected_square][1] == 'p' and abs(ord(sq[0]) - ord(selected_square[0])) == 1:
                    en_passant_squares.append(sq)

            print_board(
                board,
                legal_moves=legal_moves,
                promotion_squares=promotion_squares,
                castling_squares=castling_squares,
                en_passant_squares=en_passant_squares,
                selected_square=selected_square,
            )
            print(f"\n{'White' if current_turn == 'w' else 'Black'} to move.")
            dest_square = input(f"Enter move target for {selected_square} or 'cancel': ").strip().lower()
            if dest_square == "cancel":
                continue

            if dest_square not in legal_moves:
                print("Illegal move.")
                continue

            start_sq, end_sq = selected_square, dest_square

        moved = move_piece(board, start_sq, end_sq, last_move=last_move)
        if not moved:
            print("Move failed.")
            continue

        last_move = (start_sq, end_sq)

        if can_promote(board.get(end_sq, ""), end_sq):
            if ai_color == current_turn:
                promote_pawn(board, end_sq, 'q')  # AI always promotes to queen
            else:
                while True:
                    choice = input("Promote to (q, r, b, n): ").strip().lower()
                    if choice in ('q', 'r', 'b', 'n'):
                        promote_pawn(board, end_sq, choice)
                        break
                    print("Invalid choice.")

        current_turn = 'b' if current_turn == 'w' else 'w'

if __name__ == "__main__":
    main()
