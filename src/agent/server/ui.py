"""Single-page dark-mode dashboard interface template."""
from __future__ import annotations

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>AI Coding Agent Dashboard</title>
    <style>
        body {
            background-color: #121212;
            color: #e0e0e0;
            font-family: system-ui, sans-serif;
            margin: 0;
            display: flex;
            min-height: 100vh;
        }
        #sidebar {
            width: 320px;
            flex-shrink: 0;
            background-color: #1e1e1e;
            border-right: 1px solid #333;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 14px;
            box-sizing: border-box;
        }
        #main {
            flex: 1;
            min-width: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            overflow-y: auto;
        }
        h2, h3, h4 { margin: 0 0 8px; }
        .muted { color: #8b949e; font-size: 0.9em; }
        .state-pill {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            background-color: #444;
            font-weight: bold;
        }
        .state-active { background-color: #007acc; }
        .state-done { background-color: #238636; }
        .state-error { background-color: #dc3545; }
        #task-input {
            width: 100%;
            box-sizing: border-box;
            height: 90px;
            background: #0d1117;
            color: #e0e0e0;
            border: 1px solid #30363d;
            border-radius: 6px;
            padding: 10px;
            font-family: inherit;
            resize: vertical;
        }
        pre {
            background-color: #0d1117;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            border: 1px solid #30363d;
            white-space: pre-wrap;
            overflow-wrap: anywhere;
        }
        #feed {
            display: flex;
            flex-direction: column;
            gap: 6px;
            margin-bottom: 15px;
        }
        .entry {
            padding: 8px 12px;
            border-radius: 6px;
            background: #161b22;
            border-left: 3px solid #30363d;
        }
        .entry.plan { border-left-color: #58a6ff; white-space: pre-wrap; }
        .entry.tool { border-left-color: #2dd4bf; font-family: monospace; }
        .entry.eval-ok { border-left-color: #238636; }
        .entry.eval-bad { border-left-color: #d29922; }
        .entry.done { border-left-color: #238636; font-weight: bold; }
        .entry.err { border-left-color: #dc3545; }
        .btn {
            padding: 8px 16px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
        }
        .btn-run { background-color: #238636; color: white; width: 100%; }
        .btn-run:disabled { background-color: #30363d; cursor: not-allowed; }
        .btn-approve { background-color: #28a745; color: white; }
        .btn-deny { background-color: #dc3545; color: white; }
        #token-stats {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 10px;
            margin: 8px 0 12px;
        }
        .stat-card {
            background: #161b22;
            border: 1px solid #30363d;
            border-radius: 8px;
            padding: 12px;
            min-width: 0;
        }
        .stat-label { color: #8b949e; font-size: 0.8em; }
        .stat-value {
            font-size: clamp(1.1rem, 2vw, 1.6rem);
            font-weight: 700;
            margin-top: 4px;
            overflow-wrap: anywhere;
        }
        #speed-note { margin-bottom: 8px; }
        @media (max-width: 760px) {
            body { flex-direction: column; }
            #sidebar { width: 100%; border-right: 0; border-bottom: 1px solid #333; }
            #main { padding: 14px; }
            #token-stats { grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 6px; }
            .stat-card { padding: 8px; }
            .stat-label { font-size: 0.72em; }
        }
    </style>
</head>
<body>
    <div id="sidebar">
        <h3>AI Coding Agent</h3>
        <div class="muted">Workspace: <span id="workspace-path">-</span></div>
        <div class="muted">Model: <span id="model-name">-</span></div>
        <div>State: <span id="fsm-badge" class="state-pill">IDLE</span></div>
        <hr style="border-color:#30363d; width:100%;">
        <h4>New task</h4>
        <textarea id="task-input" placeholder="e.g. Create palindrome.py with is_palindrome(s) ignoring case and punctuation"></textarea>
        <button id="run-btn" class="btn btn-run" onclick="startRun()">Run task</button>
        <div class="muted" id="hint">Type a task and press Run — the agent plans, edits, tests, and reports back live.</div>
    </div>

    <div id="main">
        <h2>Active Task Execution</h2>
        <div id="approval-pane" style="display:none; background-color:#332222; padding:15px; border-radius:8px; border:1px solid #dc3545; margin-bottom:15px;">
            <p id="approval-text">Unsafe command execution request approval needed.</p>
            <button class="btn btn-approve" onclick="sendApproval(true)">Approve</button>
            <button class="btn btn-deny" onclick="sendApproval(false)">Deny</button>
        </div>

        <div id="feed"></div>

        <h4>Generation speed</h4>
        <div id="token-stats">
            <div class="stat-card">
                <div class="stat-label">Current speed</div>
                <div class="stat-value" id="current-speed">0 tok/s</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Average speed</div>
                <div class="stat-value" id="average-speed">0 tok/s</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Estimated tokens</div>
                <div class="stat-value" id="token-count">0</div>
            </div>
        </div>
        <div class="muted" id="speed-note">
            Waiting for generation. Live speed is estimated from received text
            (about 4 characters per token); it is not Ollama's exact token count.
        </div>
        <h4>Model Token Stream Output:</h4>
        <pre id="token-pane">Stream waiting to start...</pre>
    </div>

    <script>
        const _token = new URLSearchParams(window.location.search).get("token");
        const _proto = window.location.protocol === "https:" ? "wss" : "ws";
        const _q = _token ? ("?token=" + encodeURIComponent(_token)) : "";
        const ws = new WebSocket(`${_proto}://${window.location.host}/ws${_q}`);
        let currentApprovalId = null;

        let streamStartedAt = 0;
        let receivedChars = 0;
        let tokenSamples = [];
        let streamActive = false;

        function formatNumber(value) {
            return Math.max(0, value).toLocaleString(undefined, {
                maximumFractionDigits: 1
            });
        }

        function resetTokenStats() {
            streamStartedAt = 0;
            receivedChars = 0;
            tokenSamples = [];
            streamActive = true;
            document.getElementById("current-speed").innerText = "0 tok/s";
            document.getElementById("average-speed").innerText = "0 tok/s";
            document.getElementById("token-count").innerText = "0";
            document.getElementById("speed-note").innerText =
                "Live estimate: about 4 characters per token. Exact Ollama token statistics are reported after each model call.";
        }

        function recordText(text) {
            const now = performance.now();
            if (!streamStartedAt) streamStartedAt = now;
            const chars = text.length;
            receivedChars += chars;
            tokenSamples.push({time: now, chars: chars});

            const cutoff = now - 3000;
            while (tokenSamples.length && tokenSamples[0].time < cutoff) {
                tokenSamples.shift();
            }

            document.getElementById("token-count").innerText =
                formatNumber(receivedChars / 4);
            updateTokenStats();
        }

        function updateTokenStats() {
            const now = performance.now();
            if (!streamStartedAt || !receivedChars) return;

            const elapsedSeconds = Math.max((now - streamStartedAt) / 1000, 0.001);
            const average = (receivedChars / 4) / elapsedSeconds;

            const windowMs = Math.min(2000, now - streamStartedAt);
            const cutoff = now - windowMs;
            let recentChars = 0;
            for (const sample of tokenSamples) {
                if (sample.time >= cutoff) recentChars += sample.chars;
            }
            const current = windowMs > 0
                ? (recentChars / 4) / (windowMs / 1000)
                : 0;

            document.getElementById("current-speed").innerText =
                formatNumber(current) + " tok/s";
            document.getElementById("average-speed").innerText =
                formatNumber(average) + " tok/s";
        }

        setInterval(() => {
            if (streamActive) updateTokenStats();
        }, 500);

        function addEntry(cls, text) {
            const feed = document.getElementById("feed");
            const div = document.createElement("div");
            div.className = "entry " + cls;
            div.innerText = text;
            feed.appendChild(div);
        }

        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);

            if (data.event === "connected") {
                document.getElementById("workspace-path").innerText = data.config.workspace;
                document.getElementById("model-name").innerText = data.config.model;
            }

            else if (data.event === "state_changed") {
                const badge = document.getElementById("fsm-badge");
                badge.innerText = data.state.toUpperCase();
                badge.className = "state-pill" + (data.state === "executing" ? " state-active" : "");
            }

            else if (data.event === "token") {
                const pane = document.getElementById("token-pane");
                if (pane.innerText === "Stream waiting to start...") pane.innerText = "";
                pane.innerText += data.text;
                recordText(data.text || "");
            }

            else if (data.event === "approval_required") {
                currentApprovalId = data.id;
                document.getElementById("approval-text").innerText =
                    `Approve Action: ${data.action} - ${data.detail}`;
                document.getElementById("approval-pane").style.display = "block";
            }

            else if (data.event === "run_started") {
                document.getElementById("feed").innerHTML = "";
                document.getElementById("token-pane").innerText = "Stream waiting to start...";
                resetTokenStats();
                addEntry("plan", "▶ Task: " + data.task);
            }
            else if (data.event === "plan") {
                addEntry("plan", "Plan:\\n" + data.text);
            }
            else if (data.event === "tool_call") {
                addEntry("tool", "→ " + data.tool + "  " + JSON.stringify(data.args));
            }
            else if (data.event === "tool_result") {
                addEntry("tool", "   " + (data.ok ? "ok" : "failed") + " · " + (data.content || "").slice(0, 200));
            }
            else if (data.event === "evaluation") {
                addEntry(data.passed ? "eval-ok" : "eval-bad",
                    (data.passed ? "✔ Evaluation passed — " : "✘ Evaluation failed — ") + data.summary);
            }
            else if (data.event === "no_progress") {
                addEntry("eval-bad", "↻ Repeated " + data.tool
                    + " with no progress — stopping this phase and evaluating.");
            }
            else if (data.event === "give_up") {
                addEntry("eval-bad", "■ Retry budget exhausted after " + data.retries
                    + (data.retries === 1 ? " retry" : " retries")
                    + ". Stopping instead of looping."
                    + (data.summary ? "\\n" + data.summary : ""));
            }
            else if (data.event === "run_finished") {
                streamActive = false;
                updateTokenStats();

                const s = data.stats || {};
                if (typeof s.tokens_per_second === "number" && s.tokens_per_second > 0) {
                    document.getElementById("speed-note").innerText =
                        "Run finished. Ollama-reported average across model calls: "
                        + formatNumber(s.tokens_per_second) + " tok/s. Live figures above were estimates.";
                } else {
                    document.getElementById("speed-note").innerText =
                        "Run finished. Live figures above are estimates from received text, not exact token counts.";
                }

                addEntry("done", "● Session ended: " + data.final_state.toUpperCase()
                    + (s.total_tokens ? ("   ·   " + s.model_calls + " model calls · "
                       + s.total_tokens + " tokens · " + (s.total_seconds || 0).toFixed(1) + "s · $0.00") : ""));
                const badge = document.getElementById("fsm-badge");
                badge.className = "state-pill " + (data.final_state === "done" ? "state-done" : "state-error");
                document.getElementById("run-btn").disabled = false;
                document.getElementById("run-btn").innerText = "Run task";
            }
            else if (data.event === "error") {
                streamActive = false;
                addEntry("err", "Error: " + data.message);
                document.getElementById("run-btn").disabled = false;
                document.getElementById("run-btn").innerText = "Run task";
            }
        };

        ws.onerror = function() {
            addEntry("err", "WebSocket connection error.");
        };

        function startRun() {
            const task = document.getElementById("task-input").value.trim();
            if (!task) { alert("Please type a task first."); return; }
            const btn = document.getElementById("run-btn");
            btn.disabled = true;
            btn.innerText = "Running…";
            ws.send(JSON.stringify({"type": "run", "task": task, "options": {}}));
        }

        function sendApproval(approved) {
            ws.send(JSON.stringify({
                "type": "approval",
                "id": currentApprovalId,
                "approved": approved
            }));
            document.getElementById("approval-pane").style.display = "none";
        }
    </script>
</body>
</html>
"""
