from pathlib import Path
import re

path = Path("apps/recommendations/views.py")
text = path.read_text()

if "from django.contrib import messages" not in text:
    text = text.replace(
        "from django.shortcuts import get_object_or_404, redirect, render\n",
        "from django.contrib import messages\nfrom django.shortcuts import get_object_or_404, redirect, render\n",
    )

text = text.replace(
    "from apps.emailing.services.reply_generator import generate_followup_draft_from_inbound\n",
    "",
)
text = text.replace(
    "from apps.opportunities.services.promote import promote_task_to_opportunity\n",
    "",
)
text = text.replace(
    "from apps.tasks.services.materialize import materialize_recommendation_as_task\n",
    "",
)

if "from apps.recommendations.execution import RecommendationExecutionError, execute_recommendation_service\n" not in text:
    text = text.replace(
        "from apps.recommendations.models import AIRecommendation\n",
        "from apps.recommendations.models import AIRecommendation\nfrom apps.recommendations.execution import RecommendationExecutionError, execute_recommendation_service\n",
    )

if "def _redirect_back_to_recommendations" not in text:
    marker = "def _decorate_recommendation_for_ui(recommendation: AIRecommendation):"
    helper = """
def _redirect_back_to_recommendations(request):
    return redirect(request.META.get("HTTP_REFERER") or "/recommendations/")


"""
    text = text.replace(marker, helper + marker)

patterns = [
    (
        r"@require_POST\s*\ndef execute_followup\(request, pk\):.*?(?=^@require_POST\s*\ndef execute_contact_strategy|\Z)",
        """@require_POST
def execute_followup(request, pk):
    recommendation = get_object_or_404(AIRecommendation, pk=pk)
    try:
        execute_recommendation_service(recommendation, actor="recommendations_view")
        messages.success(request, "Recommendation executed.")
    except RecommendationExecutionError as exc:
        messages.error(request, str(exc))
    return _redirect_back_to_recommendations(request)

""",
    ),
    (
        r"@require_POST\s*\ndef execute_contact_strategy\(request, pk\):.*?(?=^@require_POST\s*\ndef execute_reply_strategy|\Z)",
        """@require_POST
def execute_contact_strategy(request, pk):
    recommendation = get_object_or_404(AIRecommendation, pk=pk)
    try:
        execute_recommendation_service(recommendation, actor="recommendations_view")
        messages.success(request, "Recommendation executed.")
    except RecommendationExecutionError as exc:
        messages.error(request, str(exc))
    return _redirect_back_to_recommendations(request)

""",
    ),
    (
        r"@require_POST\s*\ndef execute_reply_strategy\(request, pk\):.*?(?=^@require_POST\s*\ndef execute_recommendation|\Z)",
        """@require_POST
def execute_reply_strategy(request, pk):
    recommendation = get_object_or_404(AIRecommendation, pk=pk)
    try:
        execute_recommendation_service(recommendation, actor="recommendations_view")
        messages.success(request, "Recommendation executed.")
    except RecommendationExecutionError as exc:
        messages.error(request, str(exc))
    return _redirect_back_to_recommendations(request)

""",
    ),
    (
        r"@require_POST\s*\ndef execute_recommendation\(request, pk\):.*?\Z",
        """@require_POST
def execute_recommendation(request, pk):
    recommendation = get_object_or_404(AIRecommendation, pk=pk)
    try:
        execute_recommendation_service(recommendation, actor="recommendations_view")
        messages.success(request, "Recommendation executed.")
    except RecommendationExecutionError as exc:
        messages.error(request, str(exc))
    return _redirect_back_to_recommendations(request)
""",
    ),
]

for pattern, replacement in patterns:
    text, count = re.subn(pattern, replacement, text, flags=re.MULTILINE | re.DOTALL)
    if count == 0:
        print(f"WARNING: no match for pattern: {pattern}")

path.write_text(text)
print("patched", path)
