# debug_printing
# Chess 960
import random
from colorama import Fore, Back, Style
import os
from time import sleep
# Default to empty board

'''
TASKS (HIGH TO LOW PRIORITY):
- Finish CHECK and CHECKMATE
- LOGIC FOR CHECk:
 - Iterating through the board to check for each piece. If the piece can currently move to the king's position:
   - Then the king is in check
   - Otherwise, the king is not in check

- LOGIC FOR CHECKMATE
 - CHECK IF the opposing KING is currently in check
  - IF not, return False
  - IF yes, find each empty square or square occupied by opposite coloured piece to the king the king can move to
   - Iterate through each square the opposing king can move to
    - Use check() to find if any piece is checking each of the squares around the king
    - If a square next to the king is being checked, that means the king cannot move there
  - If every single available square that the king can move to, AND the king is currently in check, it is a checkmate

- LOGIC FOR CHECKING PIECES AROUND KING (CURRENTLY DOING)
 - Having a list with tuples of stuff around the king:
  - possible_squares = [(-1,-1),(0,-1),(1,-1),(-1,0)...] <- reflects this [topleft,topmiddle,topright...]
   - Using for loops, iterating through all of them
   - Then having a thing that adds it to compatible notation row and column  Eg. row += possible_squares[i][1] (changes the row according to the possible square cases)

- ALL Chess Features
  - EN PASSANT
  - CASTLING (CHECK pieces in between, move rook 2 squares and king 2 squares)
  - CHECKS (Has to make a move that stops the check, if none then it is checkmate (maybe surrendering instead of checkmate))
    - Determining the valid moves for each opponent's piece.
    - Checking if any of those valid moves land on the square occupied by the king.
- ADD turns (white move, black move) CORRECTLY [V]

(ALL OPTIONAL)
- Message when you are in check (by checking if the last move put you in check (discovered checks etc wouldn't fit))
- Possibly Checkmate
- Illegal move error messages
- INSTRUCTIONS, tutorial boards
- IMPROVE interface (icons, emojis, board outline?)
- IMPROVE quality (having better print messages, showing which piece you want to move when you get the square of it)
- ADD toggleable clocks for each side (maybe not)
- ADD settings (settings to toggle clocks, time for each side, highlight possible squares, background colour)
- POLISH and remove debug_print messages once done
'''

'''
COMPLETED:
- restrictions for all pieces (except king)
- movement system
- turn system
- proper moves for king
'''

'''
BUGS NEEDED TO FIX:
index errors
'''
EMPTY_SQUARE = '.'
colour_record = []

def cool_print(text = '', mode = 'Non-input'):
    for letter in text:
        print(letter, end="", flush=True) #makes sure it prints immediately after letter is made
        sleep(0.015) #how fast the text is printed (ideally a lower number (roughly 0.01 - 0.2))
    if mode == 'Input':
        return input()
    print()
    
def separator(text, mode = 'On'):
    '''Prints a separator after printing some text'''
    separator_text = ('-' * len(text)) if len(text) <= 50 else ('-' * 50)
    cool_print(Fore.YELLOW + separator_text + Style.RESET_ALL)
    if mode == 'On':
        cool_print(text)

def choose_theme():
    """Prompt the user for light/dark mode and return the correct symbol sets."""
    mode = ''
    while mode not in ('light','dark'):
        separator('None', 'Off')
        mode = cool_print('Are you using (light) mode or (dark) mode in GitHub right now?\n', 'Input').strip().lower()
    if mode == 'light':
        # “normal” mapping
        return (['♔','♕','♖','♗','♘','♙'],  # white actually rendered light
                ['♚','♛','♜','♝','♞','♟'])  # black actually rendered dark
    else:
        # dark mode: swap symbols so that the pieces that look white on dark bg
        # still function as White, and vice versa
        return (['♚','♛','♜','♝','♞','♟'],  # those that look white on dark bg
                ['♔','♕','♖','♗','♘','♙'])  # those that look black on dark bg

white_piece_symbols, black_piece_symbols = choose_theme()

white_pieces = white_piece_symbols[:]
black_pieces = black_piece_symbols[:]

