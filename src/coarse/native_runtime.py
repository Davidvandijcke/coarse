"""Suspend model calls as native-agent tasks and replay validated responses.

Pending work deliberately inherits BaseException: legacy optional-stage fallbacks
catch Exception, and must never mistake an unanswered task for a failed stage.
"""

from __future__ import annotations

import threading
from pathlib import Path

from pydantic import BaseModel, Field, model_validator

from coarse.native_store import atomic_json, digest, read_json
from coarse.prompts import PERPLEXITY_SYSTEM, perplexity_user


class NativePending(BaseException):
    pass


class NativeInvalid(BaseException):
    pass


class NativeLiterature(BaseModel):
    searched: bool
    context: str = Field(min_length=1)
    sources: list[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def source_evidence(self):
        if self.searched and not self.sources:
            raise ValueError("A completed search needs source URLs")
        if any(not url.startswith(("https://", "http://")) for url in self.sources):
            raise ValueError("Sources must be HTTP(S) URLs")
        return self


class NativeText(BaseModel):
    text: str = Field(min_length=1)


class NativeRuntime:
    supports_prompt_caching = False
    is_reasoning = True
    cost_usd = 0.0  # No paid reasoning API calls; subscription usage is unknown.

    def __init__(self, workspace: Path, run: dict):
        self.workspace = workspace
        self.run = run
        self.model = run["model"]
        self.models: dict[str, type[BaseModel]] = {}
        self.seen: set[str] = set()
        self.pending: set[str] = set()
        self.lock = threading.Lock()

    def create_client(self, **kwargs):
        return self

    def add_cost(self, cost_usd):
        if cost_usd:
            raise NativeInvalid("Native reasoning cannot accumulate API charges")

    def completed_futures(self, futures, **kwargs):
        # Workers still run concurrently, but replay consumes results in their
        # scheduled order. Completion timing must not change downstream prompts.
        return iter(futures)

    def complete(self, messages, response_model, **kwargs):
        try:
            return self._complete(messages, response_model, **kwargs)
        except (NativePending, NativeInvalid):
            raise
        except Exception as exc:
            raise NativeInvalid("Native task checkpoint failed validation") from exc

    def _complete(self, messages, response_model, max_tokens=4096, temperature=0.3, **kwargs):
        request = {
            "messages": messages,
            "response_schema": response_model.model_json_schema(),
            "parameters": {"max_tokens": max_tokens, "temperature": temperature},
            "host": self.run["host"],
            "model": self.run["model"],
            "effort": self.run["effort"],
        }
        request_digest = digest(request)
        task_id = request_digest[:24]
        task = {
            **request,
            "task_id": task_id,
            "request_digest": request_digest,
            "response_type": response_model.__name__,
            "web_search": response_model is NativeLiterature,
        }
        with self.lock:
            self.models[task_id] = response_model
            self.seen.add(task_id)
            task_path = self.workspace / "tasks" / f"{task_id}.json"
            if task_path.exists():
                if task_path.is_symlink() or read_json(task_path) != task:
                    raise NativeInvalid("Task changed; restore the original workspace")
            else:
                atomic_json(task_path, task)
            result_path = self.workspace / "results" / f"{task_id}.json"
            if not result_path.exists():
                self.pending.add(task_id)
                raise NativePending()
            if result_path.is_symlink():
                raise NativeInvalid("Response file must not be a symlink")
            response = read_json(result_path)
        try:
            if response["request_digest"] != request_digest:
                raise ValueError("Response belongs to another task")
            return response_model.model_validate(response["result"])
        except Exception as exc:
            raise NativeInvalid("Stored response failed validation") from exc

    def complete_text(self, messages, **kwargs):
        return self.complete(messages, NativeText, **kwargs).text

    def search_literature(self, title, abstract, client, deep_search=False, **kwargs):
        result = self.complete(
            [
                {
                    "role": "system",
                    "content": PERPLEXITY_SYSTEM + "\nUse native web tools. "
                    "If search is unavailable, set searched=false and state that limitation; "
                    "never invent citations. Return source URLs for a completed search.",
                },
                {"role": "user", "content": perplexity_user(title, abstract[:1500])},
            ],
            NativeLiterature,
        )
        prefix = "Native literature search" if result.searched else "Literature search unavailable"
        return prefix + ":\n" + result.context + "\n" + "\n".join(result.sources)
