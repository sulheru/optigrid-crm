from __future__ import annotations
from abc import ABC, abstractmethod


class MailProvider(ABC):

    @abstractmethod
    def create_draft(self, *, to: str, subject: str, body: str) -> dict:
        pass

    @abstractmethod
    def send_email(self, *, draft_id: str | None = None) -> dict:
        pass

    @abstractmethod
    def fetch_inbox(self) -> list[dict]:
        pass


class LLMProvider(ABC):

    @abstractmethod
    def infer(self, prompt: str) -> str:
        pass

    @abstractmethod
    def classify(self, text: str) -> str:
        pass

    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass


class CalendarProvider(ABC):
    pass