def main():
    """Opens the menu and runs the main game loop."""
    separator('None', 'Off')
    cool_print(Fore.RED + 'Notes:\n The following Chess960 game is not' + Style.BRIGHT + ' complete, ' + Style.NORMAL + 'and may contain syntax, logical or runtime errors.' + Style.RESET_ALL)
    cool_print(Fore.RED + ' Castling, en passant, draws, check and checkmate are all' + Style.BRIGHT + ' not, ' + Style.NORMAL + 'fully done.' + Style.RESET_ALL)
    cool_print(Fore.RED + ' It is highly recommended that you adjust your' + Style.BRIGHT + ' terminal size, ' + Style.NORMAL + 'to improve the experience.' + Style.RESET_ALL)
    cool_print(Fore.RED + ' Some' + Style.BRIGHT + ' "testing messages" ' + Style.NORMAL + 'may still exist. You can ignore them.' + Style.RESET_ALL)
    player_names = ['', '']  # [White_name, Black_name]
    game_board   = [[' '] * 8 for _ in range(8)]
    
    menu_choice = menu()
    if menu_choice == '1':
        instructions()
        menu_choice = menu()
    if menu_choice == '2':
        player_names = setup_players()
        game_board   = setup_board()

    game_active         = True
    current_player_colour = 'White'
    while game_active:
        clear()
        game_board = start_turn(current_player_colour, player_names, game_board, 'No Print')
        current_player_colour = turn(current_player_colour)
        king_square           = find_king_pos(game_board, current_player_colour)
        debug_cool_print(f"{current_player_colour}'s king is in check? -> "
             f"{is_in_check(game_board, current_player_colour)}")
        debug_cool_print(f"{current_player_colour}'s king can move to "
             f"{check_squares_around_king(king_square, game_board, current_player_colour)}")
        clear()

def clear():
    """Clears the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def instructions():
    """Displays instructions; prompts which part to explain."""
    clear()
    selected_section = -1 #makes it out of range at first
    while selected_section not in range(1, 12):
        try:
            separator('None', 'Off')
            selected_section = int(cool_print(
                'Which part of the game would you like to know more? \n'
                '1. Pawn \n2. Rook \n3. King \n4. Knight \n5. Queen \n'
                '6. Bishop \n7. Legal Moves \n8. Castling \n9. Wins \n'
                '10. Losses \n11. Draws \n','Input'
            )) 
        except ValueError:
            cool_print(Fore.RED + "Please enter a number from 1 to 11 only." + Style.RESET_ALL)

    if selected_section == 1:
        cool_print("Pawns move forward one square, or two squares from their starting row. "
              "They capture diagonally.")
        cool_print("Press enter to return to the menu.", 'Input')
    else:
        cool_print('Instructions are not yet complete.')
def menu():
    """Shows the main menu and returns the user's choice ('1' or '2')."""
    choice = ''
    while choice not in ['1', '2']:
        try:
            separator('None', 'Off')
            choice = cool_print(
                'Welcome to Chess 960!\n'
                '1. Open instructions\n'
                '2. Start new game\n'
                'Enter what you want to do: ','Input'
            )
        except:
            separator('None','Off')
            cool_print(Fore.RED + "Invalid input. Please type 1 or 2." + Style.RESET_ALL)
            # cool_print(Fore.RED + "Invalid input. Please type 1 or 2." + Style.RESET_ALL)
    return choice

def setup_players():
    """Prompts both players for their names and returns [White_name, Black_name]."""
    separator('None', 'Off')
    cool_print("Let's play!")
    while True:
        try:
            separator('None', 'Off')
            white_name = cool_print('Player 1 (White), enter your name:\n','Input').strip()
            black_name = cool_print('Player 2 (Black), enter your name:\n','Input').strip()
            if white_name and black_name:
                return [white_name, black_name]
            else:
                separator('None', 'Off')
                cool_print(Fore.RED + "Both names are required." + Style.RESET_ALL)
        except:
            separator('None', 'Off')
            cool_print(Fore.RED + "Error with input. Try again." + Style.RESET_ALL)

