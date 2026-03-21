# Ruta: /home/sulheru/OptiGrid_Project/og_pilot/optigrid_crm/apps/strategy/views.py
# LLM INFO: Este encabezado contiene la ruta absoluta de origen. Mantenlo para preservar el contexto de ubicación del archivo.
from __future__ import annotations

from django.shortcuts import redirect, render
from django.views import View

from .services.context_builder import build_strategy_context
from .services.llm_backends import generate_strategy_answer


class StrategyChatView(View):
    template_name = "strategy/chat.html"
    session_key = "strategy_chat_history"
    max_history = 20

    def get(self, request):
        strategy_context = build_strategy_context()
        history = request.session.get(self.session_key, [])

        return render(
            request,
            self.template_name,
            {
                "history": history,
                "context_summary": strategy_context.executive_summary,
                "suggested_prompts": [
                    "¿Qué hago hoy?",
                    "¿Qué oportunidades están en riesgo?",
                    "¿Dónde debo enfocarme?",
                    "¿Qué oportunidades tienen más potencial?",
                    "¿Qué bloqueos comerciales tengo ahora mismo?",
                ],
            },
        )

    def post(self, request):
        if request.POST.get("clear_history") == "1":
            request.session[self.session_key] = []
            request.session.modified = True
            return redirect("strategy:chat")

        question = (request.POST.get("message") or "").strip()
        if not question:
            return redirect("strategy:chat")

        strategy_context = build_strategy_context()
        result = generate_strategy_answer(
            question=question,
            context=strategy_context.as_dict(),
        )

        history = request.session.get(self.session_key, [])
        history.append({"role": "user", "content": question})
        history.append(
            {
                "role": "assistant",
                "content": result.text,
                "meta": f"backend={result.backend_name}",
            }
        )
        request.session[self.session_key] = history[-self.max_history:]
        request.session.modified = True

        return redirect("strategy:chat")
