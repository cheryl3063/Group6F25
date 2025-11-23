# alert_rules.py

LOW_SCORE_THRESHOLD = 50  # you can change this later if needed


class AlertRules:
    """
    Simple helper class to evaluate if a safety score is low.
    Also tracks whether we've already shown an alert for this trip
    (used later for Task 57: prevent alert spam).
    """
    def __init__(self):
        self.alert_sent = False

    def evaluate_score(self, score):
        """
        Returns True if a low-score alert should be shown, otherwise False.
        """
        try:
            value = float(score)
        except (TypeError, ValueError):
            return False

        # If we've already shown an alert this trip, do nothing
        if self.alert_sent:
            return False

        # Check threshold
        if value < LOW_SCORE_THRESHOLD:
            self.alert_sent = True
            return True

        return False

    def reset(self):
        """
        Call this before a new trip starts to allow alerts again.
        (We'll hook this up in Task 57.)
        """
        self.alert_sent = False