def turn(current_colour):
    """Switches the turn between 'White' and 'Black'."""
    return 'White' if current_colour == 'Black' else 'Black'

def start_turn(player_colour, player_names, game_board, mode = 'Some'):
    """Tells the player it’s their turn, then returns the updated board."""
    if mode == 'No Print':
        return move(player_colour, player_names, game_board)
    if player_colour == 'White':
        separator('None', 'Off')
        cool_print(f"{player_names[0]}, it is your turn to move.")
    else:
        separator('None', 'Off')
        cool_print(f"{player_names[1]}, it is your turn to move.")
    # *** return the result of move() ***
    if mode == 'None':
        return None # For printing the names
    
    return move(player_colour, player_names, game_board) # Not needed all the time


def move(player_colour, player_names, game_board):
    """Handles input, validates and performs a move, and checks for checkmate."""
    move_successful = False
    colour_record.append(player_colour)
    # * * * legal moves * * *
    while not move_successful:
        try:
            if colour_record[-1] != player_colour: #This part may be buggy
                clear() #BUGGY ! MAY BE REMOVED
        except: # Don't clear if not new turn
            continue #BUGGY! MAY BE REMOVED
        start_turn(player_colour,player_names,game_board, 'None')
        display_board(game_board)

        # Safely read squares, breaking out when done
        while True:
            try:
                separator('None', 'Off')
                starting_square = cool_print(f"Enter starting square ({player_colour}): ",'Input').lower().strip()
                ending_square   = cool_print(f"Enter ending square   ({player_colour}): ",'Input').lower().strip()
                if len(starting_square)==2 and len(ending_square)==2:
                    break
                raise ValueError
            except ValueError:
                separator('None', 'Off')
                cool_print(Fore.RED + "Enter squares like 'e2', 'd4' only." + Style.RESET_ALL)

        moving_piece = get_piece_at(starting_square, game_board)
        target_piece = get_piece_at(ending_square,   game_board)
        debug_cool_print(f"{starting_square} -> {ending_square}: {moving_piece} to {target_piece}")

        # —— NEW GUARD: must pick your own piece ——  #opponent moves prevention (based on light or dark mode)
        own_set = white_piece_symbols if player_colour=='White' else black_piece_symbols #own set of pieces
        if moving_piece == EMPTY_SQUARE:
            separator('None', 'Off')
            cool_print(Fore.YELLOW + "You must select a piece to move!" + Style.RESET_ALL)
            continue
        if moving_piece not in own_set:
            separator('None', 'Off')
            cool_print(Fore.YELLOW + "You cannot move your opponent’s pieces!" + Style.RESET_ALL)
            continue
        # —— end new guard ——
        # Basic legality
        if not is_not_moving(starting_square, ending_square):
            separator('None', 'Off')
            cool_print(Back.BLUE + Fore.WHITE + "You must move to a different square!" + Style.RESET_ALL)
            continue
        if (player_colour=='White' and target_piece in white_piece_symbols) \
        or (player_colour=='Black' and target_piece in black_piece_symbols):
            separator('None', 'Off')
            cool_print(Fore.YELLOW + f"{moving_piece} cannot capture its own color!" + Style.RESET_ALL)
            continue
        
        # Shape validation
        if moving_piece in ['♟','♙']:
            if not validate_pawn_move(starting_square, ending_square, game_board, player_colour):
                separator('None', 'Off')
                cool_print(Fore.YELLOW + "Illegal pawn move!" + Style.RESET_ALL)
                continue
        elif moving_piece in ['♞','♘']:
            if not validate_knight_move(starting_square, ending_square, game_board, player_colour):
                separator('None', 'Off')
                cool_print(Fore.YELLOW + "Illegal knight move!" + Style.RESET_ALL)
                continue
        elif moving_piece in ['♜','♖']:
            if not validate_rook_move(starting_square, ending_square, game_board, player_colour):
                separator('None', 'Off')
                cool_print(Fore.YELLOW + "Illegal rook move!" + Style.RESET_ALL)
                continue
        elif moving_piece in ['♝','♗']:
            if not validate_bishop_move(starting_square, ending_square, game_board, player_colour):
                separator('None', 'Off')
                cool_print(Fore.YELLOW + "Illegal bishop move!" + Style.RESET_ALL)
                continue
        elif moving_piece in ['♛','♕']:
            if not validate_queen_move(starting_square, ending_square, game_board, player_colour):
                separator('None', 'Off')
                cool_print(Fore.YELLOW + "Illegal queen move!" + Style.RESET_ALL)
                continue
        elif moving_piece in ['♚','♔']:
            if not validate_king_move(starting_square, ending_square, game_board, player_colour):
                separator('None', 'Off')
                cool_print(Fore.YELLOW + "Illegal king move!" + Style.RESET_ALL)
                continue
                
        # Simulate and check self-check
        simulated_board = [row[:] for row in game_board]
        simulated_board = set_piece_at(ending_square, moving_piece, simulated_board)
        simulated_board = set_piece_at(starting_square,  EMPTY_SQUARE,         simulated_board)
        if is_in_check(simulated_board, player_colour):
            separator('None', 'Off')
            cool_print(Fore.RED + "Move puts your king in check!" + Style.RESET_ALL)
            continue

        # Perform the move
        game_board = update_board(starting_square, ending_square, game_board)
        move_successful = True

        # Check for checkmate
        if is_in_check(game_board, player_colour) and checkmate(game_board, player_colour):
            separator('None', 'Off')
            cool_print(Fore.RED + Style.BRIGHT + f"{player_colour} has been checkmated!" + Style.RESET_ALL)
            end_game(player_colour)

    return game_board

