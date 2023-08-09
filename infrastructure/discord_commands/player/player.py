from abc import ABC, abstractmethod
from typing import Optional, Any, Tuple


class Song:
    def __init__(self, filename=None, title=None, meta=None, source=None):
        self.filename = filename
        self.title = title
        self.meta = meta
        self.source = source


class MusicPlayer(ABC):
    def __init__(self):
        self.queues = {}
        self.current = {}

    @abstractmethod
    async def get_song_from_url(self, url: str):
        raise NotImplementedError

    async def add_to_queue(
        self, guild_id: int, url: str
    ) -> Tuple[Optional[Song], Optional[str]]:
        try:
            song: Song = await self.get_song_from_url(url=url)
        except Exception as e:
            raise 

        if guild_id not in self.queues:
            self.queues[guild_id] = [song]
        else:
            self.queues[guild_id].append(song)

        return song, None

    def pop_from_queue(self, guild_id: int) -> Optional[Song]:
        if guild_id not in self.queues:
            return None

        if not self.queues[guild_id]:
            return None

        self.current[guild_id] = self.queues[guild_id].pop()
        return self.current[guild_id]

    def clear_queue(self, guild_id: int) -> int:
        if guild_id not in self.queues:
            return 0

        num_elements = len(self.queues[guild_id])
        del self.queues[guild_id]
        del self.current[guild_id]
        return num_elements

    def print_queue(self, guild_id: int) -> str:
        if (
            guild_id in self.current
            and guild_id in self.queues
            and self.current[guild_id] is not None
            and not self.queues[guild_id]
        ):
            head_song = self.current[guild_id]
            head_title = head_song.title

            message = f"**PLAYING. **{head_title}"
            for pos, song in enumerate(self.queues[guild_id]):
                message += f"\n**{pos}. **{song.title}"

            return message

        return "No songs playing or in queue."
