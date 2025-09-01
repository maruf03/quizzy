"""Prometheus metrics registry for Quizzy.

Centralizes metric definitions to avoid duplicate registrations when code reloads.
"""
from __future__ import annotations

from prometheus_client import Counter, Histogram, Gauge
from prometheus_client import CollectorRegistry, CONTENT_TYPE_LATEST, generate_latest
from threading import Lock

_lock = Lock()
_initialized = False

# Public metric references
quiz_created_total: Counter
question_created_total: Counter
submission_created_total: Counter
submission_score_hist: Histogram
question_attempt_total: Counter
question_correct_total: Counter
active_users_gauge: Gauge


def init_metrics():
    global _initialized, quiz_created_total, question_created_total, submission_created_total
    global submission_score_hist, question_attempt_total, question_correct_total, active_users_gauge
    if _initialized:
        return
    with _lock:
        if _initialized:
            return
        quiz_created_total = Counter(
            'quizzy_quizzes_created_total', 'Total quizzes created')
        question_created_total = Counter(
            'quizzy_questions_created_total', 'Total questions created')
        submission_created_total = Counter(
            'quizzy_submissions_created_total', 'Total submissions created', ['quiz_id'])
        submission_score_hist = Histogram(
            'quizzy_submission_score', 'Submission scores distribution', buckets=(0,1,5,10,20,50,80,100))
        question_attempt_total = Counter(
            'quizzy_question_attempts_total', 'Total question attempts', ['question_id','correct'])
        question_correct_total = Counter(
            'quizzy_question_correct_total', 'Total correct answers per question', ['question_id'])
        active_users_gauge = Gauge(
            'quizzy_active_users', 'Active authenticated users (session based)')
        _initialized = True


init_metrics()