def update_board(from_square, to_square, game_board):
    """Moves a piece from from_square to to_square and returns the board."""
    moving_piece = get_piece_at(from_square, game_board)
    game_board   = set_piece_at(to_square,   moving_piece, game_board)
    game_board   = set_piece_at(from_square, EMPTY_SQUARE,         game_board)
    return game_board

def check_squares_around_king(king_square, game_board, player_colour):
    """
    Returns a list of legal squares the king can move to (no check, no friendly).
    """
    legal_squares    = []
    king_col_index, king_row_index = notation_to_indices(king_square)
    friendly_set     = white_piece_symbols if player_colour=='White' else black_piece_symbols

    for delta_col, delta_row in [(-1,-1),(0,-1),(1,-1), #delta means change (change incolumn and row)
                                 (-1, 0),       (1,  0), #iterating through 2 things at the same time
                                 (-1, 1),(0, 1),(1,  1)]:
        new_col = king_col_index + delta_col
        new_row = king_row_index + delta_row
        if not (0 <= new_col < 8 and 0 <= new_row < 8):
            continue

        adjacent_square = indices_to_notation(new_col, new_row)
        if get_piece_at(adjacent_square, game_board) in friendly_set:
            continue

        # simulate king move
        simulated_board = [row[:] for row in game_board]
        simulated_board = set_piece_at(adjacent_square,
                                      get_piece_at(king_square, game_board),
                                      simulated_board)
        simulated_board = set_piece_at(king_square, EMPTY_SQUARE, simulated_board)
        if not is_in_check(simulated_board, player_colour):
            legal_squares.append(adjacent_square)

    return legal_squares

def checkmate(game_board, player_colour):
    """Returns True if player_colour’s king has no legal escape and is in check."""
    if not is_in_check(game_board, player_colour):
        return False

    king_square = find_king_pos(game_board, player_colour)
    for escape_square in check_squares_around_king(king_square, game_board, player_colour):
        simulated_board = [row[:] for row in game_board]
        simulated_board = set_piece_at(escape_square,
                                      get_piece_at(king_square, game_board),
                                      simulated_board)
        simulated_board = set_piece_at(king_square, EMPTY_SQUARE, simulated_board)
        if not is_in_check(simulated_board, player_colour):
            return False

    return True

def find_king_pos(game_board, player_colour):
    """Finds and returns the algebraic square of player_colour’s king."""
    king_piece = '♚' if player_colour=='White' else '♔'
    for row_index, row_list in enumerate(game_board):
        for col_index, piece in enumerate(row_list):
            if piece == king_piece:
                return indices_to_notation(col_index, row_index)
    return None
