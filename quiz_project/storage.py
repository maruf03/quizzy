"""Custom S3 storage backends (optional static/media separation).

Only used when USE_SEPARATE_STATIC_BUCKET=1 is set in environment.
"""
import os
import uuid
from storages.backends.s3boto3 import S3Boto3Storage

def user_prefixed_path(subdir: str = ""):
    """Return an upload_to callable that isolates files per user id.

    Usage: FileField(upload_to=user_prefixed_path("avatars"), storage=PrivateUserMediaStorage())
    """
    base = subdir.strip("/")
    def _inner(instance, filename: str):  # pragma: no cover (path logic)
        user_id = getattr(instance, "user_id", None) or getattr(getattr(instance, "user", None), "id", None)
        if user_id is None:
            # Fallback bucket root (still namespaced) if user missing
            user_part = "anonymous"
        else:
            user_part = str(user_id)
        # Generate collision-resistant filename, preserve extension
        ext = ""
        if "." in filename:
            ext = "." + filename.rsplit(".", 1)[1].lower()
        new_name = uuid.uuid4().hex + ext
        if base:
            return f"users/{user_part}/{base}/{new_name}"
        return f"users/{user_part}/{new_name}"
    return _inner


class StaticRootS3Boto3Storage(S3Boto3Storage):
    location = "static"
    default_acl = os.environ.get("STATIC_AWS_DEFAULT_ACL") or None
    bucket_name = os.environ.get("STATIC_AWS_STORAGE_BUCKET_NAME") or os.environ.get("AWS_STORAGE_BUCKET_NAME")


class MediaRootS3Boto3Storage(S3Boto3Storage):
    location = "media"
    default_acl = os.environ.get("MEDIA_AWS_DEFAULT_ACL") or None
    bucket_name = os.environ.get("MEDIA_AWS_STORAGE_BUCKET_NAME") or os.environ.get("AWS_STORAGE_BUCKET_NAME")


class PublicMediaRootS3Boto3Storage(S3Boto3Storage):
    """Public bucket (unsigned URLs if QUERYSTRING disabled)."""
    location = os.environ.get("PUBLIC_MEDIA_LOCATION", "public")
    default_acl = os.environ.get("PUBLIC_MEDIA_AWS_DEFAULT_ACL", "public-read")
    bucket_name = os.environ.get("PUBLIC_MEDIA_AWS_STORAGE_BUCKET_NAME") or os.environ.get("AWS_STORAGE_BUCKET_NAME")
    querystring_auth = os.environ.get("PUBLIC_MEDIA_QUERYSTRING_AUTH", "0") != "0"


class PrivateUserMediaStorage(S3Boto3Storage):
    """Private per-user media (paths isolated by user id)."""
    location = os.environ.get("PRIVATE_MEDIA_LOCATION", "private")
    default_acl = os.environ.get("PRIVATE_MEDIA_AWS_DEFAULT_ACL", "private")
    bucket_name = os.environ.get("PRIVATE_MEDIA_AWS_STORAGE_BUCKET_NAME") or os.environ.get("AWS_STORAGE_BUCKET_NAME")
    file_overwrite = False
    querystring_auth = True
