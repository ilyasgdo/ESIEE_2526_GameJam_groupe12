"""Utility helpers for loading and updating sprite animations."""
from __future__ import annotations

from typing import Dict, Mapping, Sequence, Tuple

import pygame


FrameList = Sequence[pygame.Surface]
AnimationsDict = Dict[str, FrameList]


def load_sprite_sheet(path: str) -> pygame.Surface:
    """Load a sprite sheet with alpha handling."""
    return pygame.image.load(path).convert_alpha()


def extract_frames(
    sheet: pygame.Surface,
    row_index: int,
    frame_width: int,
    frame_height: int,
    columns: int = 4,
    scale: float = 1.0,
) -> FrameList:
    """Extract a full row of frames from *sheet*.

    Args:
        sheet: Source sprite sheet.
        row_index: Index of the row to extract.
        frame_width/height: Frame size in pixels.
        columns: Number of frames to read in the row.
        scale: Optional scale factor applied to each frame (>= 1).
    """
    frames: list[pygame.Surface] = []
    y = row_index * frame_height
    for col in range(columns):
        x = col * frame_width
        frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
        frame.blit(sheet, (0, 0), (x, y, frame_width, frame_height))
        if scale != 1.0:
            new_size = (
                max(1, int(frame_width * scale)),
                max(1, int(frame_height * scale)),
            )
            frame = pygame.transform.scale(frame, new_size)
        frames.append(frame)
    return frames


def load_directional_animations(
    sheet: pygame.Surface,
    frame_width: int,
    frame_height: int,
    rows_by_direction: Mapping[str, int],
    *,
    columns: int = 4,
    scale: float = 1.0,
) -> AnimationsDict:
    """Build a dict ``direction -> [frames]`` from the provided mapping."""
    return {
        direction: extract_frames(sheet, row, frame_width, frame_height, columns, scale)
        for direction, row in rows_by_direction.items()
    }


def change_direction(
    current_direction: str,
    new_direction: str,
    frame_index: float,
) -> Tuple[str, float]:
    """Return updated ``(direction, frame_index)`` when switching direction."""
    if new_direction != current_direction:
        return new_direction, 0.0
    return current_direction, frame_index


def advance_animation(
    frame_index: float,
    frames: FrameList,
    animation_speed: float,
    playing: bool,
) -> Tuple[float, pygame.Surface]:
    """Advance ``frame_index`` and return the current frame surface."""
    if not frames:
        raise ValueError("frames list must not be empty")

    if playing:
        frame_index += animation_speed
        if frame_index >= len(frames):
            frame_index = 0.0
        image = frames[int(frame_index)]
    else:
        image = frames[0]
    return frame_index, image


__all__ = [
    "load_sprite_sheet",
    "extract_frames",
    "load_directional_animations",
    "change_direction",
    "advance_animation",
]