def update_board(from_square, to_square, game_board):
    """
    Moves the piece from from_square to to_square on game_board,
    then clears the original square. Returns the updated board.
    """
    moving_piece = get_piece_at(from_square, game_board)
    game_board   = set_piece_at(to_square, moving_piece, game_board)
    game_board   = set_piece_at(from_square, EMPTY_SQUARE, game_board)
    return game_board


def get_legal_king_escape_squares(king_square_notation, game_board, player_colour):
    """
    Returns a list of all squares the king on king_square_notation
    can legally move to (not occupied by friendlies and not into check).
    """
    legal_squares = []
    king_file_index, king_rank_index = notation_to_indices(king_square_notation)
    friendly_symbols = (
        white_piece_symbols if player_colour == 'White'
        else black_piece_symbols
    )

    # All eight directions around the king
    for file_offset, rank_offset in [
        (-1, -1), (0, -1), (1, -1),
        (-1,  0),         (1,  0),
        (-1,  1), (0,  1), (1,  1),
    ]:
        new_file = king_file_index + file_offset
        new_rank = king_rank_index + rank_offset

        # Skip off-board
        if not (0 <= new_file < 8 and 0 <= new_rank < 8):
            continue

        adjacent_square = indices_to_notation(new_file, new_rank)
        # Can't land on friendly piece
        if get_piece_at(adjacent_square, game_board) in friendly_symbols:
            continue
        #debug_cool_print(f'Check3: {game_board}')
        # Simulate king move and check for attack
        simulated_board = [row[:] for row in game_board]
        simulated_board = set_piece_at(
            adjacent_square,
            get_piece_at(king_square_notation, game_board),
            simulated_board
        ) # The board is a fake, so it doesn't change the actual board
        simulated_board = set_piece_at(king_square_notation, EMPTY_SQUARE, simulated_board)
        #debug_cool_print(f'Check2: {simulated_board}')
        if not is_in_check(simulated_board, player_colour):
            legal_squares.append(adjacent_square)

    return legal_squares


def is_in_check(game_board, player_colour, override_square='empty'):
    """
    Returns True if player_colour's king (or override_square) is under attack.
    """
    #debug_cool_print(f'Check: {game_board}')
    defending_king_square = find_king_pos(game_board, player_colour)
    target_square = (
        defending_king_square
        if override_square == 'empty'
        else override_square
    )
    opponent_symbols = (
        white_piece_symbols if player_colour == 'Black'
        else black_piece_symbols
    )
    opponent_colour = 'Black' if player_colour == 'White' else 'White'

    # Scan all squares for opposing pieces
    for row_index in range(8):
        for column_index in range(8):
            #debug_cool_print(game_board)
            piece = game_board[row_index][column_index]
            if piece not in opponent_symbols:
                continue

            attacker_square = indices_to_notation(column_index, row_index)
            validator = {
                '♝': validate_bishop_move, '♗': validate_bishop_move,
                '♜': validate_rook_move,   '♖': validate_rook_move,
                '♛': validate_queen_move,  '♕': validate_queen_move,
                '♞': validate_knight_move, '♘': validate_knight_move,
                '♟': validate_pawn_move,   '♙': validate_pawn_move,
                '♚': validate_king_move,   '♔': validate_king_move,
            }[piece] #gets the right subroutine depending on the piece

            if validator(attacker_square, target_square, game_board, opponent_colour):
                return True

    return False


def is_checkmate(game_board, player_colour):
    """
    Returns True if player_colour's king is in check and has no legal escapes.
    """
    if not is_in_check(game_board, player_colour):
        return False

    king_square_notation = find_king_pos(game_board, player_colour)
    for escape_square in get_legal_king_escape_squares(
        king_square_notation, game_board, player_colour
    ):
        simulated_board = [row[:] for row in game_board]
        simulated_board = set_piece_at(
            escape_square,
            get_piece_at(king_square_notation, game_board),
            simulated_board
        )
        simulated_board = set_piece_at(king_square_notation, EMPTY_SQUARE, simulated_board)

        if not is_in_check(simulated_board, player_colour):
            return False

    return True


