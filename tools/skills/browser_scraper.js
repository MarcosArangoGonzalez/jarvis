/*
JarvisOS browser rescue scraper.

Usage:
1. Start: python3 tools/skills/ingest_server.py
2. Open the target chat in the browser.
3. Paste this file into the browser console.
*/

(async function jarvisBrowserScraper() {
  const endpoint = "http://127.0.0.1:5000/ingest/browser";
  const selectors = [
    "[data-message-author-role]",
    "[data-testid*='conversation-turn']",
    "[class*='conversation'] [class*='message']",
    "article",
    "main [role='listitem']"
  ];

  function clean(text) {
    return (text || "").replace(/\s+/g, " ").trim();
  }

  function inferRole(node) {
    const explicit = node.getAttribute("data-message-author-role") || node.getAttribute("aria-label") || "";
    const text = explicit.toLowerCase();
    if (text.includes("user") || text.includes("you")) return "user";
    if (text.includes("assistant") || text.includes("model") || text.includes("gemini") || text.includes("claude")) return "assistant";
    return "unknown";
  }

  const seen = new Set();
  const messages = [];
  for (const selector of selectors) {
    for (const node of document.querySelectorAll(selector)) {
      const content = clean(node.innerText || node.textContent || "");
      if (!content || seen.has(content)) continue;
      seen.add(content);
      messages.push({
        role: inferRole(node),
        content,
        selector
      });
    }
    if (messages.length > 1) break;
  }

  const payload = {
    title: document.title || "Browser Chat Export",
    url: location.href,
    exported_at: new Date().toISOString(),
    user_agent: navigator.userAgent,
    messages,
    raw_text: messages.length ? null : clean(document.body.innerText || "")
  };

  const response = await fetch(endpoint, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  const result = await response.json();
  console.log("JarvisOS ingest result:", result);
  return result;
})();
