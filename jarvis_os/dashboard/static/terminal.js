(function () {
  const container = document.getElementById("terminal");
  const statusEl = document.getElementById("terminal-status");
  const closeButton = document.getElementById("terminal-close");
  const fields = {
    model: document.getElementById("terminal-model"),
    tokensIn: document.getElementById("terminal-tokens-in"),
    tokensOut: document.getElementById("terminal-tokens-out"),
    context: document.getElementById("terminal-context"),
    cost: document.getElementById("terminal-cost"),
    elapsed: document.getElementById("terminal-elapsed"),
  };

  const term = new Terminal({
    cursorBlink: true,
    convertEol: true,
    fontFamily: '"SF Mono", "JetBrains Mono", "Fira Code", monospace',
    fontSize: 14,
    theme: {
      background: "#0f0f12",
      foreground: "#e8e6f0",
      cursor: "#e8e6f0",
      selectionBackground: "#7f77dd44",
      black: "#1a1a2e",
      red: "#e24b4a",
      green: "#1d9e75",
      yellow: "#ba7517",
      blue: "#378add",
      magenta: "#7f77dd",
      cyan: "#0f6e56",
      white: "#c0bfbb",
    },
  });
  const fit = new FitAddon.FitAddon();
  term.loadAddon(fit);
  term.open(container);
  fit.fit();

  let socket = null;
  let sessionId = null;

  function setStatus(status) {
    statusEl.textContent = status;
    statusEl.dataset.status = status;
  }

  function updateMetrics(metrics) {
    fields.model.textContent = metrics.model || container.dataset.defaultModel;
    fields.tokensIn.textContent = String(metrics.tokens_in || 0);
    fields.tokensOut.textContent = String(metrics.tokens_out || 0);
    fields.context.textContent = `${metrics.context_pct || 0}%`;
    fields.cost.textContent = `$${Number(metrics.cost_usd || 0).toFixed(2)}`;
    if (fields.elapsed) {
      fields.elapsed.textContent = `${Number(metrics.elapsed_s || 0).toFixed(1)}s`;
    }
  }

  function sendResize() {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ type: "resize", cols: term.cols, rows: term.rows }));
    }
  }

  async function createSession() {
    setStatus("starting");
    const response = await fetch("/api/terminal/sessions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        cwd: ".",
        model: container.dataset.defaultModel,
        load_vault_context: true,
      }),
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "No se pudo crear la sesión." }));
      throw new Error(error.detail || "No se pudo crear la sesión.");
    }
    return response.json();
  }

  function connect(session) {
    sessionId = session.session_id;
    updateMetrics(session.metrics);
    const protocol = window.location.protocol === "https:" ? "wss" : "ws";
    socket = new WebSocket(`${protocol}://${window.location.host}/ws/terminal/${sessionId}`);

    socket.addEventListener("open", function () {
      setStatus("active");
      sendResize();
    });

    socket.addEventListener("message", function (event) {
      const message = JSON.parse(event.data);
      if (message.type === "output") {
        term.write(message.data);
      } else if (message.type === "metrics") {
        updateMetrics(message);
      } else if (message.type === "status") {
        setStatus(message.status);
      } else if (message.type === "error") {
        term.writeln(`\r\n${message.message}`);
      }
    });

    socket.addEventListener("close", function () {
      setStatus("closed");
    });
  }

  term.onData(function (data) {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ type: "input", data: data }));
    }
  });

  closeButton.addEventListener("click", async function () {
    if (socket && socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ type: "close" }));
      socket.close();
    }
    if (sessionId) {
      await fetch(`/api/terminal/sessions/${sessionId}`, { method: "DELETE" }).catch(function () {});
    }
    setStatus("closed");
  });

  window.addEventListener("resize", function () {
    fit.fit();
    sendResize();
  });

  createSession()
    .then(connect)
    .catch(function (error) {
      setStatus("error");
      term.writeln(error.message);
    });
})();
