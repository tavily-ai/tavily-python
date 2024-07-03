from dataclasses import dataclass, asdict
from typing import Sequence, Literal

@dataclass
class TavilyResult:
    title: str
    url: str
    content: str
    score: float
    raw_content: str = None
    published_date: str = None


@dataclass
class TavilyContextResult:
    url: str
    content: str

@dataclass
class TavilyResponse:
    query: str
    follow_up_questions: Sequence[str]
    answer: str
    images: Sequence[str]
    results: Sequence[TavilyResult]
    response_time: float

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def to_dict(self):
        out = asdict(self)
        for result in out["results"]:
            result["published date"] = result["published_date"]
        return out