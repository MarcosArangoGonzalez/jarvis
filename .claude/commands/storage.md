Run the Jarvis storage manager to scan for garbage, large files, duplicates, and Docker bloat.

```bash
python3 /home/marcos/jarvis/tools/skills/storage_manager.py $ARGUMENTS
```

Common usage:
- `/storage` — full scan report (no deletions)
- `/storage --clean` — delete garbage files and archive stale raw/ items
- `/storage --docker-clean` — prune Docker stopped containers, dangling images, unused networks
- `/storage --docker-clean --volumes` — also remove unused Docker volumes (destructive!)
- `/storage --push-image <image>` — tag and push a Docker image to ghcr.io, then remove local copy
- `/storage --hf-upload <path> <repo>` — upload a file or folder to HuggingFace Hub
- `/storage --cloud-check` — show GitHub repo sizes and Google Drive quota

After scanning, present a summary: disk used, top space hogs, what's reclaimable, and recommended next action.
