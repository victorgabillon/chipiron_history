#! /usr/bin/env python

"""
This module is the execution point of the chess GUI application.

It provides the `MainWindow` class, which creates a surface for the chessboard and handles user interactions.
"""

import queue
import typing

import chess
from PySide6.QtCore import QTimer, Slot
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QPushButton, QTableWidget, QWidget, QDialog, QTableWidgetItem

from chipiron.environments.chess.board import BoardChi
from chipiron.environments.chess.board.factory import create_board_chi
from chipiron.environments.chess.move.imove import moveKey
from chipiron.games.game.game_playing_status import PlayingStatus
from chipiron.games.match.match_results import MatchResults
from chipiron.games.match.match_results import SimpleResults
from chipiron.utils.communication.gui_messages import GameStatusMessage, BackMessage, EvaluationMessage
from chipiron.utils.communication.gui_messages.gui_messages import MatchResultsMessage
from chipiron.utils.communication.gui_player_message import PlayersColorToPlayerMessage
from chipiron.utils.communication.player_game_messages import BoardMessage, MoveMessage
from chipiron.utils.dataclass import IsDataclass


class MainWindow(QWidget):
    """
    Create a surface for the chessboard and handle user interactions.

    This class provides the main window for the chess GUI application. It handles user interactions such as
    clicking on chess pieces, making moves, and controlling the game status.

    Attributes:
        playing_status (PlayingStatus): The current playing status of the game.
        gui_mailbox (queue.Queue[IsDataclass]): The mailbox for receiving messages from the GUI thread.
        main_thread_mailbox (queue.Queue[IsDataclass]): The mailbox for sending messages to the main thread.
    """

    def __init__(
            self,
            gui_mailbox: queue.Queue[IsDataclass],
            main_thread_mailbox: queue.Queue[IsDataclass]
    ) -> None:
        """
        Initialize the chessboard and the main window.

        Args:
            gui_mailbox (queue.Queue[IsDataclass]): The mailbox for receiving messages from the GUI thread.
            main_thread_mailbox (queue.Queue[IsDataclass]): The mailbox for sending messages to the main thread.
        """
        super().__init__()

        self.playing_status = PlayingStatus.PLAY

        self.gui_mailbox = gui_mailbox
        self.main_thread_mailbox = main_thread_mailbox

        self.setWindowTitle("Chess GUI")
        self.setGeometry(300, 300, 1400, 800)

        self.widgetSvg = QSvgWidget(parent=self)
        self.widgetSvg.setGeometry(10, 10, 600, 600)

        self.closeButton = QPushButton(self)
        self.closeButton.setText("Close")  # text
        self.closeButton.setIcon(QIcon("close.png"))  # icon
        self.closeButton.setShortcut('Ctrl+D')  # shortcut key
        self.closeButton.clicked.connect(self.stopppy)
        self.closeButton.setToolTip("Close the widget")  # Tool tip
        self.closeButton.move(700, 0)

        # self.play_button = QPushButton(self)
        # self.play_button.setText("Play")  # text
        # self.play_button.setIcon(QIcon("data/gui/play.png"))  # icon
        # self.play_button.clicked.connect(self.play_button_clicked)
        # self.play_button.setToolTip("play the game")  # Tool tip
        # self.play_button.move(700, 100)

        self.pause_button = QPushButton(self)
        self.pause_button.setText("Pause")  # text
        self.pause_button.setIcon(QIcon("data/gui/pause.png"))  # icon
        self.pause_button.clicked.connect(self.pause_button_clicked)
        self.pause_button.setToolTip("pause the game")  # Tool tip
        self.pause_button.move(850, 100)

        self.back_button = QPushButton(self)
        self.back_button.setText("Back")  # text
        self.back_button.setIcon(QIcon("data/gui/back.png"))  # icon
        self.back_button.clicked.connect(self.back_button_clicked)
        self.back_button.setToolTip("back one move")  # Tool tip
        self.back_button.move(1000, 100)

        self.player_white_button = QPushButton(self)
        self.player_white_button.setText("Player")  # text
        self.player_white_button.setIcon(QIcon("data/gui/white_king.png"))  # icon
        self.player_white_button.setStyleSheet('QPushButton {background-color: white; color: black;}')
        self.player_white_button.setGeometry(620, 250, 470, 30)

        self.player_black_button = QPushButton(self)
        self.player_black_button.setText("Player")  # text
        self.player_black_button.setIcon(QIcon("data/gui/black_king.png"))  # icon
        self.player_black_button.setStyleSheet('QPushButton {background-color: black; color: white;}')
        self.player_black_button.setGeometry(620, 300, 470, 30)

        self.tablewidget = QTableWidget(1, 2, self)
        self.tablewidget.setGeometry(1100, 250, 260, 330)

        self.score_button = QPushButton(self)
        self.score_button.setText("Score 0-0")  # text
        self.score_button.setStyleSheet('QPushButton {background-color: white; color: black;}')
        self.score_button.setGeometry(620, 400, 370, 30)

        self.round_button = QPushButton(self)
        self.round_button.setText("Round")  # text
        self.round_button.setStyleSheet('QPushButton {background-color: white; color: black;}')
        self.round_button.setGeometry(620, 500, 370, 30)

        self.fen_button = QPushButton(self)
        self.fen_button.setText("fen")  # text
        self.fen_button.setStyleSheet('QPushButton { background-color: white; color: black;}')
        self.fen_button.setGeometry(50, 700, 1250, 30)

        self.eval_button = QPushButton(self)
        self.eval_button.setText("Stock Eval")  # text
        self.eval_button.setStyleSheet('QPushButton {background-color: white; color: black;}')
        self.eval_button.setGeometry(620, 600, 470, 30)

        self.eval_button_chi = QPushButton(self)
        self.eval_button_chi.setText("Chi Eval")  # text
        self.eval_button_chi.setStyleSheet('QPushButton {background-color: white; color: black;}')
        self.eval_button_chi.setGeometry(620, 650, 470, 30)

        self.eval_button_white = QPushButton(self)
        self.eval_button_white.setText("White Eval")  # text
        self.eval_button_white.setStyleSheet('QPushButton {background-color: white; color: black;}')
        self.eval_button_white.setGeometry(620, 700, 470, 30)

        self.eval_button_black = QPushButton(self)
        self.eval_button_black.setText("Black Eval")  # text
        self.eval_button_black.setStyleSheet('QPushButton {background-color: white; color: black;}')
        self.eval_button_black.setGeometry(620, 750, 470, 30)

        self.board_size = min(self.widgetSvg.width(),
                              self.widgetSvg.height())
        self.coordinates = True
        self.margin = 0.05 * self.board_size if self.coordinates else 0
        self.squareSize = (self.board_size - 2 * self.margin) / 8.0
        self.pieceToMove = [None, None]

        self.checkThreadTimer = QTimer(self)
        self.checkThreadTimer.setInterval(5)  # .5 seconds
        self.checkThreadTimer.timeout.connect(self.process_message)
        self.checkThreadTimer.start()

    def stopppy(self) -> None:
        """
        Stops the execution of the GUI.

        This method closes the GUI window and sends a kill message to the main thread.

        Returns:
            None
        """
        # should we send a kill message to the main thread?
        self.close()

    def play_button_clicked(self) -> None:
        """
        Handle the event when the play button is clicked.

        This method prints a message indicating that the play button has been clicked,
        and sends a GameStatusMessage with the status set to PlayingStatus.PLAY to the main thread mailbox.
        """
        print('play_button_clicked')
        message: GameStatusMessage = GameStatusMessage(status=PlayingStatus.PLAY)
        self.main_thread_mailbox.put(message)

    def back_button_clicked(self) -> None:
        """
        Handle the event when the back button is clicked.

        This method prints a message and puts a `BackMessage` object into the main thread mailbox.
        """
        print('back_button_clicked')
        message: BackMessage = BackMessage()
        self.main_thread_mailbox.put(message)

    def pause_button_clicked(
            self
    ) -> None:
        """
        Handles the click event of the pause button.

        Prints 'pause_button_clicked' and sends a GameStatusMessage with the status set to PlayingStatus.PAUSE
        to the main thread mailbox.
        """
        print('pause_button_clicked')
        message: GameStatusMessage = GameStatusMessage(status=PlayingStatus.PAUSE)
        self.main_thread_mailbox.put(message)

    @typing.no_type_check
    @Slot(QWidget)
    def mousePressEvent(self, event):
        """
        Handle left mouse clicks and enable moving chess pieces by
        clicking on a chess piece and then the target square.

        Moves must be made according to the rules of chess because
        illegal moves are suppressed.
        """
        if event.x() <= self.board_size and event.y() <= self.board_size:
            if event.buttons() == Qt.LeftButton:
                if self.margin < event.x() < self.board_size - self.margin \
                        and self.margin < event.y() < self.board_size - self.margin:

                    file = int((event.x() - self.margin) / self.squareSize)
                    rank = 7 - int((event.y() - self.margin) / self.squareSize)
                    square = chess.square(file, rank)
                    piece = self.board.piece_at(square)
                    self.coordinates = f'{chr(file + 97)}{rank + 1}'
                    if self.pieceToMove[0] is not None:
                        try:
                            move = chess.Move.from_uci("{}{}".format(self.pieceToMove[1], self.coordinates))
                            move_promote = chess.Move.from_uci("{}{}q".format(self.pieceToMove[1], self.coordinates))
                            if move in self.board.legal_moves:
                                self.send_move_to_main_thread(move)
                            elif move_promote in self.board.legal_moves:
                                self.choice_promote()
                                self.send_move_to_main_thread(self.move_promote_asked)
                            else:
                                print(f'Looks like a wrong move. {move} {self.board.legal_moves}')
                        except ValueError:
                            print("Oops!  Doubleclicked?  Try again...")
                        piece = None
                    self.pieceToMove = [piece, self.coordinates]

    def send_move_to_main_thread(
            self,
            move_key: moveKey
    ) -> None:
        """
        Sends a move to the main thread for processing.

        Args:
            move (chess.Move): The move to be sent.

        Returns:
            None
        """
        message: MoveMessage = MoveMessage(
            move=move_key,
            corresponding_board=self.board.fen,
            player_name='Gui_Human',
            color_to_play=self.board.turn
        )
        self.main_thread_mailbox.put(item=message)

    @typing.no_type_check
    def choice_promote(self):
        """
        Displays a dialog box with buttons for promoting a chess piece.

        The dialog box allows the user to choose between promoting the pawn to a queen, rook, bishop, or knight.
        Each button is connected to a corresponding method for handling the promotion.

        Returns:
            None
        """

        self.d = QDialog()
        d = self.d
        d.setWindowTitle("Promote to ?")
        d.setWindowModality(Qt.ApplicationModal)

        d.closeButtonQ = QPushButton(d)
        d.closeButtonQ.setText("Queen")  # text
        d.closeButtonQ.setStyleSheet('QPushButton {background-color: white; color: blue;}')
        d.closeButtonQ.setGeometry(150, 100, 150, 20)
        d.closeButtonQ.clicked.connect(self.promote_queen)

        d.closeButtonR = QPushButton(d)
        d.closeButtonR.setText("Rook")  # text
        d.closeButtonR.setStyleSheet('QPushButton {background-color: white; color: blue;}')
        d.closeButtonR.setGeometry(150, 200, 150, 20)
        d.closeButtonR.clicked.connect(self.promote_rook)

        d.closeButtonB = QPushButton(d)
        d.closeButtonB.setText("Bishop")  # text
        d.closeButtonB.setStyleSheet('QPushButton {background-color: white; color: blue;}')
        d.closeButtonB.setGeometry(150, 300, 150, 20)
        d.closeButtonB.clicked.connect(self.promote_bishop)

        d.closeButtonK = QPushButton(d)
        d.closeButtonK.setText("Knight")  # text
        d.closeButtonK.setStyleSheet('QPushButton {background-color: white; color: blue;}')
        d.closeButtonK.setGeometry(150, 400, 150, 20)
        d.closeButtonK.clicked.connect(self.promote_knight)

        d.exec_()

    @typing.no_type_check
    def promote_queen(self):
        """
        Promotes the selected piece to a queen.

        This method creates a move object to promote the selected piece to a queen by appending 'q' to the UCI notation
        of the piece's destination square. It then closes the dialog window.

        Returns:
            None
        """
        self.move_promote_asked = chess.Move.from_uci("{}{}q".format(self.pieceToMove[1], self.coordinates))
        self.d.close()

    @typing.no_type_check
    def promote_rook(self):
        """
        Promotes a pawn to a rook.

        This method is called when a pawn reaches the opposite end of the board and needs to be promoted to a rook.
        It creates a move object representing the promotion and closes the dialog window.

        Returns:
            None
        """
        self.move_promote_asked = chess.Move.from_uci("{}{}r".format(self.pieceToMove[1], self.coordinates))
        self.d.close()

    @typing.no_type_check
    def promote_bishop(self):
        """
        Promotes the current piece to a bishop.

        This method creates a move object to promote the current piece to a bishop and closes the dialog window.

        Returns:
            None
        """
        self.move_promote_asked = chess.Move.from_uci("{}{}b".format(self.pieceToMove[1], self.coordinates))
        self.d.close()

    @typing.no_type_check
    def promote_knight(self):
        """
        Promotes a pawn to a knight.

        This method is called when a pawn is promoted to a knight in the GUI.
        It creates a move object representing the promotion and closes the GUI.

        Returns:
        None
        """
        self.move_promote_asked = chess.Move.from_uci("{}{}n".format(self.pieceToMove[1], self.coordinates))
        self.d.close()

    def process_message(
            self
    ) -> None:

        """
        Process a message received by the GUI.

        Draw a chessboard with the starting position and then redraw
        it for every new move.

        This method is responsible for handling different types of messages
        received by the GUI and taking appropriate actions based on the message type.

        Supported message types:
        - BoardMessage: Updates the board and redraws it.
        - EvaluationMessage: Updates the evaluation values.
        - PlayersColorToPlayerMessage: Updates the mapping of player colors to player information.
        - MatchResultsMessage: Updates the match results.
        - GameStatusMessage: Updates the game play status.
        - Other: Raises a ValueError indicating an unknown message type.

        Returns:
        None
        """
        if not self.gui_mailbox.empty():
            message = self.gui_mailbox.get()
            match message:
                case BoardMessage():
                    print('receiving board')
                    board_message: BoardMessage = message
                    self.board: BoardChi = create_board_chi(fen_with_history=board_message.fen_plus_moves)
                    self.draw_board()
                    self.display_move_history()
                case EvaluationMessage():
                    evaluation_message: EvaluationMessage = message
                    evaluation_stock = evaluation_message.evaluation_stock
                    evaluation_chipiron = evaluation_message.evaluation_chipiron
                    evaluation_black = evaluation_message.evaluation_player_black
                    evaluation_white = evaluation_message.evaluation_player_white
                    self.update_evaluation(
                        evaluation_stock=evaluation_stock,
                        evaluation_chipiron=evaluation_chipiron,
                        evaluation_white=evaluation_white,
                        evaluation_black=evaluation_black
                    )
                case PlayersColorToPlayerMessage():
                    player_color_message: PlayersColorToPlayerMessage = message
                    players_color_to_player: dict[chess.Color, str] = player_color_message.player_color_to_gui_info
                    self.update_players_color_to_id(players_color_to_player)
                case MatchResultsMessage():
                    match_message: MatchResultsMessage = message
                    match_results: MatchResults = match_message.match_results
                    self.update_match_stats(match_results)
                case GameStatusMessage():
                    print('GameStatusMessage', message)
                    game_status_message: GameStatusMessage = message
                    play_status: PlayingStatus = game_status_message.status
                    self.update_game_play_status(play_status)
                case other:
                    raise ValueError(f'unknown type of message received by gui {other} in {__name__}')

    def display_move_history(self) -> None:
        """
        Display the move history in a table widget.

        This method calculates the number of rounds based on the number of half moves in the move stack.
        It then sets the number of rows in the table widget to the number of rounds.
        The table widget's horizontal header labels are set to 'White' and 'Black'.
        The move history is then iterated over and each move is added to the table widget.

        Returns:
            None
        """
        import math
        num_half_move: int = len(self.board.chess_board.move_stack)
        num_rounds: int = int(math.ceil(num_half_move / 2))
        self.tablewidget.setRowCount(num_rounds)
        self.tablewidget.setHorizontalHeaderLabels(['White', 'Black'])
        for player in range(2):
            for round_ in range(num_rounds):
                half_move = round_ * 2 + player
                if half_move < num_half_move:
                    item = QTableWidgetItem(str(self.board.chess_board.move_stack[half_move]))
                    self.tablewidget.setItem(round_, player, item)

    def draw_board(self) -> None:
        """
        Draw a chessboard with the starting position and then redraw
        it for every new move.

        Returns:
            None
        """
        print('tupe', type(self.board), type(self.board.chess_board.move_stack), self.board.chess_board.move_stack)
        self.boardSvg = self.board.chess_board._repr_svg_().encode("UTF-8")
        self.drawBoardSvg = self.widgetSvg.load(self.boardSvg)
        self.round_button.setText('Round: ' + str(self.board.chess_board.fullmove_number))  # text
        self.fen_button.setText('fen: ' + str(self.board.fen))  # text
        return self.drawBoardSvg

    def update_players_color_to_id(
            self,
            players_color_to_player: dict[chess.Color, str]
    ) -> None:
        """
        Update the player buttons with the corresponding player names.

        Args:
            players_color_to_player (dict[chess.Color, str]): A dictionary mapping chess.Color to player names.

        Returns:
            None
        """
        self.player_white_button.setText(' White: ' + players_color_to_player[chess.WHITE])  # text
        self.player_black_button.setText(' Black: ' + players_color_to_player[chess.BLACK])  # text

    def update_evaluation(
            self,
            evaluation_stock: float,
            evaluation_chipiron: float,
            evaluation_white: float,
            evaluation_black: float
    ) -> None:
        """
        Update the evaluation values displayed on the GUI.

        Args:
            evaluation_stock (float): The evaluation value for the stock.
            evaluation_chipiron (float): The evaluation value for the chipiron.
            evaluation_white (float): The evaluation value for the white.
            evaluation_black (float): The evaluation value for the black.

        Returns:
            None
        """
        self.eval_button.setText('eval: ' + str(evaluation_stock))  # text
        self.eval_button_chi.setText('eval: ' + str(evaluation_chipiron))  # text
        self.eval_button_black.setText('eval White: ' + str(evaluation_white))  # text
        self.eval_button_white.setText('eval Black: ' + str(evaluation_black))  # text

    def update_game_play_status(
            self,
            play_status: PlayingStatus
    ) -> None:
        """Update the game play status.

        Args:
            play_status (PlayingStatus): The new playing status.
        """
        print('update_game_play_status', play_status)

        if self.playing_status != play_status:
            self.playing_status = play_status
            print('real update_game_play_status', play_status)
            if play_status == PlayingStatus.PAUSE:
                self.pause_button.setText("Play")  # text
                self.pause_button.setIcon(QIcon("data/gui/play.png"))  # icon
                self.pause_button.clicked.connect(self.play_button_clicked)
                self.pause_button.setToolTip("play the game")  # Tool tip
                self.pause_button.move(850, 100)
            elif play_status == PlayingStatus.PLAY:
                self.pause_button.setText("Pause")  # text
                self.pause_button.setIcon(QIcon("data/gui/pause.png"))  # icon
                self.pause_button.clicked.connect(self.pause_button_clicked)
                self.pause_button.setToolTip("pause the game")  # Tool tip
                self.pause_button.move(850, 100)

    def update_match_stats(
            self,
            match_result: MatchResults
    ) -> None:
        """
        Update the match statistics and display them on the GUI.

        Args:
            match_result (MatchResults): The result of the match.

        Returns:
            None
        """
        simple_results: SimpleResults = match_result.get_simple_result()
        self.score_button.setText(
            'Score: ' + str(simple_results.player_one_wins) + '-'
            + str(simple_results.player_two_wins) + '-'
            + str(simple_results.draws))  # text

        print('update', match_result.match_finished)
        # if the match is over we kill the GUI
        if match_result.match_finished:
            print('finishing the widget')
            self.close()
