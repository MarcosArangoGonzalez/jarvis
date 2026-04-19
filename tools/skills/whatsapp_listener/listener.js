/**
 * Jarvis WhatsApp real-time listener (whatsapp-web.js).
 *
 * Setup (once):
 *   npm install
 *   node listener.js   → scan QR with WhatsApp → session persisted in .wwebjs_auth/
 *
 * Env vars:
 *   JARVIS_WHATSAPP_CHAT_ID   e.g. "34647001054@c.us"  (filter to this chat only)
 *   JARVIS_ROOT               override root path (default: ../../..)
 */

import pkg from "whatsapp-web.js";
const { Client, LocalAuth } = pkg;
import qrcode from "qrcode-terminal";
import { execFile } from "child_process";
import { fileURLToPath } from "url";
import path from "path";
import fs from "fs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const JARVIS_ROOT = process.env.JARVIS_ROOT || path.resolve(__dirname, "../../..");
const RAW_QUEUE = path.join(JARVIS_ROOT, "raw", "ingest_queue");
const PYTHON = process.env.PYTHON || "python3";
const ANALYZER = path.join(JARVIS_ROOT, "tools", "skills", "content_analyzer.py");
const TARGET_CHAT = process.env.JARVIS_WHATSAPP_CHAT_ID || "";

const URL_RE = /https?:\/\/[^\s]+/i;

function stamp() {
  return new Date().toISOString().replace(/[:.]/g, "-").replace("T", "T").slice(0, 19);
}

function detectType(text) {
  if (/youtube\.com|youtu\.be/i.test(text)) return "youtube";
  if (/instagram\.com/i.test(text)) return "instagram";
  if (/github\.com\/[^/]+\/[^/]+/i.test(text)) return "github";
  if (URL_RE.test(text)) return "url";
  return "text";
}

function enqueue(text, type) {
  fs.mkdirSync(RAW_QUEUE, { recursive: true });
  const file = path.join(RAW_QUEUE, `${stamp()}-whatsapp-${type}.txt`);
  fs.writeFileSync(file, text, "utf-8");
  return file;
}

function runAnalyzer(urlOrPath, model = "local:llama3.1") {
  return new Promise((resolve, reject) => {
    execFile(
      PYTHON,
      [ANALYZER, urlOrPath, "--model", model],
      { timeout: 120_000 },
      (err, stdout, stderr) => {
        if (err) {
          reject(new Error(stderr.slice(0, 300) || err.message));
        } else {
          try {
            resolve(JSON.parse(stdout.trim()));
          } catch {
            resolve({ status: "ok", output: "?", title: urlOrPath });
          }
        }
      }
    );
  });
}

async function handleMessage(msg) {
  const text = msg.body?.trim() || "";
  if (!text) return;

  const type = detectType(text);
  const urlMatch = text.match(URL_RE);
  const url = urlMatch ? urlMatch[0].replace(/[.,;)>]+$/, "") : null;

  console.log(`[${new Date().toISOString()}] ${type}: ${text.slice(0, 80)}`);

  if (url) {
    // Analyze immediately with content_analyzer
    try {
      const result = await runAnalyzer(url);
      const noteName = result.output ? path.basename(result.output) : "?";
      const reply = `✓ Nota creada: ${noteName}\n📝 ${result.summary || result.title || url}`;
      await msg.reply(reply);
    } catch (err) {
      // Fallback: enqueue for sync_watcher
      enqueue(url, type);
      await msg.reply(`⚠️ En cola para procesamiento: ${type}`);
      console.error("Analyzer error:", err.message);
    }
  } else {
    // Plain text: drop to queue
    enqueue(text, "text");
    await msg.reply("✓ Texto recibido. Guardando en wiki...");
  }
}

// ── Client setup ──────────────────────────────────────────────────────────────

const client = new Client({
  authStrategy: new LocalAuth({ dataPath: path.join(__dirname, ".wwebjs_auth") }),
  puppeteer: {
    headless: true,
    args: ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
  },
});

client.on("qr", (qr) => {
  console.log("\nScan this QR code with WhatsApp:\n");
  qrcode.generate(qr, { small: true });
  console.log("\nWaiting for scan...\n");
});

client.on("authenticated", () => {
  console.log("✓ Authenticated. Session saved.");
});

client.on("auth_failure", (msg) => {
  console.error("✗ Auth failure:", msg);
  process.exit(1);
});

client.on("ready", () => {
  console.log("✓ WhatsApp client ready.");
  if (TARGET_CHAT) {
    console.log(`  Listening on chat: ${TARGET_CHAT}`);
  } else {
    console.log("  JARVIS_WHATSAPP_CHAT_ID not set — processing messages from ALL chats.");
  }
});

client.on("message", async (msg) => {
  // Skip group messages and status updates
  if (msg.from === "status@broadcast") return;
  if (msg.isGroupMsg) return;

  // Filter to target chat if configured
  if (TARGET_CHAT && msg.from !== TARGET_CHAT) return;

  try {
    await handleMessage(msg);
  } catch (err) {
    console.error("Message handler error:", err);
  }
});

client.on("disconnected", (reason) => {
  console.warn("Disconnected:", reason);
  process.exit(0);
});

console.log("Starting Jarvis WhatsApp listener...");
client.initialize();
