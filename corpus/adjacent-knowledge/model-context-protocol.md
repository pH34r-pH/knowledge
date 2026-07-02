---
title: "Model Context Protocol (MCP): the agent–tool integration standard"
pillar: adjacent-knowledge
method: deep-research
date: 2026-07-01
sources: 9
confidence: high
---

## What it is

MCP is an open, JSON-RPC 2.0-based protocol for connecting AI applications to external data and tools. Anthropic announced it on November 25, 2024 to replace fragmented, per-data-source custom integrations; the initial release shipped pre-built servers for Google Drive, Slack, GitHub, Git, Postgres, and Puppeteer [2]. On December 9, 2025 it was donated to the Linux Foundation's Agentic AI Foundation (AAIF) — co-founded by Anthropic, Block, and OpenAI, backed by Google, Microsoft, AWS, Cloudflare, and Bloomberg — alongside Block's goose and OpenAI's AGENTS.md [8].

The mental model: MCP is a wire protocol that lets any host application discover and invoke tools exposed by any server, where the server — not the app — owns both the tool's schema and its execution. Everything below follows from that split, including the failure modes.

## When to reach for it

MCP is not a replacement for function-calling; it standardizes the transport and discovery layer *beneath* it [4].

Reach for plain **function-calling** when the tool is application-specific and single-client, when prototyping fast, on a latency-sensitive path, or when you're locked to one model provider anyway — the app already owns the schema and dispatch loop, so a protocol between them buys nothing [4]. Reach for **MCP** when the same tool must serve more than one client, when multi-model portability matters, or when governance — audit trails, rate limiting, access control — must live at a boundary the app doesn't own [4]. Most teams end up mixed: app-coupled tools stay function-calls, shared-infrastructure tools become MCP servers [4].

The organizing justification is the **N×M problem**: wiring M AI applications to N data sources bespoke means M×N integrations; a shared protocol collapses that to M+N — each app implements one client, each source one server. Prefect's concrete version of the same point [4]: three apps hitting a support-ticket database otherwise carry three copies of the schema, dispatch logic, and DB connection; one MCP server means one place to change.

## How it works

**Architecture: client–host–server, 1:1 connections.** An MCP *host* (the AI application — Claude Code, Claude Desktop, VS Code) creates one MCP *client* per server, each holding a dedicated 1:1 connection [1]. Local servers typically run over stdio and serve a single client; remote servers run over Streamable HTTP and serve many [1].

**Two layers.** MCP splits into a **data layer** — the JSON-RPC 2.0 protocol defining lifecycle, capability negotiation, and the primitives — and a **transport layer** handling connections, framing, and authorization [1]. The data layer is transport-agnostic — the same messages run over any transport [1].

**It's stateful, with lifecycle.** A session opens with the client sending `initialize` carrying `protocolVersion` (e.g. `2025-06-18`), `capabilities`, and `clientInfo`; the server replies with its capabilities and `serverInfo`; the client then sends `notifications/initialized` [1]. Capability negotiation determines which primitives and features (such as `listChanged`) are live for the session [1]. Stateful is the default, not an absolute — a subset of the protocol can run statelessly over Streamable HTTP, where session IDs are optional [1][3].

**Server primitives.** Servers expose **Tools** (executable functions the model can invoke), **Resources** (URI-addressed data for context), and **Prompts** (reusable interaction templates), each with discovery (`*/list`), retrieval (`*/get` or `resources/read`), and for tools execution (`tools/call`) [1]. The load-bearing detail is the **list-then-call** design: clients discover tools at runtime via `tools/list`, and changes propagate via `notifications/tools/list_changed` with no client code change [1][4]. This is exactly what distinguishes MCP from function-calling — where the app ships provider-specific tool schemas alongside the prompt and runs the dispatch loop itself, coupling schema to app and per-provider format [4].

**Client primitives — the reverse direction.** Servers can invoke capabilities *on the client*: **Sampling** (`sampling/createMessage`) lets a server request an LLM completion from the host without bundling its own model SDK, staying model-independent; **Elicitation** (`elicitation/create`) requests input or confirmation from the user; **Logging** sends log messages to the client [1].

**Transports — exactly two.** **stdio**: the client launches the server as a subprocess and exchanges newline-delimited JSON-RPC over stdin/stdout; the server MUST NOT write non-MCP content to stdout — a stray debug `print` corrupts the channel [3]. **Streamable HTTP**: a single endpoint supporting POST and GET; the client POSTs each message with an `Accept` header allowing both `application/json` and `text/event-stream`, and the server answers with a single JSON object or an SSE stream, with optional stateful sessions via an `Mcp-Session-Id` header [3]. Clients SHOULD support stdio whenever possible [3]. Streamable HTTP (protocol version 2025-03-26) replaced the deprecated two-endpoint HTTP+SSE transport from 2024-11-05 [3].

## Trade-offs

The spec's own security document enumerates the same attacks the critics publicize — an acknowledged, still-hardening surface, not a denied one [5][7]. The design choices that give MCP its leverage — dynamic discovery, mixing servers, OAuth proxying — are the ones that open it:

