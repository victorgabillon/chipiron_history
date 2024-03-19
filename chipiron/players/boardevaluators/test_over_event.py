import unittest

from chipiron.players.boardevaluators.over_event import OverEvent, Winner


class TestOverEvent(unittest.TestCase):

    def test_construct_over_events(self):

        def test_construct_over_event(test_over_event: OverEvent):
            if test_over_event.is_over():
                self.assertTrue(test_over_event.is_win() or test_over_event.is_draw())
            if test_over_event.is_win():
                self.assertTrue(not test_over_event.is_draw())
                self.assertTrue(test_over_event.who_is_winner is not None)
                self.assertTrue(test_over_event.who_is_winner is Winner.WHITE
                                or test_over_event.who_is_winner is Winner.BLACK)
            if test_over_event.is_draw():
                self.assertTrue(not test_over_event.is_win())
                self.assertTrue(test_over_event.who_is_winner is None)

        test_over_event_: OverEvent = OverEvent()
        test_construct_over_event(test_over_event_)

        # todo make more tests !
        test_over_event_ = OverEvent()
        test_construct_over_event(test_over_event_)
