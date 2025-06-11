"""Utility functions for managing Face Invaders high scores."""

from json import load as json_load, dump as json_dump

from face_invaders import constants as C

def load_high_scores():
    """Return saved high scores or an empty list if none exist."""
    try:
        with open(C.HIGH_SCORES_FNAME, "r") as file:
            return json_load(file)
    except Exception:
        return []

def save_high_scores(high_scores):
    """Persist high scores to storage."""
    with open(C.HIGH_SCORES_FNAME, "w") as file:
        json_dump(high_scores, file)

def check_high_score(high_scores, score):
    """Return True if ``score`` qualifies as a high score."""
    if len(high_scores) < C.NUM_HIGH_SCORES:
        return True
    else:
        for _, high_score in high_scores:
            if score > high_score:
                return True
    return False

def update_high_scores(high_scores, initials, score):
    """Update ``high_scores`` with a new entry and persist to disk."""
    high_scores.append((initials, score))
    high_scores.sort(key=lambda item: item[1], reverse=True)
    if len(high_scores) > C.NUM_HIGH_SCORES:
        high_scores.pop()
    save_high_scores(high_scores)

