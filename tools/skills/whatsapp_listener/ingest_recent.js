/**
 * List or ingest selected recent video links from the configured WhatsApp chat.
 *
 * Examples:
 *   node ingest_recent.js --list --since today --limit 80
 *   node ingest_recent.js --select 1,3-5 --since today --limit 80
 */

import pkg from "whatsapp-web.js";
const { Client, LocalAuth } = pkg;
import { execFile } from "child_process";
import { fileURLToPath } from "url";
import path from "path";
import fs from "fs";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const JARVIS_ROOT = process.env.JARVIS_ROOT || path.resolve(__dirname, "../../..");
const PYTHON = process.env.PYTHON || "python3";
const ANALYZER = path.join(JARVIS_ROOT, "tools", "skills", "content_analyzer.py");
const TARGET_CHAT = process.env.JARVIS_WHATSAPP_CHAT_ID || "";

const URL_RE = /https?:\/\/[^\s<>"']+/gi;
const VIDEO_RE = /(youtube\.com|youtu\.be|instagram\.com\/(reel|p)\/)/i;

function parseArgs(argv) {
  const args = {
    list: false,
    select: "",
    since: "today",
    limit: 80,
    contains: "",
    model: process.env.JARVIS_DEFAULT_MODEL || "local:llama3.1",
  };
  for (let i = 2; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === "--list") args.list = true;
    else if (arg === "--select") args.select = argv[++i] || "";
    else if (arg === "--since") args.since = argv[++i] || "today";
    else if (arg === "--limit") args.limit = Number(argv[++i] || "80");
    else if (arg === "--contains") args.contains = argv[++i] || "";
    else if (arg === "--model") args.model = argv[++i] || args.model;
    else if (arg === "--help") {
      printHelp();
      process.exit(0);
    }
  }
  return args;
}

function printHelp() {
  console.log(`Usage:
  node ingest_recent.js --list [--since today|YYYY-MM-DD] [--limit N] [--contains text]
  node ingest_recent.js --select 1,3-5 [--since today|YYYY-MM-DD] [--limit N] [--contains text]
`);
}

function sinceTimestamp(value) {
  if (!value || value === "all") return 0;
  const now = new Date();
  if (value === "today") {
    return new Date(now.getFullYear(), now.getMonth(), now.getDate()).getTime() / 1000;
  }
  if (value === "yesterday") {
    return new Date(now.getFullYear(), now.getMonth(), now.getDate() - 1).getTime() / 1000;
  }
  const parsed = new Date(`${value}T00:00:00`);
  if (Number.isNaN(parsed.getTime())) {
    throw new Error(`Invalid --since value: ${value}`);
  }
  return parsed.getTime() / 1000;
}

function parseSelection(value, max) {
  const selected = new Set();
  for (const part of value.split(",").map((item) => item.trim()).filter(Boolean)) {
    const range = part.match(/^(\d+)-(\d+)$/);
    if (range) {
      const start = Number(range[1]);
      const end = Number(range[2]);
      for (let i = start; i <= end; i += 1) selected.add(i);
      continue;
    }
    selected.add(Number(part));
  }
  return [...selected].filter((item) => item >= 1 && item <= max).sort((a, b) => a - b);
}

function cleanUrl(url) {
  return url.replace(/[.,;)>]+$/, "");
}

function extractCandidates(messages, args) {
  const since = sinceTimestamp(args.since);
  const candidates = [];
  const seen = new Set();
  const contains = args.contains.toLowerCase();

  for (const msg of messages) {
    const body = msg.body || msg.caption || "";
    if (!body || (msg.timestamp || 0) < since) continue;
    if (contains && !body.toLowerCase().includes(contains)) continue;

    const urls = body.match(URL_RE) || [];
    for (const rawUrl of urls) {
      const url = cleanUrl(rawUrl);
      if (!VIDEO_RE.test(url) || seen.has(url)) continue;
      seen.add(url);
      candidates.push({
        url,
        body,
        timestamp: msg.timestamp || 0,
        fromMe: Boolean(msg.fromMe),
      });
    }
  }

  return candidates.sort((a, b) => a.timestamp - b.timestamp);
}

