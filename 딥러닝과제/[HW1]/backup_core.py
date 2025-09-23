import os
import shutil
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple


@dataclass
class BackupStats:
	files_copied: int
	bytes_copied: int
	start_time: float
	end_time: float

	@property
	def duration_seconds(self) -> float:
		return self.end_time - self.start_time


def ensure_directory_exists(path: str) -> None:
	if not os.path.exists(path):
		os.makedirs(path, exist_ok=True)


def copy_file_with_dirs(src_file: str, dest_file: str) -> int:
	"""Copy a single file ensuring destination directory exists. Returns bytes copied."""
	dest_dir = os.path.dirname(dest_file)
	ensure_directory_exists(dest_dir)
	shutil.copy2(src_file, dest_file)
	return os.path.getsize(dest_file)


def perform_backup(source_dir: str, backup_dir: str, now: Optional[datetime] = None) -> BackupStats:
	"""Copy all files from source_dir to backup_dir, preserving subdirectories.

	- Only copies files (directories are recreated as needed)
	- Uses copy2 to preserve metadata
	- Returns BackupStats
	"""
	if now is None:
		now = datetime.now()

	start = time.time()
	files_copied = 0
	bytes_copied = 0

	# Normalize paths
	source_dir = os.path.abspath(source_dir)
	backup_dir = os.path.abspath(backup_dir)

	# Print backup paths
	print(f"[Backup] Source directory: {source_dir}")
	print(f"[Backup] Backup directory: {backup_dir}")

	for root, dirs, files in os.walk(source_dir):
		rel_root = os.path.relpath(root, source_dir)
		for file_name in files:
			src_path = os.path.join(root, file_name)
			# Skip if it is not a file
			if not os.path.isfile(src_path):
				continue

			dest_path = os.path.join(backup_dir, rel_root, file_name) if rel_root != os.curdir else os.path.join(backup_dir, file_name)
			bytes_written = copy_file_with_dirs(src_path, dest_path)
			print(f"[Backup] Copied: {src_path} -> {dest_path} ({bytes_written} bytes)")
			files_copied += 1
			bytes_copied += bytes_written

	end = time.time()
	return BackupStats(files_copied=files_copied, bytes_copied=bytes_copied, start_time=start, end_time=end)


