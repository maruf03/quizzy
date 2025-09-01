from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def broadcast_leaderboard(quiz_id: int, payload=None):
    """Broadcast a leaderboard update to the quiz group.

    payload can be a dict; if None, send a minimal ping.
    """
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    group = f"quiz_{quiz_id}_leaderboard"
    message = {"type": "leaderboard.update", "payload": payload or {"quiz_id": quiz_id}}
    try:
        async_to_sync(channel_layer.group_send)(group, message)
        print(f"[WS][broadcast] quiz={quiz_id} group={group} payload_keys={list((payload or {}).keys())}")  # debug
    except Exception as e:  # pragma: no cover
        print(f"[WS][broadcast][error] quiz={quiz_id} {e}")