def find_king_position(game_board, player_colour):
    """
    Returns the king’s square in algebraic notation (e.g. "e1")
    for the given player_colour on game_board.
    """
    king_symbol = '♚' if player_colour == 'White' else '♔'
    for row_index, row in enumerate(game_board):
        for col_index, piece in enumerate(row):
            if piece == king_symbol:
                return indices_to_notation(col_index, row_index)
    return None


def get_piece_at(square_notation, game_board, lookup_mode='default'):
    """
    Returns the piece at square_notation on game_board,
    or EMPTY_SQUARE if the notation is out of bounds.
    """
    try:
        col_index, row_index = notation_to_indices(square_notation)
        return game_board[row_index][col_index]
    except:
        return EMPTY_SQUARE


def set_piece_at(square_notation, piece_symbol, game_board):
    """
    Places piece_symbol on square_notation in game_board
    and returns the updated board.
    """
    try:
        col_index, row_index = notation_to_indices(square_notation)
        game_board[row_index][col_index] = piece_symbol
        return game_board
    except:
        separator('None', 'Off')
        cool_print(Fore.RED + f"Could not edit piece at square {square_notation}" + Style.RESET_ALL)
        return game_board


def end_game(losing_player_colour):
    """
    Announces the winner (opposite of losing_player_colour)
    and exits the program.
    """
    winner = 'White' if losing_player_colour == 'Black' else 'Black'
    cool_print(
        Fore.GREEN
        + Style.BRIGHT
        + f"Game over! {winner} wins by checkmate!"
        + Style.RESET_ALL
    )
    exit()


def debug_cool_print(message):
    """Prints a debug message in magenta."""
    cool_print(Fore.MAGENTA + f"{message}\n" + Style.RESET_ALL)


def is_not_moving(start_square, end_square):
    """
    Returns False if the player attempted to move to the same square.
    """
    return start_square != end_square


def is_moving_opponents_piece(start_square, game_board, player_colour):
    """
    Returns True if the piece at start_square belongs to the opponent.
    """
    piece_symbol = get_piece_at(start_square, game_board)
    if player_colour == 'White' and piece_symbol in black_piece_symbols:
        return True
    if player_colour == 'Black' and piece_symbol in white_piece_symbols:
        return True
    return False


def validate_king_move(start_square, end_square, game_board, player_colour):
    """
    Returns True if the king moves exactly one square in any direction
    and does not move into check.
    """
    start_file_ord = ord(start_square[0])
    start_rank_int = int(start_square[1])
    end_file_ord   = ord(end_square[0])
    end_rank_int   = int(end_square[1])

    # Must move exactly one square
    if max(abs(end_file_ord - start_file_ord),
           abs(end_rank_int - start_rank_int)) != 1:
        return False

    # Simulate the move to ensure the king is not placed in check
    simulated_board = [row[:] for row in game_board]
    simulated_board = set_piece_at(
        end_square,
        get_piece_at(start_square, game_board),
        simulated_board
    )
    simulated_board = set_piece_at(start_square, EMPTY_SQUARE, simulated_board)
    return not is_in_check(simulated_board, player_colour)


def validate_queen_move(start_square, end_square, game_board, player_colour):
    """
    Returns True if the queen’s move is legal
    (either rook-like or bishop-like).
    """
    return (
        validate_rook_move(start_square, end_square, game_board, player_colour)
        or validate_bishop_move(start_square, end_square, game_board, player_colour)
    )


