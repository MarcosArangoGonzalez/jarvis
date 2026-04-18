#!/usr/bin/env python3
"""Jarvis storage manager — local cleanup, Docker, and cloud deployment uploads.

Commands:
  scan      Local scan: disk usage, large files, duplicates, stale raw/
  docker    Docker disk usage + cleanup options
  cloud     Check Google Drive + GitHub storage quotas
  push      Push Docker image to ghcr.io or Docker Hub, optionally remove locally
  upload    Upload model/artifact to Hugging Face Hub or GCS
  clean     Remove local garbage (--dry-run by default, --yes to execute)
  full      scan + docker + cloud

Examples:
  python3 storage_manager.py scan
  python3 storage_manager.py docker --clean
  python3 storage_manager.py docker --clean --all-images --yes
  python3 storage_manager.py push myimage:latest --registry ghcr.io --remove
  python3 storage_manager.py upload ./model.gguf --dest hf --repo user/models
  python3 storage_manager.py upload ./artifact/ --dest gcs --bucket my-bucket
  python3 storage_manager.py clean --yes
  python3 storage_manager.py full
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
HOME = Path.home()

W = 58
S = "─" * W


def human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def dir_size(path: Path) -> int:
    total = 0
    try:
        for e in path.rglob("*"):
            if e.is_file(follow_symlinks=False):
                try:
                    total += e.stat().st_size
                except OSError:
                    pass
    except (PermissionError, OSError):
        pass
    return total


def file_hash(path: Path) -> str:
    h = hashlib.md5()
    try:
        with path.open("rb") as f:
            while block := f.read(65536):
                h.update(block)
    except OSError:
        return ""
    return h.hexdigest()


def days_old(path: Path) -> float:
    try:
        return (datetime.now(timezone.utc).timestamp() - path.stat().st_mtime) / 86400
    except OSError:
        return 0.0


def run(cmd: list[str], timeout: int = 30) -> tuple[int, str, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except FileNotFoundError:
        return 1, "", f"{cmd[0]}: not found"
    except subprocess.TimeoutExpired:
        return 1, "", "timeout"


# ── Patterns ──────────────────────────────────────────────────────────────────

WIPE_DIRS = ["__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", "dist", "build", ".eggs"]
WIPE_GLOBS = ["**/*.pyc", "**/*.pyo", "**/.DS_Store", "**/*.tmp", "**/*.swp", "**/npm-debug.log*"]
STALE_DIRS = {ROOT / "raw" / "ingest_queue": 3, ROOT / "raw" / "chats": 30, ROOT / "raw" / "news": 14}
CACHE_DIRS = [HOME / ".cache" / "yt-dlp", HOME / ".cache" / "pip", HOME / ".local" / "share" / "Trash"]
SKIP = {".git", "node_modules", ".wwebjs_auth", ".wwebjs_cache", ".ollama"}


# ── Local scan ────────────────────────────────────────────────────────────────

@dataclass
class ScanResult:
    disk_usage: dict[str, int] = field(default_factory=dict)
    large_files: list[dict] = field(default_factory=list)
    duplicates: list[list[str]] = field(default_factory=list)
    garbage_files: list[dict] = field(default_factory=list)
    stale_raw: list[dict] = field(default_factory=list)
    cache_usage: dict[str, int] = field(default_factory=dict)
    total_reclaimable: int = 0


def local_scan(scope: Path, min_size_mb: int = 10) -> ScanResult:
    r = ScanResult()
    min_bytes = min_size_mb * 1024 * 1024

    # disk usage by top-level dir
    try:
        for child in sorted(scope.iterdir()):
            if child.is_dir(follow_symlinks=False) and not child.name.startswith("."):
                rel = str(child.relative_to(HOME) if scope == HOME else child.relative_to(scope))
                r.disk_usage[rel] = dir_size(child)
        r.disk_usage = dict(sorted(r.disk_usage.items(), key=lambda x: -x[1])[:20])
    except (PermissionError, OSError):
        pass

    # large files
    try:
        for p in scope.rglob("*"):
            if not p.is_file(follow_symlinks=False):
                continue
            if any(part in SKIP for part in p.parts):
                continue
            try:
                sz = p.stat().st_size
                if sz >= min_bytes:
                    r.large_files.append({"path": str(p), "size": sz, "days_old": round(days_old(p), 1)})
            except OSError:
                pass
    except (PermissionError, OSError):
        pass
    r.large_files = sorted(r.large_files, key=lambda x: -x["size"])[:30]

    # duplicates (by hash, files ≥100KB)
    by_size: dict[int, list[Path]] = defaultdict(list)
    try:
        for p in scope.rglob("*"):
            if not p.is_file(follow_symlinks=False):
                continue
            if any(part in SKIP for part in p.parts):
                continue
            try:
                sz = p.stat().st_size
                if sz >= 102400:
                    by_size[sz].append(p)
            except OSError:
                pass
    except (PermissionError, OSError):
        pass
    for paths in by_size.values():
        if len(paths) < 2:
            continue
        by_hash: dict[str, list[str]] = defaultdict(list)
        for p in paths:
            h = file_hash(p)
            if h:
                by_hash[h].append(str(p))
        for plist in by_hash.values():
            if len(plist) > 1:
                r.duplicates.append(sorted(plist))
    r.duplicates = r.duplicates[:20]

    # garbage
    for glob in WIPE_GLOBS:
        try:
            for p in scope.glob(glob):
                if p.is_file():
                    try:
                        r.garbage_files.append({"path": str(p), "size": p.stat().st_size, "reason": "temp file"})
                    except OSError:
                        pass
        except Exception:
            pass
    for d in WIPE_DIRS:
        try:
            for p in scope.glob(f"**/{d}"):
                if p.is_dir():
                    r.garbage_files.append({"path": str(p), "size": dir_size(p), "reason": "build dir", "is_dir": True})
        except Exception:
            pass
    r.garbage_files = sorted(r.garbage_files, key=lambda x: -x["size"])[:50]

    # stale raw/
    for raw_dir, max_days in STALE_DIRS.items():
        if not raw_dir.exists():
            continue
        for p in raw_dir.iterdir():
            if p.is_file():
                age = days_old(p)
                if age > max_days:
                    try:
                        r.stale_raw.append({"path": str(p.relative_to(ROOT)), "size": p.stat().st_size,
                                            "days_old": round(age, 1), "reason": f"unprocessed >{max_days}d"})
                    except OSError:
                        pass
    r.stale_raw = sorted(r.stale_raw, key=lambda x: -x["days_old"])

    # caches
    for d in CACHE_DIRS:
        if d.exists():
            r.cache_usage[str(d)] = dir_size(d)

    r.total_reclaimable = (sum(f["size"] for f in r.garbage_files)
                           + sum(f["size"] for f in r.stale_raw)
                           + sum(r.cache_usage.values()))
    return r


# ── Docker ────────────────────────────────────────────────────────────────────

def docker_available() -> bool:
    return run(["docker", "info"], timeout=5)[0] == 0


def docker_df() -> dict[str, Any]:
    if not docker_available():
        return {"status": "error", "detail": "Docker not running or not installed"}
    _, out, _ = run(["docker", "system", "df", "--format", "{{json .}}"])
    rows = []
    for line in out.splitlines():
        try:
            rows.append(json.loads(line.strip()))
        except Exception:
            pass
    _, images, _ = run(["docker", "images", "--format", "{{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}"])
    return {"status": "ok", "summary": rows, "images": images[:2000]}


def docker_clean(volumes: bool = False, build_cache: bool = True,
                 all_images: bool = False, execute: bool = False) -> dict[str, Any]:
    if not docker_available():
        return {"status": "error", "detail": "Docker not running"}
    cmds = [
        ["docker", "container", "prune", "-f"],
        ["docker", "image", "prune"] + (["-a"] if all_images else []) + ["-f"],
        ["docker", "network", "prune", "-f"],
    ]
    if volumes:
        cmds.append(["docker", "volume", "prune", "-f"])
    if build_cache:
        cmds.append(["docker", "builder", "prune", "-f"])
    if not execute:
        _, current, _ = run(["docker", "system", "df"])
        return {"dry_run": True, "current_usage": current, "would_run": [" ".join(c) for c in cmds]}
    results = []
    for cmd in cmds:
        rc, out, err = run(cmd, timeout=120)
        results.append({"cmd": " ".join(cmd), "ok": rc == 0, "output": (out or err)[:150]})
    return {"dry_run": False, "actions": results}


def docker_push_and_remove(image: str, registry: str = "ghcr.io",
                            namespace: str | None = None, remove_after: bool = False) -> dict[str, Any]:
    if not docker_available():
        return {"status": "error", "detail": "Docker not running"}
    ns = namespace or os.environ.get("GITHUB_USERNAME", "")
    if not ns and registry == "ghcr.io":
        rc, out, _ = run(["gh", "api", "user", "--jq", ".login"])
        ns = out if rc == 0 else ""
    name = image.split("/")[-1].split(":")[0]
    tag = image.split(":")[-1] if ":" in image else "latest"
    if registry == "ghcr.io":
        remote = f"ghcr.io/{ns}/{name}:{tag}" if ns else image
        token = os.environ.get("GITHUB_PERSONAL_ACCESS_TOKEN", "")
        if token and ns:
            subprocess.run(["docker", "login", "ghcr.io", "-u", ns, "--password-stdin"],
                           input=token, text=True, capture_output=True)
    else:
        hub = os.environ.get("DOCKERHUB_USERNAME", ns)
        remote = f"{hub}/{name}:{tag}"
    steps: list[dict] = []
    rc, _, err = run(["docker", "tag", image, remote])
    steps.append({"step": f"tag → {remote}", "ok": rc == 0, "detail": err[:100]})
    if rc != 0:
        return {"status": "error", "steps": steps}
    rc, out, err = run(["docker", "push", remote], timeout=300)
    steps.append({"step": "push", "ok": rc == 0, "detail": (out or err)[:200]})
    if rc != 0:
        return {"status": "error", "steps": steps}
    if remove_after:
        rc, _, err = run(["docker", "rmi", image])
        steps.append({"step": f"rmi {image}", "ok": rc == 0, "detail": err[:100]})
    return {"status": "ok", "remote": remote, "steps": steps}


# ── Upload ────────────────────────────────────────────────────────────────────

def upload_to_huggingface(local_path: str, repo_id: str, repo_type: str = "model",
                          commit_msg: str = "upload via jarvis") -> dict[str, Any]:
    try:
        from huggingface_hub import HfApi  # type: ignore
    except ImportError:
        return {"status": "error", "detail": "Run: pip install huggingface_hub"}
    token = os.environ.get("HF_TOKEN") or os.environ.get("HUGGINGFACE_TOKEN", "")
    if not token:
        return {"status": "error", "detail": "HF_TOKEN not set. source ~/toolbox/secrets/load-env.sh"}
    api = HfApi(token=token)
    p = Path(local_path)
    try:
        fn = api.upload_folder if p.is_dir() else api.upload_file
        kwargs = ({"folder_path": str(p)} if p.is_dir() else {"path_or_fileobj": str(p), "path_in_repo": p.name})
        url = fn(**kwargs, repo_id=repo_id, repo_type=repo_type, commit_message=commit_msg)
        return {"status": "ok", "url": str(url), "repo": repo_id}
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}


def upload_to_gcs(local_path: str, bucket: str, dest_prefix: str = "") -> dict[str, Any]:
    dest = f"gs://{bucket}/{dest_prefix}".rstrip("/")
    p = Path(local_path)
    cmd = ["gsutil", "-m", "cp"] + (["-r"] if p.is_dir() else []) + [str(p), dest]
    rc, out, err = run(cmd, timeout=600)
    return {"status": "ok", "dest": dest} if rc == 0 else {"status": "error", "detail": err[:300]}


def upload_artifact(local_path: str, dest: str, **kw: Any) -> dict[str, Any]:
    if dest in ("hf", "huggingface"):
        repo = kw.get("repo", "")
        if not repo:
            return {"status": "error", "detail": "--repo required for HuggingFace"}
        return upload_to_huggingface(local_path, repo, kw.get("repo_type", "model"), kw.get("msg", "upload via jarvis"))
    if dest in ("gcs", "gs"):
        bucket = kw.get("bucket", "")
        if not bucket:
            return {"status": "error", "detail": "--bucket required for GCS"}
        return upload_to_gcs(local_path, bucket, kw.get("prefix", ""))
    return {"status": "error", "detail": f"Unknown dest: {dest}. Use: hf, gcs"}


# ── Cloud quota ───────────────────────────────────────────────────────────────

def check_google_drive() -> dict[str, Any]:
    token = os.environ.get("GDRIVE_TOKEN") or os.environ.get("GOOGLE_ACCESS_TOKEN", "")
    if not token:
        return {"status": "unconfigured", "note": "Set GDRIVE_TOKEN or GOOGLE_ACCESS_TOKEN"}
    try:
        import urllib.request as ur
        req = ur.Request("https://www.googleapis.com/drive/v3/about?fields=storageQuota",
                         headers={"Authorization": f"Bearer {token}"})
        data = json.loads(ur.urlopen(req, timeout=5).read())
        q = data.get("storageQuota", {})
        used, limit, trash = int(q.get("usageInDrive", 0)), int(q.get("limit", 0)), int(q.get("usageInDriveTrash", 0))
        return {"status": "ok", "used_human": human_size(used),
                "limit_human": human_size(limit) if limit else "unlimited",
                "trash_human": human_size(trash),
                "percent": round(used / limit * 100, 1) if limit else None}
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}


def check_github_storage() -> dict[str, Any]:
    rc, out, _ = run(["gh", "api", "user/repos", "--paginate", "--jq",
                      "[.[]|{name:.name,size_kb:.size,private:.private}]|sort_by(-.size_kb)|.[0:10]"])
    if rc != 0:
        return {"status": "error", "detail": "gh api failed"}
    try:
        repos = json.loads(out or "[]")
        return {"status": "ok", "top_repos": repos,
                "total_human": human_size(sum(r.get("size_kb", 0) for r in repos) * 1024)}
    except Exception as exc:
        return {"status": "error", "detail": str(exc)}


def check_cloud() -> dict[str, Any]:
    return {"google_drive": check_google_drive(), "github": check_github_storage()}


# ── Clean ─────────────────────────────────────────────────────────────────────

def clean_local(scan: ScanResult, execute: bool = False) -> dict[str, Any]:
    targets = ([{**f, "action": "delete"} for f in scan.garbage_files]
               + [{"path": str(ROOT / f["path"]), "size": f["size"],
                   "reason": f["reason"], "action": "archive"} for f in scan.stale_raw])
    total = sum(t["size"] for t in targets)
    actions: list[str] = []
    if execute:
        archive = ROOT / "raw" / "archive" / "storage_clean" / datetime.now().strftime("%Y-%m-%d")
        archive.mkdir(parents=True, exist_ok=True)
        for t in targets:
            p = Path(t["path"])
            try:
                if t["action"] == "delete":
                    shutil.rmtree(p) if t.get("is_dir") else p.unlink()
                else:
                    shutil.move(str(p), str(archive / p.name))
                actions.append(f"{'deleted' if t['action']=='delete' else 'archived'}  {p.name}")
            except Exception as exc:
                actions.append(f"ERROR  {p.name}: {exc}")
    else:
        actions = [f"would {t['action']}: {Path(t['path']).name} ({human_size(t['size'])})"
                   for t in targets[:25]]
    return {"dry_run": not execute, "targets": len(targets),
            "reclaimable_human": human_size(total), "actions": actions}


# ── Print ─────────────────────────────────────────────────────────────────────

def _h(title: str) -> None:
    print(f"\n{S}\n  {title}\n{S}")


def print_local(scan: ScanResult) -> None:
    print(f"\n{'═'*W}\n  Jarvis Storage — Local\n{'═'*W}")
    _h("Disk usage by directory")
    mx = max(scan.disk_usage.values(), default=1)
    for name, size in list(scan.disk_usage.items())[:12]:
        print(f"  {name:<32} {human_size(size):>10}  {'█' * int(size/mx*26)}")
    if scan.large_files:
        _h(f"Large files (top {min(10, len(scan.large_files))})")
        for f in scan.large_files[:10]:
            age = f"  [{f['days_old']}d]" if f['days_old'] > 14 else ""
            print(f"  {human_size(f['size']):>10}  ...{f['path'][-54:]}{age}")
    if scan.duplicates:
        _h(f"Duplicate groups ({len(scan.duplicates)})")
        for g in scan.duplicates[:4]:
            try:
                sz = Path(g[0]).stat().st_size
            except OSError:
                sz = 0
            print(f"  {len(g)} copies  {human_size(sz)}")
            for path in g:
                print(f"    · ...{path[-65:]}")
    if scan.garbage_files:
        _h(f"Garbage ({len(scan.garbage_files)} items · {human_size(sum(f['size'] for f in scan.garbage_files))})")
        for f in scan.garbage_files[:10]:
            print(f"  {human_size(f['size']):>10}  {f.get('reason',''):<20} ...{f['path'][-40:]}")
    if scan.stale_raw:
        _h(f"Stale raw/ ({len(scan.stale_raw)} · {human_size(sum(f['size'] for f in scan.stale_raw))})")
        for f in scan.stale_raw[:8]:
            print(f"  {f['days_old']:>5.0f}d  {human_size(f['size']):>10}  {f['path']}")
    if scan.cache_usage:
        _h("Cache dirs")
        for d, size in scan.cache_usage.items():
            print(f"  {human_size(size):>10}  {d}")
    print(f"\n  ✦ Total reclaimable: {human_size(scan.total_reclaimable)}")


def print_docker(info: dict) -> None:
    print(f"\n{'═'*W}\n  Jarvis Storage — Docker\n{'═'*W}")
    if info.get("status") == "error":
        print(f"  {info.get('detail')}"); return
    if info.get("summary"):
        _h("docker system df")
        for row in info["summary"]:
            print(f"  {row.get('Type',''):<18} size={row.get('Size',''):<12} reclaimable={row.get('Reclaimable','')}")
    if info.get("images"):
        _h("Images")
        for line in info["images"].splitlines()[:14]:
            print(f"  {line}")


def print_cloud(cloud: dict) -> None:
    print(f"\n{'═'*W}\n  Jarvis Storage — Cloud\n{'═'*W}")
    gd = cloud.get("google_drive", {})
    if gd.get("status") == "ok":
        pct = f"{gd['percent']}%" if gd.get("percent") else "?"
        print(f"\n  Google Drive:  {gd['used_human']} / {gd['limit_human']}  ({pct})")
        if gd.get("trash_human", "0.0 B") != "0.0 B":
            print(f"    Trash:       {gd['trash_human']}")
    else:
        print(f"\n  Google Drive:  {gd.get('status')} — {gd.get('note', gd.get('detail', ''))}")
    gh = cloud.get("github", {})
    if gh.get("status") == "ok":
        print(f"\n  GitHub repos (top 10 · {gh['total_human']}):")
        for r in gh.get("top_repos", [])[:6]:
            print(f"    {'🔒' if r.get('private') else '  '} {r['name']:<38} {human_size(r['size_kb']*1024):>10}")
    else:
        print(f"\n  GitHub:  {gh.get('detail', 'unavailable')}")
    print()


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="command")

    def _sc(p: argparse.ArgumentParser) -> None:
        p.add_argument("--min-size", type=int, default=10, metavar="MB")
        p.add_argument("--scope", type=Path, default=HOME)

    _sc(sub.add_parser("scan")); _sc(sub.add_parser("full"))

    dc = sub.add_parser("docker")
    dc.add_argument("--clean", action="store_true")
    dc.add_argument("--all-images", action="store_true", help="Include ALL unused images")
    dc.add_argument("--volumes", action="store_true")
    dc.add_argument("--yes", action="store_true")

    pu = sub.add_parser("push")
    pu.add_argument("image")
    pu.add_argument("--registry", default="ghcr.io", choices=["ghcr.io", "dockerhub"])
    pu.add_argument("--namespace", default=None)
    pu.add_argument("--remove", action="store_true", help="Remove local image after push")

    ul = sub.add_parser("upload")
    ul.add_argument("path")
    ul.add_argument("--dest", required=True, choices=["hf", "huggingface", "gcs", "gs"])
    ul.add_argument("--repo", default=None, help="HuggingFace repo ID (user/name)")
    ul.add_argument("--repo-type", default="model", choices=["model", "dataset", "space"])
    ul.add_argument("--bucket", default=None, help="GCS bucket")
    ul.add_argument("--prefix", default="")
    ul.add_argument("--msg", default="upload via jarvis")

    sub.add_parser("cloud")

    cl = sub.add_parser("clean")
    cl.add_argument("--scope", type=Path, default=HOME)
    cl.add_argument("--min-size", type=int, default=10, metavar="MB")
    cl.add_argument("--yes", action="store_true")

    args = ap.parse_args()
    if not args.command:
        args.command, args.min_size, args.scope = "scan", 10, HOME

    if args.command in ("scan", "full"):
        print(f"Scanning {args.scope} ...", file=sys.stderr)
        scan = local_scan(args.scope, args.min_size)
        print_local(scan)
        if args.command == "full":
            print_docker(docker_df())
            print_cloud(check_cloud())

    elif args.command == "docker":
        if not docker_available():
            print("Docker not running."); sys.exit(1)
        if args.clean:
            r = docker_clean(volumes=args.volumes, all_images=args.all_images, execute=args.yes)
            if r.get("dry_run"):
                print(f"DRY RUN — current:\n{r.get('current_usage','')}\n\nWould run:")
                for cmd in r.get("would_run", []):
                    print(f"  {cmd}")
                print("\nPass --yes to execute.")
            else:
                for a in r.get("actions", []):
                    print(f"  {'✓' if a['ok'] else '✗'} {a['cmd']}")
                    if a.get("output"):
                        print(f"    {a['output'][:100]}")
        else:
            print_docker(docker_df())

    elif args.command == "push":
        r = docker_push_and_remove(args.image, args.registry, args.namespace, args.remove)
        print(f"{'✓ Pushed to ' + r.get('remote','') if r['status']=='ok' else '✗ Push failed'}")
        for s in r.get("steps", []):
            print(f"  {'✓' if s['ok'] else '✗'} {s['step']}" + (f": {s['detail']}" if s.get("detail") else ""))
        if r["status"] != "ok":
            sys.exit(1)

    elif args.command == "upload":
        r = upload_artifact(args.path, dest=args.dest, repo=getattr(args, "repo", None),
                            repo_type=getattr(args, "repo_type", "model"),
                            bucket=getattr(args, "bucket", None),
                            prefix=getattr(args, "prefix", ""),
                            msg=getattr(args, "msg", "upload via jarvis"))
        print(f"{'✓ Uploaded → ' + str(r.get('url') or r.get('dest','')) if r['status']=='ok' else '✗ ' + r['detail']}")
        if r["status"] != "ok":
            sys.exit(1)

    elif args.command == "cloud":
        print_cloud(check_cloud())

    elif args.command == "clean":
        print("Scanning ...", file=sys.stderr)
        scan = local_scan(args.scope, args.min_size)
        r = clean_local(scan, execute=args.yes)
        mode = "EXECUTED" if args.yes else "DRY RUN"
        print(f"\n── Clean [{mode}] {'─'*38}")
        print(f"  Targets: {r['targets']}  ·  Reclaimable: {r['reclaimable_human']}")
        for a in r["actions"][:25]:
            print(f"  · {a}")
        if not args.yes:
            print("\n  Pass --yes to execute.")


if __name__ == "__main__":
    main()
