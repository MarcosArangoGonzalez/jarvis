(function () {
  const form = document.getElementById("newsletter-form");
  const output = document.getElementById("newsletter-output");
  if (!form || !output) return;

  form.addEventListener("submit", async function (event) {
    event.preventDefault();
    const data = new FormData(form);
    const sections = String(data.get("sections") || "").split(",").map((item) => item.trim()).filter(Boolean);
    const payload = {
      date: String(data.get("date") || "") || null,
      sections: sections.length ? sections : null,
      export_pdf: data.get("export_pdf") === "true",
    };
    output.textContent = "generando...";
    try {
      const response = await fetch("/api/newsletter/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const result = await response.json();
      if (!response.ok) {
        output.textContent = result.detail || "No se pudo generar.";
        return;
      }
      output.textContent = `Newsletter ${result.date}
Items: ${result.items_total}
MD: ${result.md_path}
HTML: ${result.html_path}
PDF: ${result.pdf_path || "no generado"}`;
    } catch (error) {
      output.textContent = error.message;
    }
  });
})();