def validate_pawn_move(start_square, end_square, game_board, player_colour):
    """
    Returns True if the pawn move from start_square to end_square
    is legal under standard pawn rules.
    """
    start_file = start_square[0]
    start_rank = int(start_square[1])
    end_file   = end_square[0]
    end_rank   = int(end_square[1])

    forward_step =  1 if player_colour == 'White' else -1
    home_rank    =  2 if player_colour == 'White' else 7
    enemy_set    = (
        black_piece_symbols if player_colour == 'White'
        else white_piece_symbols
    )

    # Straight move
    if start_file == end_file:
        # must land on empty
        if get_piece_at(end_square, game_board) != EMPTY_SQUARE:
            return False
        # one square forward
        if end_rank - start_rank == forward_step:
            return True
        # two squares from home rank, intermediate empty
        if start_rank == home_rank and end_rank - start_rank == 2 * forward_step:
            intermediate = start_file + str(start_rank + forward_step)
            return get_piece_at(intermediate, game_board) == EMPTY_SQUARE
        return False

    # Diagonal capture
    if (
        abs(ord(end_file) - ord(start_file)) == 1
        and end_rank - start_rank == forward_step
    ):
        return get_piece_at(end_square, game_board) in enemy_set

    return False


def validate_knight_move(start_square, end_square, game_board, player_colour):
    """
    Returns True if the knight’s L-shaped move is legal.
    """
    start_file_ord = ord(start_square[0])
    start_rank_int = int(start_square[1])
    end_file_ord   = ord(end_square[0])
    end_rank_int   = int(end_square[1])

    file_diff = abs(end_file_ord - start_file_ord)
    rank_diff = abs(end_rank_int - start_rank_int)
    return sorted([file_diff, rank_diff]) == [1, 2]


def validate_rook_move(start_square, end_square, game_board, player_colour):
    """
    Returns True if the rook’s move is legal (straight line, no blockers).
    """
    start_file, start_rank = start_square
    end_file,   end_rank   = end_square

    if start_file == end_file:
        pieces_between, _ = pieces_in_between(
            start_square, end_square, 'vertical', game_board
        )
    elif start_rank == end_rank:
        pieces_between, _ = pieces_in_between(
            start_square, end_square, 'horizontal', game_board
        )
    else:
        return False

    return all(p == EMPTY_SQUARE for p in pieces_between)


def validate_bishop_move(start_square, end_square, game_board, player_colour):
    """
    Returns True if the bishop’s move is legal
    (diagonal line, no blockers).
    """
    sc, sr = notation_to_indices(start_square)
    ec, er = notation_to_indices(end_square)
    # must lie on a diagonal
    if abs(ec - sc) != abs(er - sr):
        return False

    pieces_between, _ = pieces_in_between(
        start_square, end_square, 'diagonal', game_board
    )
    return all(p == EMPTY_SQUARE for p in pieces_between)


def filter_squares_in_board(candidate_squares):
    """
    From a list of algebraic squares, returns only those
    that lie within a valid 8×8 board.
    """
    valid_squares = []
    for square in candidate_squares:
        file, rank = square[0], square[1]
        if file in 'abcdefgh' and rank in '12345678':
            valid_squares.append(square)
    return valid_squares


def pieces_in_between(start_square, end_square, mode, game_board):
    """
    Returns ([pieces_between], direction) for moves in 'horizontal',
    'vertical', or 'diagonal' mode—otherwise ([], None).
    """
    sc, sr = notation_to_indices(start_square)
    ec, er = notation_to_indices(end_square)
    blockers = []
    direction = None

    # horizontal
    if mode == 'horizontal' and sr == er:
        step = 1 if ec > sc else -1
        direction = 'right' if step == 1 else 'left'
        for col in range(sc + step, ec, step):
            sq = indices_to_notation(col, sr)
            blockers.append(get_piece_at(sq, game_board))
        return [blockers, direction]

    # vertical
    if mode == 'vertical' and sc == ec:
        step = 1 if er > sr else -1
        direction = 'down' if step == 1 else 'up'
        for row in range(sr + step, er, step):
            sq = indices_to_notation(sc, row)
            blockers.append(get_piece_at(sq, game_board))
        return [blockers, direction]

    # diagonal
    if mode == 'diagonal' and abs(ec - sc) == abs(er - sr):
        dc = 1 if ec > sc else -1
        dr = 1 if er > sr else -1
        if   (dc, dr) == ( 1, -1): direction = 'upright'
        elif (dc, dr) == (-1, -1): direction = 'upleft'
        elif (dc, dr) == ( 1,  1): direction = 'bottomright'
        else:                       direction = 'bottomleft'

        col, row = sc + dc, sr + dr
        while (col, row) != (ec, er):
            sq = indices_to_notation(col, row)
            blockers.append(get_piece_at(sq, game_board))
            col += dc; row += dr
        return [blockers, direction]

    return [[], None]

