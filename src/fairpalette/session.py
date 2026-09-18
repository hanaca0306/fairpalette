"""Lifecycle management for attribution generation sessions."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Sequence

from .manifest import AttributionManifest, Contributor


class AttributionSessionError(ValueError):
    """Raised when an attribution session transition is invalid."""


class SessionState(str, Enum):
    """Lifecycle states for a managed attribution session."""

    OPEN = "open"
    FINALIZED = "finalized"
    ABORTED = "aborted"


def _required_text(value: str, field_name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise AttributionSessionError(f"{field_name} must be a non-empty string")


def _validate_timestamp(value: str) -> None:
    _required_text(value, "timestamp")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise AttributionSessionError("timestamp must be an ISO 8601 datetime") from exc
    if parsed.tzinfo is None:
        raise AttributionSessionError("timestamp must include a timezone")


class AttributionSession:
    """Collect contributors for one generation and finalize exactly one manifest."""

    def __init__(
        self,
        generation_id: str,
        base_model: str,
        *,
        contributors: Sequence[Contributor] = (),
        timestamp: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> None:
        _required_text(generation_id, "generation_id")
        _required_text(base_model, "base_model")
        if metadata is not None and not isinstance(metadata, Mapping):
            raise AttributionSessionError("metadata must be a mapping")

        selected_timestamp = (
            datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            if timestamp is None
            else timestamp
        )
        _validate_timestamp(selected_timestamp)

        self._generation_id = generation_id
        self._base_model = base_model
        self._timestamp = selected_timestamp
        self._metadata = dict(metadata or {})
        self._contributors: list[Contributor] = []
        self._state = SessionState.OPEN
        self._manifest: AttributionManifest | None = None
        self._abort_reason: str | None = None

        for contributor in contributors:
            self.add_contributor(contributor)

    @property
    def generation_id(self) -> str:
        return self._generation_id

    @property
    def base_model(self) -> str:
        return self._base_model

    @property
    def timestamp(self) -> str:
        return self._timestamp

    @property
    def metadata(self) -> Mapping[str, Any]:
        return dict(self._metadata)

    @property
    def state(self) -> SessionState:
        return self._state

    @property
    def contributors(self) -> tuple[Contributor, ...]:
        """Return an immutable snapshot of the currently recorded contributors."""

        return tuple(self._contributors)

    @property
    def manifest(self) -> AttributionManifest | None:
        return self._manifest

    @property
    def abort_reason(self) -> str | None:
        return self._abort_reason

    def add_contributor(self, contributor: Contributor) -> None:
        """Record a contributor while the session is open."""

        self._require_open("add contributors")
        if not isinstance(contributor, Contributor):
            raise AttributionSessionError("contributor must be a Contributor")
        if any(item.module_id == contributor.module_id for item in self._contributors):
            raise AttributionSessionError(
                f"module_id already recorded in session: {contributor.module_id}"
            )
        self._contributors.append(contributor)

    def finalize(self) -> AttributionManifest:
        """Freeze the session and return its stable attribution manifest."""

        if self._state is SessionState.FINALIZED:
            assert self._manifest is not None
            return self._manifest
        self._require_open("finalize")
        if not self._contributors:
            raise AttributionSessionError(
                "at least one contributor is required before finalizing"
            )

        self._manifest = AttributionManifest(
            generation_id=self.generation_id,
            base_model=self.base_model,
            contributors=tuple(self._contributors),
            timestamp=self.timestamp,
            metadata=dict(self._metadata),
        )
        self._state = SessionState.FINALIZED
        return self._manifest

    def abort(self, reason: str | None = None) -> None:
        """Close an unfinished session without emitting a manifest."""

        if self._state is SessionState.ABORTED:
            return
        self._require_open("abort")
        if reason is not None:
            _required_text(reason, "reason")
        self._abort_reason = reason
        self._state = SessionState.ABORTED

    def _require_open(self, action: str) -> None:
        if self._state is not SessionState.OPEN:
            raise AttributionSessionError(
                f"cannot {action} a {self._state.value} attribution session"
            )


class AttributionSessionManager:
    """Own attribution sessions and enforce unique generation identifiers."""

    def __init__(self, *, default_base_model: str | None = None) -> None:
        if default_base_model is not None:
            _required_text(default_base_model, "default_base_model")
        self.default_base_model = default_base_model
        self._sessions: dict[str, AttributionSession] = {}

    @property
    def sessions(self) -> tuple[AttributionSession, ...]:
        """Return all sessions in creation order, including closed sessions."""

        return tuple(self._sessions.values())

    @property
    def open_sessions(self) -> tuple[AttributionSession, ...]:
        return tuple(
            session
            for session in self._sessions.values()
            if session.state is SessionState.OPEN
        )

    def start_session(
        self,
        generation_id: str,
        *,
        base_model: str | None = None,
        contributors: Sequence[Contributor] = (),
        timestamp: str | None = None,
        metadata: Mapping[str, Any] | None = None,
    ) -> AttributionSession:
        """Create and register a new open attribution session."""

        _required_text(generation_id, "generation_id")
        if generation_id in self._sessions:
            raise AttributionSessionError(
                f"generation_id is already managed: {generation_id}"
            )
        if base_model is not None:
            _required_text(base_model, "base_model")
        selected_base_model = (
            self.default_base_model if base_model is None else base_model
        )
        if selected_base_model is None:
            raise AttributionSessionError(
                "base_model is required when no default_base_model is configured"
            )

        session = AttributionSession(
            generation_id,
            selected_base_model,
            contributors=contributors,
            timestamp=timestamp,
            metadata=metadata,
        )
        self._sessions[generation_id] = session
        return session

    def get_session(self, generation_id: str) -> AttributionSession:
        try:
            return self._sessions[generation_id]
        except KeyError as exc:
            raise AttributionSessionError(
                f"unknown generation_id: {generation_id}"
            ) from exc

    def finalize_session(self, generation_id: str) -> AttributionManifest:
        return self.get_session(generation_id).finalize()

    def abort_session(self, generation_id: str, reason: str | None = None) -> None:
        self.get_session(generation_id).abort(reason)
