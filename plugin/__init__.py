"""Deliver profile-owned communication guidance through native Hermes hooks.

No session modes, workflow routing, output rewriting, network calls or model calls.
The canonical Caveman skill owns writing rules; this module only delivers them.
"""
import json
import logging
from threading import Lock

LOG = logging.getLogger("caveman-communication")
DISABLED = (
    "Caveman skill is disabled for this profile/platform. Suspend Caveman communication style, "
    "including earlier guidance; other instructions and task functionality remain unchanged."
)
MODES = ("lite", "full", "ultra", "wenyan-lite", "wenyan-full", "wenyan-ultra", "off", "manual")
HELP = (
    "Caveman communication: /caveman status|help|lite|full|ultra|wenyan-lite|wenyan-full|wenyan-ultra|off. "
    "Mode changes apply to the whole active profile, including existing and new sessions. "
    "Bare /caveman reports status; on/reset select full. /ultracave selects ultra; /megacave selects wenyan-full. "
    "Communication only: no input compression, reasoning control, workflow changes, proxy or editing model. "
    "Instruction delivery is not a guarantee of model adherence. Usage remains available through native Hermes usage reporting."
)


def skill_disabled(platform=None):
    """Recheck native policy without rereading the cached skill body."""
    from agent.skill_utils import get_disabled_skill_names
    return "caveman" in get_disabled_skill_names(platform)


def load_body(task_id=None):
    """Use native resolution so profile discovery and disabled-skill policy remain authoritative."""
    from tools.skills_tool import skill_view
    payload = json.loads(skill_view(name="caveman", task_id=task_id, preprocess=False))
    if not payload.get("success") or payload.get("name") != "caveman":
        raise ValueError("caveman_skill_unavailable")
    body = payload.get("content", "")
    if not isinstance(body, str) or not body.strip():
        raise ValueError("caveman_skill_empty")
    return body