def enforce_move_within_limit(blocking_pieces, movement_direction, starting_square, ending_square, player_colour):
    """
    Checks if the intended move from starting_square to ending_square
    goes beyond the furthest reachable square along movement_direction.
    """
    step = 1 if movement_direction in ['right', 'up'] else -1
    furthest_offset = 0
    start_col, start_row = notation_to_index(starting_square)

    for blocker in blocking_pieces:
        if blocker == EMPTY_SQUARE:
            furthest_offset += step
        elif blocker in white_piece_symbols:
            if player_colour == 'White':
                break
            furthest_offset += step
        else:  # blocker in black_piece_symbols
            if player_colour == 'Black':
                break
            furthest_offset += step

    # Determine limit square and compare
    if movement_direction in ['up', 'down']:
        limit_square = indices_to_notation(start_col, start_row + furthest_offset)
        end_rank = int(ending_square[1])
        limit_rank = int(limit_square[1])
        if end_rank > limit_rank:
            return False
    else:
        limit_square = indices_to_notation(start_col + furthest_offset, start_row)
        end_file_ord  = ord(ending_square[0])
        limit_file_ord = ord(limit_square[0])
        if end_file_ord > limit_file_ord:
            return False

    return True


def notation_to_index(square_notation):
    """
    Converts algebraic notation (e.g. 'a4') into 0-based (column_index, row_index).
    """
    if isinstance(square_notation, list):
        square_notation = f"{square_notation[0]}{square_notation[1]}"
    notation = str(square_notation)
    if len(notation) != 2:
        separator('None', 'Off')
        raise ValueError(f"Invalid square: {notation}")
    file_char, rank_char = notation[0], notation[1]
    column_index = ord(file_char) - ord('a')
    row_index    = 8 - int(rank_char)
    return column_index, row_index


def indices_to_notation(column_index, row_index):
    """
    Converts 0-based (column_index, row_index) into algebraic notation like 'a1'.
    """
    if not (0 <= column_index < 8 and 0 <= row_index < 8):
        separator('None', 'Off')
        raise ValueError(f"Invalid board indices: {(column_index, row_index)}")
    file_char = chr(column_index + ord('a'))  # 0 -> 'a'
    rank_char = str(8 - row_index)            # 0 -> '8'
    return file_char + rank_char


def display_board(game_board):
    """Nicely prints out the current state of the board."""
    current_rank = 8
    for rank in game_board:
        print(f"{current_rank} {' '.join(rank)}")
        current_rank -= 1

    files_line = " ".join(chr(ord('A') + i) for i in range(len(game_board[0])))
    print(f"  {files_line}")


def empty_board():
    """Creates and returns an empty 8×8 board."""
    return [[EMPTY_SQUARE ] * 8 for _ in range(8)]
    


def randomize_chess960_board(board):
    """
    Places shuffled Chess960 major pieces on rank 8 and 1,
    pawns on rank 7 and 2.
    """
    white_backrank = ['♔', '♕', '♖', '♖', '♗', '♗', '♘', '♘']
    black_backrank = ['♚', '♛', '♜', '♜', '♝', '♝', '♞', '♞']

    random.shuffle(white_backrank)
    random.shuffle(black_backrank)

    board[0]  = white_backrank
    board[-1] = black_backrank
    board[1]  = ['♙'] * 8
    board[-2] = ['♟'] * 8

    return board


def setup_board():
    """Creates, displays, and returns a randomized Chess960 board."""
    board = randomize_chess960_board(empty_board())
    display_board(board)
    return board

def notation_to_indices(square):
    '''Turns chess format (like a4) into indexable format [column,row]'''
    if type(square) == list:
        square = str(square[0]) + str(square[1])
    square = str(square)

    if len(square) != 2:
        separator('None', 'Off')
        raise ValueError(f"Invalid square: {square}")

    column = ord(square[0]) - ord('a')
    row = 8 - int(square[1])
    return [column, row]




main()