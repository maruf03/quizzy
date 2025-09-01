import json
from channels.generic.websocket import AsyncWebsocketConsumer


class LeaderboardConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.quiz_id = self.scope["url_route"]["kwargs"]["quiz_id"]
        self.group_name = f"quiz_{self.quiz_id}_leaderboard"
        print(f"[WS][connect] quiz={self.quiz_id} channel={self.channel_name}")  # debug
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self._send_leaderboard()

    async def disconnect(self, close_code):
        print(f"[WS][disconnect] quiz={self.quiz_id} code={close_code}")  # debug
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        # Ignore any client messages (broadcast only)
        return

    async def leaderboard_update(self, event):
        print(f"[WS][group_message] quiz={self.quiz_id} type=leaderboard.update")  # debug
        await self._send_leaderboard()

    async def _send_leaderboard(self):
        from .utils import get_leaderboard  # local import to avoid early model import
        data = get_leaderboard(int(self.quiz_id))
        print(f"[WS][send_snapshot] quiz={self.quiz_id} entries={len(data)}")  # debug
        await self.send(text_data=json.dumps({"type": "leaderboard", "entries": data}))
