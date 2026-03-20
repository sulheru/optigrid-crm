# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/opportunities/services/autotasker.py
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from django.conf import settings
from django.utils import timezone

from apps.tasks.models import CRMTask


PRIORITY_RANK = {
    "low": 1,
    "monitor": 2,
    "medium": 3,
    "high": 4,
}

ACTION_TO_TASK = {
    "schedule_followup": {
        "task_type": "follow_up",
        "title": "Follow up on opportunity",
        "description": "Automated follow-up task created from Opportunity Intelligence timing signals.",
        "priority": "high",
        "due_days": 2,
    },
    "advance_opportunity": {
        "task_type": "opportunity_review",
        "title": "Advance opportunity review",
        "description": "Automated task created to move a high-potential opportunity forward.",
        "priority": "high",
        "due_days": 1,
    },
    "review_pricing_strategy": {
        "task_type": "pricing_review",
        "title": "Review pricing strategy",
        "description": "Automated pricing review task created from pricing risk signals.",
        "priority": "high",
        "due_days": 1,
    },
    "review_opportunity_stall": {
        "task_type": "opportunity_review",
        "title": "Review stalled opportunity",
        "description": "Automated review task created because opportunity activity appears stale.",
        "priority": "normal",
        "due_days": 2,
    },
    "define_next_action": {
        "task_type": "review_manually",
        "title": "Define next action",
        "description": "Automated manual review task created because no open task exists for this opportunity.",
        "priority": "normal",
        "due_days": 1,
    },
}


@dataclass
class AutotaskResult:
    created: int
    reused: int
    skipped: int
    tasks: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "created": self.created,
            "reused": self.reused,
            "skipped": self.skipped,
            "tasks": self.tasks,
        }


def _get_setting(name: str, default):
    return getattr(settings, name, default)


def _priority_meets_threshold(bucket: str) -> bool:
    minimum = str(_get_setting("AUTO_TASKING_MIN_PRIORITY", "medium")).strip().lower()
    return PRIORITY_RANK.get(bucket, 0) >= PRIORITY_RANK.get(minimum, 3)


def _allowed_actions() -> set[str]:
    configured = _get_setting(
        "AUTO_TASKING_ALLOWED_ACTIONS",
        [
            "schedule_followup",
            "advance_opportunity",
            "review_pricing_strategy",
            "review_opportunity_stall",
            "define_next_action",
        ],
    )
    return {str(item).strip() for item in configured if str(item).strip()}


def _task_title(base_title: str, opportunity) -> str:
    title = str(getattr(opportunity, "title", "") or "").strip()
    if title:
        return f"{base_title} · {title}"
    return base_title


def _task_description(base_description: str, opportunity, action: str, risk_flags: list[str]) -> str:
    parts = [
        base_description,
        f"Opportunity ID: {opportunity.id}",
        f"Stage: {getattr(opportunity, 'stage', '')}",
        f"Action: {action}",
    ]
    if risk_flags:
        parts.append(f"Risk flags: {', '.join(risk_flags)}")
    return "\n".join(parts)


def _existing_task(opportunity, task_type: str, action: str):
    return CRMTask.objects.filter(
        opportunity=opportunity,
        task_type=task_type,
        source="auto",
        source_action=action,
        is_revoked=False,
        status__in=["open", "in_progress"],
    ).order_by("id").first()


def _has_revoked_task(opportunity, action: str) -> bool:
    return CRMTask.objects.filter(
        opportunity=opportunity,
        source="auto",
        source_action=action,
        is_revoked=True,
    ).exists()


def auto_materialize_tasks(
    *,
    opportunity,
    priority_bucket: str,
    next_actions: list[str],
    risk_flags: list[str] | None = None,
) -> AutotaskResult:
    if not _get_setting("AUTO_TASKING_ENABLED", False):
        return AutotaskResult(created=0, reused=0, skipped=0, tasks=[])

    if str(getattr(opportunity, "stage", "")).lower() in {"won", "lost"}:
        return AutotaskResult(created=0, reused=0, skipped=0, tasks=[])

    if not _priority_meets_threshold(priority_bucket):
        return AutotaskResult(created=0, reused=0, skipped=len(next_actions), tasks=[])

    allowed_actions = _allowed_actions()
    created = 0
    reused = 0
    skipped = 0
    task_rows: list[dict[str, Any]] = []
    risk_flags = risk_flags or []

    for action in next_actions:
        if action not in allowed_actions:
            skipped += 1
            continue

        mapping = ACTION_TO_TASK.get(action)
        if not mapping:
            skipped += 1
            continue

        if _has_revoked_task(opportunity, action):
            skipped += 1
            task_rows.append(
                {
                    "task_id": None,
                    "status": "blocked_revoked",
                    "task_type": mapping["task_type"],
                    "source_action": action,
                }
            )
            continue

        existing = _existing_task(
            opportunity=opportunity,
            task_type=mapping["task_type"],
            action=action,
        )
        if existing is not None:
            reused += 1
            task_rows.append(
                {
                    "task_id": existing.id,
                    "status": "reused",
                    "task_type": existing.task_type,
                    "source_action": existing.source_action,
                }
            )
            continue

        due_days = int(mapping.get("due_days", 1))
        task = CRMTask.objects.create(
            opportunity=opportunity,
            source_recommendation=getattr(opportunity, "source_recommendation", None),
            title=_task_title(mapping["title"], opportunity),
            description=_task_description(
                mapping["description"],
                opportunity,
                action,
                risk_flags,
            ),
            task_type=mapping["task_type"],
            status="open",
            priority=mapping.get("priority", "normal"),
            due_at=timezone.now() + timedelta(days=due_days),
            source="auto",
            source_action=action,
            is_revoked=False,
        )
        created += 1
        task_rows.append(
            {
                "task_id": task.id,
                "status": "created",
                "task_type": task.task_type,
                "source_action": task.source_action,
            }
        )

    return AutotaskResult(
        created=created,
        reused=reused,
        skipped=skipped,
        tasks=task_rows,
    )
