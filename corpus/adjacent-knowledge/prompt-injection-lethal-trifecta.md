---
title: Prompt injection and the lethal trifecta
pillar: adjacent-knowledge
method: deep-research
date: 2026-07-01
sources: 7
confidence: high
---

## What it is

Prompt injection is what happens when text an LLM merely reads gets treated as instructions it should obey. The context window is a flat sequence of tokens; the model has no architecturally enforced way to tell "trusted instruction from the operator" apart from "attacker-controlled data I retrieved." When an LLM-integrated application pulls a web page, email, document, or tool output into context, the boundary between data and instructions blurs, and text from the data half executes as if it were an instruction [2]. Willison's compression of the point: models "are unable to reliably distinguish the importance of instructions based on where they came from" [1].

This is not a bug with a patch waiting on the other side; it is a direct consequence of how instruction-following LLMs work. The *indirect* variant — where the attacker never talks to the model but plants instructions in content it will later retrieve — was formalized and demonstrated against real systems (Bing's GPT-4 Chat, code-completion engines) by Greshake et al. in 2023, with a taxonomy of harms spanning data theft, self-propagating "worm" prompts, and information-ecosystem contamination. Their verdict at the time: "effective mitigations of these emerging threats are currently lacking" [2]. Two years of guardrail engineering later, OWASP's LLM01:2025 concedes the same in plainer words: "it is unclear if there are fool-proof methods of prevention for prompt injection" [5].

Willison's "lethal trifecta" is the threat model that makes this actionable. An agent is exploitable precisely when it simultaneously has all three of: (1) access to private data, (2) exposure to untrusted content, and (3) an external-communication channel it can use to exfiltrate. Hold any two and you are safe; grant all three in one session and an attacker who controls the untrusted content can read the private data and ship it out — no exploit code, no memory corruption, just English [1].

## When to reach for it

This is a lens you apply during agent design, not a library you install. The moment you wire an LLM to tools — retrieval over private documents, an email or calendar connector, a browser, anything that reads external content or takes consequential action — audit for the trifecta. Three questions: does this agent touch data an attacker would want? does it ingest content an attacker can author? can it send anything outward? Three yeses inside one trust boundary is a latent EchoLeak (below), and no amount of prompt engineering closes it.

The useful discipline is that removing *any one* leg neutralizes the whole class for that surface. An agent reading untrusted web pages with an external API but no access to secrets is fine; an agent over private data with egress but no untrusted input is fine. The framing tells you *which* leg is cheapest to cut for a given feature — often egress, via allowlisting — rather than chasing the impossible goal of an injection-proof model [1].

## How it works

The load-bearing insight is where enforcement must live. Because the model cannot be made to reliably resist injection, any control that depends on the model *deciding* correctly is unsound as a security boundary — which demotes detection-based guardrails to defense-in-depth, never the boundary itself.

**Why detection is structurally insufficient.** A classifier that catches "95% of attacks" is a failing grade in a security context. The attacker is not sampling randomly; they iterate until one payload evades the filter, and the non-deterministic model gives no guarantee about the next attempt [1]. This is the mindset shift from ML evaluation, where 95% is excellent, to security, where the adversary controls the input distribution and only needs to win once.

**Move enforcement out of the model and into the runtime.** The credible direction is deterministic controls that constrain what the agent can *do* with tainted data, regardless of what the model "decides." CaMeL (Google DeepMind, Debenedetti et al.) is the sharpest instance, porting operating-system security concepts — Control Flow Integrity, access control, information-flow control — to agent runtimes [3]:

- A **privileged LLM (P-LLM)** sees only the trusted user query and emits a plan as Python-like code; it never reads untrusted data.
- A **quarantined LLM (Q-LLM)** parses untrusted content into structured values but has no tool access.
- Every value carries a **capability** that taint-tracks its provenance and permitted uses.
- A **custom interpreter** runs the plan and checks security policies before every tool call.

The property this buys is categorical: because control flow and data flow are extracted from the *trusted* query, "the untrusted data retrieved by the LLM can never impact the program flow" [3]. An injected instruction in a retrieved email cannot redirect the plan — the plan was fixed before the email was read, and the interpreter, not the model, decides whether a tool call is allowed.

**The Dual-LLM pattern is the building block.** CaMeL's split predates it: Willison's 2023 Dual-LLM design has a privileged LLM that plans and holds the tools, and a quarantined LLM that processes untrusted content and returns only *symbolic variables* the privileged LLM manipulates without reading their tainted contents [4]. CaMeL generalizes this with capabilities and a policy-checking interpreter.

**The invariant, stated generally.** The design-patterns literature (Beurer-Kellner et al., summarized by Willison) abstracts six patterns — Action-Selector, Plan-Then-Execute, LLM Map-Reduce, Dual-LLM, Code-Then-Execute, Context-Minimization — around one rule: "once an LLM agent has ingested untrusted input, it must be constrained so that it is impossible for that input to trigger any consequential actions" [4]. Each pattern enforces that structurally, and each pays by limiting the agent's ability to do arbitrary open-ended tasks.

## Trade-offs

**The utility cost is real but not catastrophic.** On AgentDojo, CaMeL "solv[es] 77% of tasks with provable security (compared to 84% with an undefended system)" [3]. Read carefully: 77% and 84% are *task utility*, not attack rates. (An intermediate summarizer garbled this into a "77.8% attack success rate" — wrong, and exactly the recent-topic fabrication risk worth naming.) Deterministic non-exfiltration guarantees cost roughly seven points of task completion here — a bargain against a CVSS 9.3 exfiltration, but a price, and it will be higher on agents whose value *is* open-ended autonomy.

**Runtime enforcement does not solve everything.** CaMeL explicitly cannot defend against attacks with no data-flow consequence — "text-to-text attacks which have no consequences on the data flow," such as an injection that makes the model summarize an email misleadingly, or induces phishing content [3]. If the harm is the text itself rather than an exfiltrating action, taint-tracking has nothing to grab. CaMeL also still needs a human in the loop for ambiguous data flows and *developer-authored* security policies — where the approach's scalability is most in doubt.

**A framing tension worth surfacing.** The primary research (Willison, CaMeL) treats runtime constraint as the real fix and is openly skeptical of classifiers. OWASP LLM01 is more permissive, listing input/output filtering and adversarial testing alongside least-privilege and human approval [5]. Reconcile these by treating runtime enforcement — least-privilege tool access, egress allowlisting, capability checks — as the load-bearing boundary, with detection as defense-in-depth that reduces attempt volume. OWASP's own controls are framed as risk reduction, not elimination [5], consistent with that ranking.

## In practice

EchoLeak (CVE-2025-32711, CVSS 9.3, disclosed by Aim Security in June 2025) is the trifecta made concrete against a shipping product: the first real-world *zero-click* prompt-injection exploit in a production LLM system, where a single crafted email caused Microsoft 365 Copilot to exfiltrate private tenant data with no user interaction [6][7].

What makes it instructive is that Copilot already had model-side guardrails, and the chain walked through all of them [6]:

1. **Bypass the injection classifier.** Microsoft's XPIA (cross-prompt-injection) classifier was evaded with benign-sounding phrasing — the 95%-catch problem, live.
2. **Bypass link/image redaction.** The attacker used *reference-style* Markdown to slip an image URL past Copilot's redaction.
3. **Exfiltrate through an allowlisted proxy.** The final hop rode a Microsoft Teams image proxy the Content-Security-Policy already trusted; the proxy fetched the attacker's URL with the secrets embedded in it.

Markdown image auto-fetch is the canonical exfiltration leg: instruct the model to emit an image whose URL encodes the stolen data, and the client renders — fetches — it with no click, which is why "external communication" includes seemingly passive rendering channels [1][6]. Every layer EchoLeak defeated was a detection or redaction control, each individually bypassable — the whole argument for enforcement at the egress/runtime layer instead.

The practical takeaway: identify the trifecta early, cut a leg (usually egress, via strict default-deny allowlisting), and if you must keep all three, put a CaMeL-style capability/policy layer between the model's plan and its tool calls so the *runtime*, not the model, decides what leaves the boundary [3]. Treat classifiers as attempt-reducers, not the wall.

## Further reading

1. The lethal trifecta for AI agents: private data, untrusted content, and external communication — Simon Willison — https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/
2. Not what you've signed up for: Compromising Real-World LLM-Integrated Applications with Indirect Prompt Injection (Greshake et al., 2023) — https://arxiv.org/abs/2302.12173
3. Defeating Prompt Injections by Design (CaMeL) — Debenedetti et al., Google DeepMind, 2025 — https://arxiv.org/abs/2503.18813
4. Design Patterns for Securing LLM Agents against Prompt Injections (summary of Beurer-Kellner et al.) — Simon Willison — https://simonwillison.net/2025/Jun/13/prompt-injection-design-patterns/
5. LLM01:2025 Prompt Injection — OWASP Gen AI Security Project — https://genai.owasp.org/llmrisk/llm01-prompt-injection/
6. EchoLeak: The First Real-World Zero-Click Prompt Injection Exploit in a Production LLM System (Reddy, Gujral, 2025) — https://arxiv.org/html/2509.10540v1
7. Zero-Click AI Vulnerability Exposes Microsoft 365 Copilot Data Without User Interaction (CVE-2025-32711, CVSS 9.3) — The Hacker News — https://thehackernews.com/2025/06/zero-click-ai-vulnerability-exposes.html
