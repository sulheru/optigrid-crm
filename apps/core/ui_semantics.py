# Central semantic mapping for UI rendering

PRIORITY_LEVELS = {
    "high": {
        "min_score": 70,
        "label": "High",
        "css": "priority-high",
        "color": "danger",
    },
    "medium": {
        "min_score": 40,
        "label": "Medium",
        "css": "priority-medium",
        "color": "warning",
    },
    "low": {
        "min_score": 0,
        "label": "Low",
        "css": "priority-low",
        "color": "success",
    },
}


def get_priority_level(score):
    for key, config in PRIORITY_LEVELS.items():
        if score >= config["min_score"]:
            return key, config
    return "low", PRIORITY_LEVELS["low"]


RECOMMENDATION_UI = {
    "followup": {
        "icon": "fa-reply",
        "color": "info",
        "actions": ["execute", "task"],
    },
    "reply_strategy": {
        "icon": "fa-envelope",
        "color": "info",
        "actions": ["execute", "task"],
    },
    "contact_strategy": {
        "icon": "fa-user-plus",
        "color": "primary",
        "actions": ["execute", "task"],
    },
    "qualification": {
        "icon": "fa-filter",
        "color": "warning",
        "actions": ["promote", "task"],
    },
    "pricing_strategy": {
        "icon": "fa-eur",
        "color": "warning",
        "actions": ["promote", "task"],
    },
    "schedule_call": {
        "icon": "fa-calendar",
        "color": "primary",
        "actions": ["promote", "task"],
    },
    "opportunity_review": {
        "icon": "fa-line-chart",
        "color": "primary",
        "actions": ["promote", "task"],
    },
}


DEFAULT_UI = {
    "icon": "fa-lightbulb-o",
    "color": "secondary",
    "actions": ["task"],
}


def get_recommendation_ui(rec_type):
    return RECOMMENDATION_UI.get(rec_type, DEFAULT_UI)


def build_available_actions(recommendation):
    rec_type = recommendation.recommendation_type
    ui = get_recommendation_ui(rec_type)

    actions = []

    for action in ui.get("actions", []):
        if action == "execute":
            actions.append(
                {
                    "type": "execute",
                    "label": "Execute",
                    "url": f"/recommendations/{recommendation.id}/execute/",
                    "style": "primary",
                    "icon": "fa-play",
                }
            )

        elif action == "promote":
            actions.append(
                {
                    "type": "promote",
                    "label": "Promote",
                    "url": f"/recommendations/{recommendation.id}/promote-opportunity/",
                    "style": "secondary",
                    "icon": "fa-line-chart",
                }
            )

        elif action == "task":
            actions.append(
                {
                    "type": "task",
                    "label": "Create Task",
                    "url": f"/recommendations/{recommendation.id}/create-task/",
                    "style": "secondary",
                    "icon": "fa-check-square-o",
                }
            )

    return actions