- **Confused deputy.** An MCP proxy using a static `client_id` to a third-party auth server, combined with dynamic client registration, lets a crafted link reuse an existing consent cookie: the auth server skips its consent screen and redirects the authorization code to an attacker `redirect_uri` [5]. Mitigations: per-client consent before forwarding, exact-match `redirect_uri` validation, single-use cryptographic `state` [5].
- **Token passthrough — forbidden.** Servers MUST NOT accept tokens not explicitly issued for the MCP server [5]. Forwarding a client's upstream token downstream collapses trust boundaries, bypasses rate-limiting and audience controls, breaks audit trails, and turns a stolen token into a data-exfiltration proxy [5].
- **SSRF via OAuth metadata.** A malicious server can return metadata URLs (`resource_metadata`, `authorization_servers`, `token_endpoint`) pointing at internal resources — e.g. the cloud metadata endpoint `http://169.254.169.254/` to exfiltrate IAM credentials [5]. Clients SHOULD enforce HTTPS, block private/reserved IP ranges, validate redirect targets, and use egress proxies; the spec warns against hand-rolled IP validation because of encoding tricks [5].
- **Session hijacking.** An attacker who obtains or guesses a session ID can impersonate a client or inject events into a shared queue the server relays [5]. Servers MUST verify all inbound requests, MUST NOT use sessions for authentication, MUST use non-deterministic session IDs, and SHOULD bind them to user identity (`<user_id>:<session_id>`) [5].
- **Local server compromise.** A local server is a downloaded binary running with the client's privileges, so a malicious startup command or payload is arbitrary code execution — the spec's example exfiltrates `~/.ssh/id_rsa` [5]. Clients supporting one-click config MUST show the exact command and get explicit consent, and SHOULD sandbox [5].

**Prompt injection through the tool layer.** Here the poison arrives as trusted protocol data — the model can't defend by being smart. **Tool poisoning**: descriptions are fed to the model but not normally shown to users, so malicious instructions hide there — Invariant Labs demonstrated a poisoned `add()` tool whose description told the model to read `~/.cursor/mcp.json` and exfiltrate it [7]. **Rug pulls** (Elena Cross): a tool mutates its own description after install — approved-safe on day 1, rerouting secrets by day 7 — and clients typically don't notify users when descriptions change [7]. **Cross-server shadowing**: a malicious server overrides or intercepts calls meant for a trusted one — in the WhatsApp-MCP example a fake tool redirected `send_message()` to steal chat history, hiding the exfiltration with whitespace obfuscation [7]. Willison called this combination — private data + untrusted instructions + an exfiltration vector in one agent — "toxic" in the MCP post [7], and later named it the **lethal trifecta** [9].

**Context and token cost.** Tool definitions occupy context, and at thousands of tools an agent may process hundreds of thousands of tokens before handling the request; intermediate results (a two-hour transcript, say) can add ~50,000 tokens as content passes through the model twice [6]. Anthropic's proposed fix presents MCP servers as code APIs called from a code-execution environment with on-demand tool loading (progressive disclosure), reporting a drop from 150,000 to 2,000 tokens — 98.7% [6]. Treat that as directional: one figure from Anthropic's own workflow, not independently reproduced. Nearly every MCP weakness is the flip side of a strength: runtime discovery enables rug pulls, multi-server hosting enables shadowing, descriptions-as-context enable poisoning, broad inventories enable the token blowup.

## In practice

At donation time: more than 10,000 active public MCP servers, over 75 connectors in Claude's directory, and 97M+ monthly SDK downloads across Python and TypeScript [8] — Anthropic's own unaudited figures, which don't separate production use from experimentation; momentum, not maturity.

Guidance that falls out of the mechanism:

- **The security model leans hard on client-side enforcement** — consent dialogs, SSRF blocking, sandboxing — and several critical mitigations are specced as SHOULD, not MUST [5]. Don't assume a host enforces what the spec merely recommends.
- **Audit tool descriptions, not just tool code.** Poisoning and rug pulls live in the description field users never see, so the reviewable artifact is the `tools/list` payload over time, not the server's source at install [7].
- **Reach for code-execution / progressive disclosure once tool counts or result sizes get large** [6] — but validate the savings on your own tool set rather than inheriting the 98.7% figure.
- **Some things aren't settled.** The Tasks primitive for durable execution is still marked Experimental in the architecture docs [1]; plan around the stable primitives.

## Further reading

1. Architecture overview — Model Context Protocol (official docs) — https://modelcontextprotocol.io/docs/learn/architecture
2. Introducing the Model Context Protocol — Anthropic (Nov 25, 2024) — https://www.anthropic.com/news/model-context-protocol
3. Transports — MCP Specification 2025-06-18 — https://modelcontextprotocol.io/specification/2025-06-18/basic/transports
4. MCP vs Function Calling: When to Use Which — Prefect (engineering writeup) — https://www.prefect.io/resources/mcp-vs-function-calling
5. Security Best Practices — MCP specification (current revision; the SSRF and local-server-compromise sections postdate the 2025-06-18 tag, whose URL redirects to the live document) — https://modelcontextprotocol.io/specification/2025-06-18/basic/security_best_practices
6. Code execution with MCP: building more efficient AI agents — Anthropic Engineering — https://www.anthropic.com/engineering/code-execution-with-mcp
7. Model Context Protocol has prompt injection security problems — Simon Willison (Apr 9, 2025) — https://simonwillison.net/2025/Apr/9/mcp-prompt-injection/
8. Donating the Model Context Protocol and establishing the Agentic AI Foundation — Anthropic (Dec 9, 2025) — https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation
9. The lethal trifecta for AI agents — Simon Willison (Jun 16, 2025) — https://simonwillison.net/2025/Jun/16/the-lethal-trifecta/
