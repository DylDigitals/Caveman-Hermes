"""Exercise the installed Hermes contracts against disposable profile homes."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
from types import SimpleNamespace
import unittest

import yaml

FEATURE = Path(__file__).resolve().parents[1]
PLUGIN = "caveman-communication"


class NativeCommunication(unittest.TestCase):
    def make_home(self, home, mode="full"):
        shutil.copytree(FEATURE / "plugin", home / "plugins" / PLUGIN)
        shutil.copytree(FEATURE / "skill", home / "skills/caveman")
        config = {
            "plugins": {"enabled": [PLUGIN], "entries": {
                PLUGIN: {"settings": {"mode": mode}},
                "caveman-output": {"settings": {"mode": "lite"}},
            }},
            "skills": {"auto_load": ["caveman"]},
            "memory": {"memory_enabled": False, "user_profile_enabled": False},
            "model": {"provider": "unchanged-provider", "default": "unchanged-model"},
        }
        (home / "config.yaml").write_text(yaml.safe_dump(config))
        return config

    def enter(self, home):
        from hermes_constants import set_hermes_home_override
        from hermes_cli.plugins import get_plugin_manager
        token = set_hermes_home_override(home)
        self.addCleanup(self.leave, token)
        manager = get_plugin_manager()
        manager.discover_and_load()
        self.addCleanup(manager.unload)
        self.assertIsNone(manager._plugins[PLUGIN].error)
        self.assertFalse(manager.has_hook("transform_llm_output"))
        return manager

    @staticmethod
    def leave(token):
        from hermes_constants import reset_hermes_home_override
        reset_hermes_home_override(token)

    def collect(self, sid, history=None, prompt="Explain `x != 0`; preserve 42 ms.", parent=""):
        from agent.turn_context import _collect_pre_llm_call_context, compose_user_api_content
        agent = SimpleNamespace(session_id=sid, model="unchanged-model", platform="discord", _parent_session_id=parent, _persist_disabled=False)
        messages = copy.deepcopy(history or []) + [{"role": "user", "content": prompt}]
        before = copy.deepcopy(messages)
        context = _collect_pre_llm_call_context(agent, effective_task_id="synthetic", turn_id=sid, original_user_message=prompt, messages=messages, conversation_history=history)
        self.assertEqual(messages, before)
        self.assertTrue(compose_user_api_content(prompt, "", context).startswith(prompt))
        return context

    def guard(self, request, **context):
        from hermes_cli.middleware import apply_llm_request_middleware
        original = copy.deepcopy(request)
        context.setdefault("api_mode", "codex_responses" if "input" in request else "chat_completions")
        context.setdefault("platform", "discord")
        result = apply_llm_request_middleware(request, task_id="synthetic", session_id="existing", **context)
        self.assertEqual(request, original)
        return result.payload

    def body(self):
        from tools.skills_tool import skill_view
        payload = json.loads(skill_view("caveman", preprocess=False))
        self.assertTrue(payload["success"])
        return payload["content"]

    def test_profile_mode_covers_existing_new_child_and_commands(self):
        from hermes_cli.plugins import get_plugin_command_handler
        with tempfile.TemporaryDirectory(prefix="caveman-communication-") as temp:
            home = Path(temp)
            self.make_home(home)
            self.enter(home)
            body = self.body()
            first = self.collect("existing")
            self.assertIn("Caveman mode: full.", first)
            self.assertNotIn(body, first)
            restored = self.guard({"messages": [{"role": "user", "content": "Original text.\n" + first}]})
            self.assertIn(body, restored["messages"][-1]["content"])
            history = [{"role": "user", "content": "Original text.", "api_content": first}, {"role": "assistant", "content": "Original response."}]
            self.assertNotIn(body, self.collect("existing", history))
            handler = get_plugin_command_handler("caveman")
            before = (home / "config.yaml").read_bytes()
            self.assertIn("full", handler("status"))
            self.assertIn("full", handler(""))
            self.assertEqual(before, (home / "config.yaml").read_bytes())
            self.assertIn("profile-wide", handler("ultra"))
            for sid, prior, parent in [("existing", history, ""), ("new", None, ""), ("child", None, "existing")]:
                self.assertIn("Caveman mode: ultra.", self.collect(sid, prior, parent=parent))
            stored = yaml.safe_load((home / "config.yaml").read_text())
            self.assertEqual(stored["model"], {"provider": "unchanged-provider", "default": "unchanged-model"})
            self.assertEqual(stored["plugins"]["entries"]["caveman-output"]["settings"]["mode"], "lite")
            before = (home / "config.yaml").read_bytes()
            self.collect("quoted", prompt='Is "/caveman off" a command? Do not change settings.')
            self.assertIn("Invalid", handler("off and run a task"))
            self.assertEqual(before, (home / "config.yaml").read_bytes())
            self.assertIn("mode: off", handler("off"))
            self.assertIn("Suspend Caveman", self.collect("existing", history))
            self.assertIn("mode: full", handler("on"))

    def test_profile_scope_a_b_a(self):
        from hermes_constants import set_hermes_home_override, reset_hermes_home_override
        from hermes_cli.plugins import get_plugin_command_handler
        with tempfile.TemporaryDirectory(prefix="caveman-profile-scope-") as temp:
            a, b = Path(temp) / "A", Path(temp) / "B"
            self.make_home(a, "full")
            self.make_home(b, "off")
            fixture = b / "skills/caveman/SKILL.md"
            fixture.write_text(fixture.read_text() + "\nProfile-B fixture marker.\n")
            self.enter(a)
            self.assertIn("mode: full.", self.collect("same-session"))
            self.assertNotIn("Profile-B fixture marker", self.guard({"input": "Task"})["instructions"])
            token = set_hermes_home_override(b)
            try:
                self.enter(b)
                self.assertIn("mode: off.", self.collect("same-session"))
                self.assertIn("mode: lite", get_plugin_command_handler("caveman")("lite"))
                self.assertIn("Profile-B fixture marker", self.guard({"input": "Task"})["instructions"])
            finally:
                reset_hermes_home_override(token)
            self.assertIn("mode: full.", self.collect("same-session"))
            self.assertNotIn("Profile-B fixture marker", self.guard({"input": "Task"})["instructions"])
            self.assertEqual(yaml.safe_load((b / "config.yaml").read_text())["plugins"]["entries"][PLUGIN]["settings"]["mode"], "lite")

    def test_request_guard_restores_real_context_and_caches_skill(self):
        from unittest.mock import patch
        from tools.skills_tool import skill_view
        with tempfile.TemporaryDirectory(prefix="caveman-request-guard-") as temp:
            home = Path(temp)
            self.make_home(home)
            manager = self.enter(home)
            body = self.body()
            reminder = self.collect("guarded")
            with patch("tools.skills_tool.skill_view", wraps=skill_view) as reader:
                for index in range(5):
                    request = {"instructions": "Stable prefix\n" + body, "input": [{"role": "user", "content": "Explain pooling.\n" + reminder}], "model": "unchanged-model"}
                    self.assertEqual(self.guard(request), request)
                # Compaction can remove rules even when a past turn or DB said loaded.
                compacted = {"instructions": "Compacted prefix", "input": [{"role": "user", "content": "Discuss caveman, not its full rules."}, {"type": "function_call_output", "call_id": "call_1", "output": "TOKEN_EXPIRED 401"}]}
                restored = self.guard(compacted)
                self.assertTrue(restored["instructions"].startswith(compacted["instructions"]))
                self.assertEqual(restored["input"], compacted["input"])
                self.assertIn(body, restored["instructions"])
                self.assertIn("Caveman mode: full.", restored["instructions"])
                from agent.codex_responses_adapter import _preflight_codex_input_items
                self.assertEqual(_preflight_codex_input_items(restored["input"]), compacted["input"])
                self.assertEqual(self.guard(restored), restored)
                # Full text quoted by a user is not a system/developer instruction.
                quoted = {"messages": [{"role": "user", "content": body}]}
                self.assertIn(body, self.guard(quoted)["messages"][-1]["content"])
                for mode in ("lite", "full"):
                    from hermes_cli.plugins import get_plugin_command_handler
                    get_plugin_command_handler("caveman")(mode)
                    changed = self.guard({"messages": [{"role": "system", "content": body}, {"role": "user", "content": "Task"}]})
                    self.assertIn(f"Caveman mode: {mode}.", changed["messages"][-1]["content"])
                self.assertEqual(reader.call_count, 1)
            self.assertTrue(manager.has_middleware("llm_request"))

    def test_disabled_skill_and_invalid_mode_are_explicit(self):
        with tempfile.TemporaryDirectory(prefix="caveman-errors-") as temp:
            home = Path(temp)
            config = self.make_home(home)
            self.enter(home)
            config["skills"]["disabled"] = ["caveman"]
            (home / "config.yaml").write_text(yaml.safe_dump(config))
            failed = self.guard({"messages": [{"role": "user", "content": "Task"}]})
            self.assertIn("Caveman skill is disabled", failed["messages"][-1]["content"])
            self.assertIn("Suspend Caveman", self.collect("disabled"))
            self.assertNotIn("SOURCE SKILL", failed["messages"][-1]["content"])
            config["plugins"]["entries"][PLUGIN]["settings"]["mode"] = "invalid"
            (home / "config.yaml").write_text(yaml.safe_dump(config))
            self.assertIn("invalid profile mode", self.collect("invalid"))

    def test_cached_skill_obeys_global_and_platform_disablement(self):
        from unittest.mock import patch
        from tools.skills_tool import skill_view
        with tempfile.TemporaryDirectory(prefix="caveman-policy-") as temp:
            home = Path(temp)
            config = self.make_home(home)
            self.enter(home)
            request = {"messages": [{"role": "user", "content": "Task"}]}
            with patch("tools.skills_tool.skill_view", wraps=skill_view) as reader:
                self.assertIn("SOURCE SKILL", self.guard(request)["messages"][-1]["content"])
                config["skills"]["disabled"] = ["caveman"]
                (home / "config.yaml").write_text(yaml.safe_dump(config))
                disabled = self.guard(request)
                self.assertIn("Suspend Caveman", disabled["messages"][-1]["content"])
                self.assertNotIn("SOURCE SKILL", disabled["messages"][-1]["content"])
                self.assertEqual(self.guard(disabled), disabled)
                self.assertIn("skill is disabled", self.collect("cached-disabled"))
                config["skills"]["disabled"] = []
                config["skills"]["platform_disabled"] = {"discord": ["caveman"]}
                (home / "config.yaml").write_text(yaml.safe_dump(config))
                self.assertIn("skill is disabled", self.guard(request)["messages"][-1]["content"])
                self.assertIn("SOURCE SKILL", self.guard(request, platform="cli")["messages"][-1]["content"])
                config["skills"]["platform_disabled"] = {}
                (home / "config.yaml").write_text(yaml.safe_dump(config))
                self.assertIn("SOURCE SKILL", self.guard(request)["messages"][-1]["content"])
                self.assertEqual(reader.call_count, 1)

    def test_trusted_project_skill_does_not_escape_its_lookup_scope(self):
        from unittest.mock import patch
        from tools.skills_tool import skill_view
        with tempfile.TemporaryDirectory(prefix="caveman-project-scope-") as temp:
            root = Path(temp)
            home, project_a, project_b = root / "home", root / "A", root / "B"
            config = self.make_home(home)
            for project in (project_a, project_b):
                (project / ".git").mkdir(parents=True)
            project_skill = project_a / ".hermes/skills/caveman/SKILL.md"
            project_skill.parent.mkdir(parents=True)
            shared_body = (home / "skills/caveman/SKILL.md").read_text()
            project_body = shared_body + "\nProject A fixture marker.\n"
            project_skill.write_text(project_body)
            config["skills"]["trusted_project_dirs"] = [str(project_a)]
            (home / "config.yaml").write_text(yaml.safe_dump(config))
            self.enter(home)
            request = {"messages": [{"role": "user", "content": "Task"}]}
            with patch("tools.skills_tool.skill_view", wraps=skill_view) as reader:
                for project, expected in [(project_a, project_body), (project_b, shared_body),
                                          (project_a, project_body)]:
                    with patch("agent.runtime_cwd.resolve_agent_cwd", return_value=project):
                        restored = self.guard(request)
                        self.assertIn("SOURCE SKILL: caveman\n" + expected, restored["messages"][-1]["content"])
                        if project == project_b:
                            self.assertNotIn("Project A fixture marker", str(restored))
                        self.assertEqual(self.guard(restored), restored)
                self.assertEqual(reader.call_count, 3)

    def test_unqualified_api_modes_and_mismatched_shapes_are_unchanged(self):
        from unittest.mock import patch
        from agent.anthropic_adapter import build_anthropic_kwargs
        with tempfile.TemporaryDirectory(prefix="caveman-provider-") as temp:
            self.make_home(Path(temp))
            self.enter(Path(temp))
            anthropic = build_anthropic_kwargs(
                model="claude-sonnet-4-5", messages=[{"role": "user", "content": "Task"}],
                tools=None, max_tokens=128, reasoning_config=None,
            )
            chat = {"messages": [{"role": "user", "content": "Task"}]}
            cases = [("anthropic_messages", anthropic), ("bedrock_converse", chat),
                     ("unknown", chat), (None, chat), ("codex_responses", chat),
                     ("chat_completions", {"input": "Task"})]
            with patch("tools.skills_tool.skill_view", side_effect=AssertionError("must not load skill")):
                for api_mode, request in cases:
                    with self.subTest(api_mode=api_mode):
                        self.assertEqual(self.guard(request, api_mode=api_mode), request)


if __name__ == "__main__":
    unittest.main()
