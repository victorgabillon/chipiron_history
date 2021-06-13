import chess
import torch


def transform_board_pieces_one_side(board, requires_grad_):
    # normalisation of the board so that it is white turn (possible color inversion if it was black's turn)

    if board.chess_board.turn == chess.BLACK:
        color_turn = board.chess_board.turn
        color_not_turn = chess.WHITE
    else:
        color_turn = chess.WHITE
        color_not_turn = chess.BLACK

    transform = torch.zeros(5)

    # print('ol', board.chessBoard)
    transform[0] = bin(board.chess_board.pawns & board.chess_board.occupied_co[color_turn]).count('1') \
                   - bin(board.chess_board.pawns & board.chess_board.occupied_co[color_not_turn]).count('1')
    transform[1] = bin(board.chess_board.knights & board.chess_board.occupied_co[color_turn]).count('1') \
                   - bin(board.chess_board.knights & board.chess_board.occupied_co[color_not_turn]).count('1')
    transform[2] = bin(board.chess_board.bishops & board.chess_board.occupied_co[color_turn]).count('1') \
                   - bin(board.chess_board.bishops & board.chess_board.occupied_co[color_not_turn]).count('1')
    transform[3] = bin(board.chess_board.rooks & board.chess_board.occupied_co[color_turn]).count('1') \
                   - bin(board.chess_board.rooks & board.chess_board.occupied_co[color_not_turn]).count('1')
    transform[4] = bin(board.chess_board.queens & board.chess_board.occupied_co[color_turn]).count('1') \
                   - bin(board.chess_board.queens & board.chess_board.occupied_co[color_not_turn]).count('1')

    if requires_grad_:
        transform.requires_grad_(True)

    return transform


def transform_board_pieces_two_sides(board, requires_grad_):
    # normalisation of the board so that it is white turn (possible color inversion if it was black's turn)

    if board.chess_board.turn == chess.BLACK:
        color_turn = board.chess_board.turn
        color_not_turn = chess.WHITE
    else:
        color_turn = chess.WHITE
        color_not_turn = chess.BLACK

    transform = torch.zeros(10, requires_grad=requires_grad_)

    # print('ol', board.chessBoard)
    transform[0] = bin(board.chess_board.pawns & board.chess_board.occupied_co[color_turn]).count('1')
    transform[1] = bin(board.chess_board.knights & board.chess_board.occupied_co[color_turn]).count('1')
    transform[2] = bin(board.chess_board.bishops & board.chess_board.occupied_co[color_turn]).count('1')
    transform[3] = bin(board.chess_board.rooks & board.chess_board.occupied_co[color_turn]).count('1')
    transform[4] = bin(board.chess_board.queens & board.chess_board.occupied_co[color_turn]).count('1')
    transform[5] = -bin(board.chess_board.pawns & board.chess_board.occupied_co[color_not_turn]).count('1')
    transform[6] = -bin(board.chess_board.knights & board.chess_board.occupied_co[color_not_turn]).count('1')
    transform[7] = -bin(board.chess_board.bishops & board.chess_board.occupied_co[color_not_turn]).count('1')
    transform[8] = -bin(board.chess_board.rooks & board.chess_board.occupied_co[color_not_turn]).count('1')
    transform[9] = -bin(board.chess_board.queens & board.chess_board.occupied_co[color_not_turn]).count('1')
    return transform


def node_to_tensors_pieces_square(node, requires_grad_):
    board = node.board

    tensor_white, tensor_black, tensor_castling_white, tensor_castling_black \
        = board_to_tensors_pieces_square(board, requires_grad_)

    node.tensor_white = tensor_white
    node.tensor_black = tensor_black
    node.tensor_castling_white = tensor_castling_white
    node.tensor_castling_black = tensor_castling_black


def board_to_tensor_pieces_square(board, requires_grad_):
    tensor_white, tensor_black, tensor_castling_white, tensor_castling_black \
        = board_to_tensors_pieces_square(board, requires_grad_)
    side_to_move = board.chess_board.turn
    tensor = get_tensor_from_tensors(tensor_white, tensor_black, tensor_castling_white, tensor_castling_black,
                                     side_to_move)
    return tensor


def board_to_tensor_pieces_square_two_sides(board, requires_grad_):
    tensor_white, tensor_black, tensor_castling_white, tensor_castling_black \
        = board_to_tensors_pieces_square(board, requires_grad_)
    side_to_move = board.chess_board.turn
    tensor = get_tensor_from_tensors_two_sides(tensor_white, tensor_black, tensor_castling_white, tensor_castling_black,
                                               side_to_move)
    return tensor


def get_tensor_from_tensors_two_sides(tensor_white, tensor_black, tensor_castling_white, tensor_castling_black,
                                      color_to_play):
    if color_to_play == chess.WHITE:
        tensor = torch.cat((tensor_white, tensor_black), 0)
    else:
        tensor = torch.cat((tensor_black, tensor_white), 0)

    if color_to_play == chess.WHITE:
        tensor_castling = torch.cat((tensor_castling_white, tensor_castling_black), 0)
    else:
        tensor_castling = torch.cat((tensor_castling_black, tensor_castling_white), 0)

    tensor_2 = torch.cat((tensor, tensor_castling), 0)
    return tensor_2


def get_tensor_from_tensors(tensor_white, tensor_black, tensor_castling_white, tensor_castling_black, color_to_play):
    if color_to_play == chess.WHITE:
        tensor = tensor_white - tensor_black
    else:
        tensor = tensor_black - tensor_white

    if color_to_play == chess.WHITE:
        tensor_castling = tensor_castling_white - tensor_castling_black
    else:
        tensor_castling = tensor_castling_black - tensor_castling_white

    tensor_2 = torch.cat((tensor, tensor_castling), 0)
    return tensor_2


