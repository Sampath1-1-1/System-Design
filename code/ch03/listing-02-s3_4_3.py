# Extracted from manuscript/book1-traditional/03-learning-method.md §3.4.3 (listing 2). Edit the manuscript, not this file.
"""Minimal Leitner-box scheduler for system-design flashcards."""
from dataclasses import dataclass, field
from datetime import date, timedelta

INTERVALS = [1, 3, 7, 16, 35]  # days until next review, per box (box 0..4)


@dataclass
class Card:
    prompt: str
    box: int = 0
    due: date = field(default_factory=date.today)

    def review(self, recalled: bool, today: date) -> None:
        # Success promotes one box; failure sends the card back to box 0.
        self.box = min(self.box + 1, len(INTERVALS) - 1) if recalled else 0
        self.due = today + timedelta(days=INTERVALS[self.box])


def due_cards(cards, today):
    return [c for c in cards if c.due <= today]


if __name__ == "__main__":
    start = date(2026, 1, 5)
    card = Card("Why do virtual nodes reduce load imbalance?", due=start)
    today = start
    for ok in [True, True, False, True, True, True]:
        card.review(ok, today)
        print(f"{today}  recalled={ok!s:<5} -> box {card.box}, next {card.due}")
        today = card.due
