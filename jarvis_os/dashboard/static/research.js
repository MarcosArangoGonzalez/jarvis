(function () {
  const form = document.getElementById("research-form");
  const output = document.getElementById("research-output");
  if (!form || !output) return;

  form.addEventListener("submit", async function (event) {
    event.preventDefault();
    const data = new FormData(form);
    const payload = {
      query: String(data.get("query") || ""),
      backend: String(data.get("backend") || "perplexity"),
      model: String(data.get("model") || "sonar"),
      save_to_vault: data.get("save_to_vault") === "true",
    };
    output.textContent = "consultando...";
    try {
      const response = await fetch("/api/research/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const result = await response.json();
      if (!response.ok) {
        output.textContent = result.detail || "Error ejecutando research.";
        return;
      }
      const citations = result.citations && result.citations.length ? `\n\nCitations:\n${result.citations.map((item) => `- ${item}`).join("\n")}` : "";
      const vault = result.vault_path ? `\n\nVault: ${result.vault_path}` : "";
      const notice = result.notice ? `\n\nNotice: ${result.notice}` : "";
      output.textContent = `${result.answer}${citations}${vault}${notice}`;
    } catch (error) {
      output.textContent = error.message;
    }
  });
})();
