from __future__ import annotations

from .base import CalendarProvider


class PlaceholderCalendarProvider(CalendarProvider):
    """
    Placeholder explícito para mantener la interfaz preparada sin
    introducir integración real de calendario en esta fase.
    """
    pass
