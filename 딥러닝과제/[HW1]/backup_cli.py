import argparse
import os
import sys
import time
from datetime import datetime
from typing import Any, Dict

import yaml

from backup_core import perform_backup
from kakao_notify import send_kakao_memo


def load_config(path: str) -> Dict[str, Any]:
	with open(path, "r", encoding="utf-8") as f:
		return yaml.safe_load(f)


def format_bytes(num_bytes: int) -> str:
	# Simple human-readable formatter
	units = ["B", "KB", "MB", "GB", "TB"]
	size = float(num_bytes)
	for unit in units:
		if size < 1024.0 or unit == units[-1]:
			return f"{size:.2f} {unit}"
		size /= 1024.0


def run_once(config: Dict[str, Any]) -> None:
	source_dir = config.get("source_dir")
	backup_dir = config.get("backup_dir")
	if not source_dir or not backup_dir:
		raise ValueError("source_dir and backup_dir must be set in config")

	stats = perform_backup(source_dir, backup_dir)

	kakao_cfg = config.get("kakao", {}) or {}
	if kakao_cfg.get("enabled"):
		message_template = kakao_cfg.get(
			"message_template",
			"[Backup] {timestamp} - Copied {files_copied} files, {bytes_copied} bytes",
		)
		message = message_template.format(
			timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
			files_copied=stats.files_copied,
			bytes_copied=format_bytes(stats.bytes_copied),
		)
		error = send_kakao_memo(kakao_cfg.get("access_token", ""), message)
		if error:
			print(f"[WARN] Kakao notification failed: {error}")

	print(
		f"Backup completed: {stats.files_copied} files, {format_bytes(stats.bytes_copied)} in {stats.duration_seconds:.2f}s"
	)


def main() -> None:
	parser = argparse.ArgumentParser(description="Periodic folder backup with optional KakaoTalk notification")
	parser.add_argument(
		"--config",
		type=str,
		default="config.yaml",
		help="Path to YAML config file (default: config.yaml)",
	)
	parser.add_argument(
		"--once",
		action="store_true",
		help="Run a single backup and exit (ignore interval)",
	)
	args = parser.parse_args()

	cfg_path = args.config
	if not os.path.exists(cfg_path):
		print(f"Config file not found: {cfg_path}")
		sys.exit(1)

	config = load_config(cfg_path)

	if args.once:
		run_once(config)
		return

	interval_minutes = int(config.get("interval_minutes", 60))
	interval_seconds = max(1, interval_minutes * 60)

	print(f"Starting periodic backup every {interval_minutes} minute(s). Press Ctrl+C to stop.")
	try:
		while True:
			run_once(config)
			time.sleep(interval_seconds)
	except KeyboardInterrupt:
		print("Stopped.")


if __name__ == "__main__":
	main()