def board_to_tensors_pieces_square(board, requires_grad_):
    tensor_white = torch.zeros(384, requires_grad=requires_grad_)
    tensor_black = torch.zeros(384, requires_grad=requires_grad_)
    tensor_castling_white = torch.zeros(2, requires_grad=requires_grad_)
    tensor_castling_black = torch.zeros(2, requires_grad=requires_grad_)

    for square in range(64):
        piece = board.chess_board.piece_at(square)
        if piece:
            piece_code = piece.piece_type - 1
            if piece.color == chess.BLACK:
                square_index = chess.square_mirror(square)
                index = 64 * piece_code + square_index
                tensor_black[index] += 1
            else:
                square_index = square
                index = 64 * piece_code + square_index
                tensor_white[index] += 1

    tensor_castling_white[0] = board.chess_board.has_queenside_castling_rights(chess.WHITE)
    tensor_castling_white[1] = board.chess_board.has_kingside_castling_rights(chess.WHITE)
    tensor_castling_black[0] = board.chess_board.has_queenside_castling_rights(chess.BLACK)
    tensor_castling_black[1] = board.chess_board.has_kingside_castling_rights(chess.BLACK)

    return tensor_white, tensor_black, tensor_castling_white, tensor_castling_black


def node_to_tensors_pieces_square_fast(node, parent_node, board_modifications, requires_grad_):
    """  this version is supposed to be faster as it only modifies the parent
    representation with the last move and does not scan fully the new board"""
    if parent_node is None:  # this is the root_node
        node_to_tensors_pieces_square(node, requires_grad_)
    else:
        tensor_white = parent_node.tensor_white.detach().clone()
        tensor_black = parent_node.tensor_black.detach().clone()
        node_to_tensors_pieces_square_from_parent(node, board_modifications, tensor_white, tensor_black)


def node_to_tensors_pieces_square_from_parent(node, board_modifications, tensor_white, tensor_black):
    for removal in board_modifications.removals:
        piece_type = removal[1]
        piece_color = removal[2]
        square = removal[0]
        piece_code = piece_type - 1
        if piece_color == chess.BLACK:
            square_index = chess.square_mirror(square)
            index = 64 * piece_code + square_index
            tensor_black[index] = 0
        else:
            square_index = square
            index = 64 * piece_code + square_index
            tensor_white[index] = 0

    for appearance in board_modifications.appearances:
        # print('app',appearance)
        piece_type = appearance[1]
        piece_color = appearance[2]
        square = appearance[0]
        piece_code = piece_type - 1
        if piece_color == chess.BLACK:
            square_index = chess.square_mirror(square)
            index = 64 * piece_code + square_index
            tensor_black[index] = 1
        else:
            square_index = square
            index = 64 * piece_code + square_index
            tensor_white[index] = 1

    node.tensor_white = tensor_white
    node.tensor_black = tensor_black

    board = node.board
    node.tensor_castling_white = torch.zeros(2, requires_grad=False)
    node.tensor_castling_black = torch.zeros(2, requires_grad=False)
    node.tensor_castling_white[0] = board.chess_board.has_queenside_castling_rights(chess.WHITE)
    node.tensor_castling_white[1] = board.chess_board.has_kingside_castling_rights(chess.WHITE)
    node.tensor_castling_black[0] = board.chess_board.has_queenside_castling_rights(chess.BLACK)
    node.tensor_castling_black[1] = board.chess_board.has_kingside_castling_rights(chess.BLACK)


def transform_board_pieces_square_old(node, requires_grad_):
    # print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    board = node.board
    # normalisation of the board so that it is white turn (possible color inversion if it was black's turn)
    inversion = 1
    if board.chess_board.turn == chess.BLACK:
        inversion = -1

    transform = torch.zeros(384, requires_grad=requires_grad_)

    for square in range(64):
        piece_type = board.chess_board.piece_type_at(square)
        piece_color = board.chess_board.color_at(square)
        if piece_type is not None:
            # print('p', square, piece.color, type(piece.piece_type))
            piece_code = (piece_type - 1)
            # print('dp', 64 * piece_code + square, 2 * piece.color - 1)
            if piece_color == chess.BLACK:
                square_index = chess.square_mirror(square)
            else:
                square_index = square
            index = 64 * piece_code + square_index
            transform[index] += (2 * piece_color - 1) * inversion

        # transform[64 * piece_code + square] = 2 * piece.color - 1
    return transform


def transform_board_pieces_square_old2(node, requires_grad_):
    # print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
    board = node.board
    # normalisation of the board so that it is white turn (possible color inversion if it was black's turn)
    inversion = 1
    if board.chess_board.turn == chess.BLACK:
        inversion = -1

    transform = torch.zeros(384, requires_grad=requires_grad_)

    for square in range(64):
        piece = board.chess_board.piece_at(square)
        if piece:
            # print('p', square, piece.color, type(piece.piece_type))
            piece_code = (piece.piece_type - 1)
            # print('dp', 64 * piece_code + square, 2 * piece.color - 1)
            if piece.color == chess.BLACK:
                square_index = chess.square_mirror(square)
            else:
                square_index = square
            index = 64 * piece_code + square_index
            transform[index] += (2 * piece.color - 1) * inversion

        # transform[64 * piece_code + square] = 2 * piece.color - 1
    return transform
