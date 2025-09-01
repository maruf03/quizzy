class ScoringStrategy:
    def compute(self, attempts):  # attempts: list[QuestionAttempt]
        raise NotImplementedError


class BestAttempt(ScoringStrategy):
    def compute(self, attempts):
        return int(any(a.is_correct for a in attempts))


class LastAttempt(ScoringStrategy):
    def compute(self, attempts):
        return int(attempts[-1].is_correct) if attempts else 0


class FirstAttempt(ScoringStrategy):
    def compute(self, attempts):
        return int(attempts[0].is_correct) if attempts else 0


def get_strategy(quiz):
    return {"best": BestAttempt(), "last": LastAttempt(), "first": FirstAttempt()}[quiz.scoring_policy]