def content_text(content):
    """Inspect instruction text without treating quoted user/tool payloads as loaded rules."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(block.get("text", "") for block in content
                         if isinstance(block, dict) and isinstance(block.get("text"), str))
    return ""


def instruction_text(request):
    parts = [content_text(request.get(key)) for key in ("instructions", "system")]
    for key in ("messages", "input"):
        for row in request.get(key, []) if isinstance(request.get(key), list) else []:
            if isinstance(row, dict) and row.get("role") in {"system", "developer"}:
                parts.append(content_text(row.get("content")))
    return "\n".join(parts)


def recent_guidance(request):
    rows = request.get("messages", request.get("input", []))
    fixed = "\n".join(content_text(request.get(key)) for key in ("instructions", "system"))
    if not isinstance(rows, list):
        return fixed
    # Only the current user turn counts for mode. Older reminders must not win.
    start = max((i for i, row in enumerate(rows)
                 if isinstance(row, dict) and row.get("role") == "user"), default=0)
    return fixed + "\n" + "\n".join(content_text(row.get("content")) for row in rows[start:]
                     if isinstance(row, dict) and row.get("role") in {"user", "developer"})


class Communication:
    def __init__(self, ctx):
        self.ctx = ctx
        self._body = None
        self._body_scope = None
        self._body_lock = Lock()

    def body(self, task_id=None):
        """Keep one cached body; never carry a trusted project override into another scope."""
        from agent.skill_utils import get_project_skills_dirs
        scope = tuple(path.resolve() for path in get_project_skills_dirs())
        with self._body_lock:
            if self._body is None or self._body_scope != scope:
                body = load_body(task_id)
                self._body, self._body_scope = body, scope
            return self._body

    def mode(self):
        mode = self.ctx.get_config("mode", "full")
        if mode not in MODES:
            raise ValueError("invalid_profile_mode")
        return mode

    def command(self, args=""):
        """Only explicit native commands change the one profile setting."""
        argument = args.strip().lower()
        if argument == "help":
            return HELP
        if argument in {"", "status"}:
            try:
                return f"Caveman mode: {self.mode()} (profile-wide)."
            except ValueError:
                return "Caveman configuration error: invalid profile mode. " + HELP
        selected = {"on": "full", "reset": "full", "wenyan": "wenyan-full"}.get(argument, argument)
        if selected not in MODES:
            return "Invalid Caveman mode. " + HELP
        try:
            self.ctx.set_config("mode", selected)
        except (OSError, ValueError, PermissionError):
            return "Caveman mode change failed; profile setting was not confirmed."
        return f"Caveman mode: {self.mode()} (profile-wide; applies on each session's next turn)."

    def pre_turn(self, session_id="", conversation_history=None, task_id=None, platform=None, **kwargs):
        try:
            mode = self.mode()
            if skill_disabled(platform):
                return {"context": DISABLED}
        except ValueError:
            return {"context": "Caveman configuration error: invalid profile mode. Report the limitation; do not claim Caveman was applied. Continue the requested work."}
        return {"context": self.reminder(mode)}

    @staticmethod
    def reminder(mode):
        if mode in {"off", "manual"}:
            return f"Caveman mode: {mode}. Profile setting supersedes earlier session voice selections. Suspend Caveman communication style; other instructions and task functionality remain unchanged."
        return (
            f"Caveman mode: {mode}. This profile setting supersedes earlier session voice selections. "
            "Apply the complete Caveman writing skill to every user-facing reply and tool-work explanation. "
            "Communication only: do not change internal reasoning, decisions, tools, execution, verification, task scope or provider routing. "
            "Do not rewrite user input, raw tool results or persisted artifacts. Preserve meaning, code, identifiers, numbers, units, negation, uncertainty, required formats and safety notices. "
            "Follow clarity exceptions and independently active presentation requirements. Do not announce this reminder or make an extra editing/model call."
        )

    def guard_request(self, request, task_id=None, api_mode=None, platform=None, **kwargs):
        """Check effective request instructions, including tool-loop and post-compaction calls."""
        if api_mode not in {"chat_completions", "codex_responses"}:
            LOG.debug("Caveman request recovery skipped: unqualified API mode %r", api_mode)
            return None
        if (api_mode == "chat_completions" and not isinstance(request.get("messages"), list)
                or api_mode == "codex_responses" and ("input" not in request or "messages" in request)):
            LOG.warning("Caveman request guidance unavailable: API mode/payload mismatch")
            return None
        additions = []
        try:
            mode = self.mode()
            reminder = self.reminder(mode)
            if skill_disabled(platform):
                reminder = DISABLED
            elif mode not in {"off", "manual"}:
                body = self.body(task_id)
                if body.strip() not in instruction_text(request):
                    additions.append("SOURCE SKILL: caveman\n" + body)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            LOG.warning("Caveman request guidance unavailable (%s)", type(exc).__name__)
            reminder = "Caveman guidance unavailable. State this limitation briefly and continue the original answer; do not claim Caveman was applied."
        if reminder not in recent_guidance(request):
            additions.append(reminder)
        if not additions:
            return None
        updated = dict(request)
        addition = "\n\n".join(additions)
        if api_mode == "codex_responses":
            # Codex accepts system/developer guidance only in top-level instructions,
            # not as role='developer' items in input. Keep the original prefix intact.
            original = request.get("instructions", "")
            if not isinstance(original, str):
                LOG.warning("Caveman request guidance unavailable: invalid instructions")
                return None
            updated["instructions"] = original + ("\n\n" if original else "") + addition
        else:
            # Chat Completions supports a request-local developer message. Stored
            # history, the frozen system prefix, user text and tool results stay intact.
            updated["messages"] = [*request["messages"], {"role": "developer", "content": addition}]
        return {"request": updated, "source": "caveman-communication", "reason": "restore_missing_writing_guidance"}


def register(ctx):
    worker = Communication(ctx)
    ctx.register_hook("pre_llm_call", worker.pre_turn)
    ctx.register_middleware("llm_request", worker.guard_request)
    ctx.register_command("caveman", worker.command, description="Profile-wide Caveman communication mode", args_hint="[mode|status|help]", argument_mode="text")
    ctx.register_command("caveman-help", lambda args="": HELP, description="Caveman communication help")
    ctx.register_command("ultracave", lambda args="": worker.command("ultra") if not args.strip() else "Use /caveman ultra; no task arguments.", description="Set profile-wide Ultra communication")
    ctx.register_command("megacave", lambda args="": worker.command("wenyan-full") if not args.strip() else "Use /caveman wenyan-full; no task arguments.", description="Set profile-wide Wenyan communication")
