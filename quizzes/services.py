from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User

from .models import Quiz, Invitation


def ensure_creator(user: User, quiz: Quiz):
    if quiz.creator_id != user.id:
        raise PermissionDenied("Only the creator can manage invitations")


def is_invited(user: User, quiz: Quiz) -> bool:
    if quiz.visibility == Quiz.PUBLIC:
        return True
    if not user.is_authenticated:
        return False
    # User must have an accepted (and not declined) invitation
    return Invitation.objects.filter(quiz=quiz, email=user.email, accepted=True, declined=False).exists()


def invite_email(user: User, quiz: Quiz, email: str) -> Invitation:
    ensure_creator(user, quiz)
    invite, _ = Invitation.objects.get_or_create(quiz=quiz, email=email, defaults={"invited_by": user})
    return invite


def accept_invite(user: User, quiz: Quiz) -> bool:
    """Accept an invitation for the current user's email. Returns True if marked accepted."""
    updated = Invitation.objects.filter(quiz=quiz, email=user.email).update(accepted=True, declined=False)
    return updated > 0


def decline_invite(user: User, quiz: Quiz) -> bool:
    """Decline an invitation for the current user's email. Returns True if marked declined."""
    updated = Invitation.objects.filter(quiz=quiz, email=user.email).update(declined=True, accepted=False)
    return updated > 0