async function fetchRawMessages(client, chatId, limit) {
  return client.pupPage.evaluate(async ({ chatId, limit }) => {
    const wid = window.Store.WidFactory.createWid(chatId);
    let chat = window.Store.Chat.get(wid);
    if (!chat && window.Store.FindOrCreateChat?.findOrCreateLatestChat) {
      chat = (await window.Store.FindOrCreateChat.findOrCreateLatestChat(wid))?.chat;
    }
    if (!chat) return [];

    const toPlain = (msg) => ({
      body: msg.body || msg.caption || "",
      caption: msg.caption || "",
      timestamp: msg.t || 0,
      fromMe: Boolean(msg.id?.fromMe),
    });

    let msgs = chat.msgs?.getModelsArray?.() || [];
    while (msgs.length < limit && window.Store.ConversationMsgs?.loadEarlierMsgs) {
      const loaded = await window.Store.ConversationMsgs.loadEarlierMsgs(chat, chat.msgs);
      if (!loaded || !loaded.length) break;
      msgs = [...loaded, ...msgs];
    }

    return msgs
      .filter((msg) => !msg.isNotification)
      .sort((a, b) => (a.t || 0) - (b.t || 0))
      .slice(-limit)
      .map(toPlain);
  }, { chatId, limit });
}

function formatDate(timestamp) {
  return timestamp ? new Date(timestamp * 1000).toISOString().replace("T", " ").slice(0, 16) : "?";
}

function runAnalyzer(url, model) {
  return new Promise((resolve, reject) => {
    execFile(
      PYTHON,
      [ANALYZER, url, "--model", model, "--origin", "whatsapp"],
      { timeout: 120_000 },
      (err, stdout, stderr) => {
        if (err) {
          reject(new Error(stderr.slice(0, 300) || err.message));
        } else {
          try {
            resolve(JSON.parse(stdout.trim()));
          } catch {
            resolve({ status: "ok", output: "?", title: url });
          }
        }
      }
    );
  });
}

function waitForReady(client) {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error("Timed out waiting for WhatsApp client ready")), 60_000);
    client.once("ready", () => {
      clearTimeout(timer);
      resolve();
    });
    client.once("auth_failure", (message) => {
      clearTimeout(timer);
      reject(new Error(`WhatsApp auth failure: ${message}`));
    });
  });
}

async function main() {
  const args = parseArgs(process.argv);
  if (!TARGET_CHAT) {
    throw new Error("JARVIS_WHATSAPP_CHAT_ID must be set in .env or the environment.");
  }

  const client = new Client({
    authStrategy: new LocalAuth({ dataPath: path.join(__dirname, ".wwebjs_auth") }),
    puppeteer: {
      headless: true,
      args: ["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"],
    },
  });

  client.on("qr", () => {
    console.error("WhatsApp session is not authenticated. Start listener.js and scan the QR first.");
  });

  const ready = waitForReady(client);
  await client.initialize();
  await ready;
  const messages = await fetchRawMessages(client, TARGET_CHAT, args.limit);
  if (!messages.length) {
    throw new Error(`No messages found for WhatsApp chat: ${TARGET_CHAT}`);
  }
  const candidates = extractCandidates(messages, args);

  if (!args.select) {
    console.log(`Found ${candidates.length} video link(s).`);
    candidates.forEach((item, index) => {
      const direction = item.fromMe ? "me" : "them";
      console.log(`${String(index + 1).padStart(3, " ")}. ${formatDate(item.timestamp)} ${direction} ${item.url}`);
    });
    await client.destroy();
    return;
  }

  const selected = parseSelection(args.select, candidates.length);
  if (!selected.length) {
    console.log("No valid selections.");
    await client.destroy();
    return;
  }

  for (const index of selected) {
    const item = candidates[index - 1];
    process.stdout.write(`[${index}] ${item.url} `);
    try {
      const result = await runAnalyzer(item.url, args.model);
      console.log(`-> ${result.output || "?"}`);
    } catch (err) {
      console.log(`FAILED: ${err.message}`);
    }
  }

  await client.destroy();
}

main().catch((err) => {
  console.error(err.message || err);
  process.exit(1);
});
