# Hermes integration

`caveman-communication` 1.1.1 supplies a profile-wide mode receipt through `pre_llm_call` and missing-rule recovery through `llm_request`. Native `skills.auto_load` normally supplies the full skill first.

A single cached body follows the native trusted-project lookup scope. Native global/platform disablement is rechecked independently. Recovery is limited to explicit Chat Completions and Codex Responses modes; unsupported formats remain unchanged.

Mode commands change the profile, not a single conversation. Input text, tool payloads, and stored history are preserved. There is no second model, proxy, output filter, or Hermes core patch.

See the [root README](../../README.md) and [licensing](../../LICENSING.md). Source preparation does not install or reload a gateway, and instruction delivery does not guarantee model adherence.
