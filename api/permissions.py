from rest_framework.permissions import BasePermission, SAFE_METHODS
from quizzes.models import Quiz
from quizzes.services import is_invited


class IsCreatorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return getattr(obj, "creator_id", None) == getattr(request.user, "id", None)


class CanViewQuiz(BasePermission):
    """Allow viewing if public & published, creator, or invited for private."""

    def has_object_permission(self, request, view, obj: Quiz):
        if obj.is_published and obj.visibility == Quiz.PUBLIC:
            return True
        if request.user.is_authenticated and obj.creator_id == request.user.id:
            return True
        if obj.visibility == Quiz.PRIVATE:
            return is_invited(request.user, obj)
        return False
