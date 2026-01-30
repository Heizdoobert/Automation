import os
import subprocess
import time
import platform
import threading
from pathlib import Path
from typing import Optional, Tuple, Callable


class AndroidScreenRecorder:
    """
    Android screen recorder that handles encoder failures (err=-38).

    Strategy:
    - Uses very short segments (15-20 seconds) to stay well under failure point
    - Tests different encoder settings to find what works
    - Auto-detects optimal bitrate and resolution for your device
    - Continuous recording with automatic segment management
    """

    def __init__(self, device_id: Optional[str] = None):
        """Initialize the screen recorder."""
        self.device_id = device_id
        self.is_recording = False
        self.remote_path = "/sdcard/screen_recording.mp4"
        self.is_windows = platform.system() == "Windows"

        self.optimal_settings = {
            "bitrate": 3000000,
            "size": None,
            "name": "Native @ 3Mbps",
        }

        env = os.environ.copy()
        env["ANDROID_ADB_SERVER_PORT"] = "5038"
        self.adb_env = env

        # Segment recording attributes
        self.segmented_recording = False
        self.monitor_thread = None
        self.segment_callback = None
        self._lock = threading.Lock()

        self._check_adb()

    def _check_adb(self) -> bool:
        """Check if ADB is available and devices are connected."""
        try:
            result = subprocess.run(
                self._get_adb_command(["version"]),
                capture_output=True,
                text=True,
                check=True,
                timeout=5,
                env=self.adb_env,
            )
            return True
        except:
            raise RuntimeError("ADB is not installed or not in PATH")

    def _get_adb_command(self, command: list) -> list:
        """Build ADB command with device specification if needed."""
        base = ["adb"]
        if self.device_id:
            base.extend(["-s", self.device_id])
        base.extend(["-P", "5038"])
        base.extend(command)
        return base

    def _kill_screenrecord_on_device(self) -> bool:
        """Kill the screenrecord process directly on the Android device."""
        try:
            cmd = self._get_adb_command(["shell", "pkill", "-2", "screenrecord"])
            subprocess.run(
                cmd, capture_output=True, text=True, timeout=5, env=self.adb_env
            )
            time.sleep(0.5)
            return True
        except:
            try:
                cmd = self._get_adb_command(["shell", "pidof screenrecord"])
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=5, env=self.adb_env
                )

                if result.returncode == 0 and result.stdout.strip():
                    pid = result.stdout.strip()
                    kill_cmd = self._get_adb_command(["shell", "kill", "-2", pid])
                    subprocess.run(
                        kill_cmd,
                        capture_output=True,
                        check=True,
                        timeout=5,
                        env=self.adb_env,
                    )
                    time.sleep(0.5)
                    return True
            except:
                pass
            return False

    def _start_screenrecord_detached(
        self,
        bit_rate: int,
        time_limit: int,
        size: Optional[Tuple[int, int]] = None,
    ) -> bool:
        """Start screenrecord as a detached process on the device."""
        try:
            cmd_parts = [
                "screenrecord",
                f"--bit-rate={bit_rate}",
                f"--time-limit={time_limit}",
            ]

            if size:
                width, height = size
                cmd_parts.append(f"--size={width}x{height}")

            cmd_parts.append(self.remote_path)

            # Execute as detached background process
            full_cmd = " ".join(cmd_parts)
            adb_cmd = self._get_adb_command(
                ["shell", f"nohup {full_cmd} > /dev/null 2>&1 &"]
            )

            result = subprocess.run(
                adb_cmd, capture_output=True, text=True, timeout=5, env=self.adb_env
            )
            time.sleep(1)

            # Verify it's running
            check_cmd = self._get_adb_command(["shell", "pidof screenrecord"])
            check_result = subprocess.run(
                check_cmd, capture_output=True, text=True, timeout=5, env=self.adb_env
            )

            return check_result.returncode == 0 and bool(check_result.stdout.strip())

        except Exception as e:
            print(f"❌ Error starting screenrecord: {e}")
            return False

    def _is_screenrecord_running(self) -> bool:
        """Check if screenrecord is currently running on the device."""
        try:
            cmd = self._get_adb_command(["shell", "pidof screenrecord"])
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=5, env=self.adb_env
            )
            return result.returncode == 0 and bool(result.stdout.strip())
        except:
            return False

    def pull_recording(
        self,
        remote_path: str,
        local_path: str,
        delete_remote: bool = True,
        max_retries: int = 3,
    ) -> bool:
        """Pull the recorded video from device to local machine with retry logic."""
        try:
            Path(local_path).parent.mkdir(parents=True, exist_ok=True)

            for attempt in range(max_retries):
                try:
                    cmd = self._get_adb_command(["pull", remote_path, local_path])
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        check=True,
                        timeout=30,
                        env=self.adb_env,
                    )

                    if (
                        Path(local_path).exists()
                        and Path(local_path).stat().st_size > 0
                    ):
                        if delete_remote:
                            subprocess.run(
                                self._get_adb_command(["shell", "rm", remote_path]),
                                capture_output=True,
                                timeout=10,
                                env=self.adb_env,
                            )
                        return True
                except:
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    raise

            return False

        except Exception as e:
            print(f"❌ Error pulling {remote_path}: {e}")
            return False

    def record_with_segments(
        self,
        segment_duration: int = None,  # Will auto-determine if None
        bit_rate: int = None,  # Will use tested optimal if None
        size: Optional[Tuple[int, int]] = None,  # Will use tested optimal if None
        on_segment_complete: Optional[Callable[[int, str], None]] = None,
    ):
        """
        Start continuous segment recording using tested optimal settings.

        Args:
            segment_duration: Duration of each segment (default: auto, typically 15-20s)
            bit_rate: Video bit rate (default: uses tested optimal)
            size: Video size (default: uses tested optimal)
            on_segment_complete: Optional callback function(segment_number, remote_path)
        """
        # Use optimal settings if not specified
        if segment_duration is None:
            segment_duration = 18  # Conservative: well under 27s failure point

        if bit_rate is None:
            bit_rate = self.optimal_settings["bitrate"]

        if size is None:
            size = self.optimal_settings["size"]

        self.segment_duration = segment_duration
        self.segment_bit_rate = bit_rate
        self.segment_size = size
        self.segment_number = 0
        self.segment_files = []
        self.segmented_recording = True
        self.segment_callback = on_segment_complete

        # Start monitoring thread
        self.monitor_thread = threading.Thread(
            target=self._segment_monitor_loop, daemon=True
        )
        self.monitor_thread.start()

        # Start first segment
        self._record_next_segment()

    def _record_next_segment(self):
        """Internal method to record the next segment using detached process."""
        if not self.segmented_recording:
            return

        self.segment_number += 1
        segment_filename = f"segment_{self.segment_number:03d}.mp4"

        # Update remote path for this segment
        base_path = "/data/local/tmp"  # Use internal storage (more reliable)
        self.remote_path = (
            f"{base_path}/rec_{int(time.time())}_{self.segment_number:03d}.mp4"
        )

        print(f"📹 Recording segment {self.segment_number}...")

        try:
            success = self._start_screenrecord_detached(
                bit_rate=self.segment_bit_rate,
                time_limit=self.segment_duration,
                size=self.segment_size,
            )

            if success:
                self.is_recording = True
                self.segment_files.append(
                    {
                        "number": self.segment_number,
                        "remote_path": self.remote_path,
                        "filename": segment_filename,
                    }
                )
            else:
                print(f"❌ Failed to start segment {self.segment_number}")
                self.segmented_recording = False

        except Exception as e:
            print(f"❌ Error starting segment {self.segment_number}: {e}")
            self.segmented_recording = False

    def _segment_monitor_loop(self):
        """Background thread that monitors segments and starts new ones automatically."""
        while self.segmented_recording:
            time.sleep(0.1)

            is_running = self._is_screenrecord_running()

            if self.is_recording and not is_running:
                segment_num = self.segment_number
                remote_path = self.remote_path

                print(f"✓ Segment {segment_num} completed")
                self.is_recording = False

                if self.segment_callback:
                    try:
                        self.segment_callback(segment_num, remote_path)
                    except Exception as e:
                        print(f"⚠ Callback error: {e}")
                if self.segmented_recording:
                    self._record_next_segment()

    def stop_segments(self, output: str = ".", delete_remote: bool = True) -> Path:
        """Stop segment recording and pull all segments to local directory."""
        print("\n⏹ Stopping segment recording...")

        self.segmented_recording = False
        self._kill_screenrecord_on_device()

        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)

        self.is_recording = False
        time.sleep(3)

        output_path = Path(output)
        output_path.mkdir(parents=True, exist_ok=True)

        print(f"\n📥 Pulling {len(self.segment_files)} segments to {output}/...")
        local_files = []

        for segment in self.segment_files:
            local_file = output_path / segment["filename"]
            print(f"   Pulling segment {segment['number']}...", end=" ")

            success = self.pull_recording(
                remote_path=segment["remote_path"],
                local_path=str(local_file),
                delete_remote=delete_remote,
                max_retries=3,
            )

            if success:
                print("✓")
                local_files.append(str(local_file))
            else:
                print("✗")

        print(
            f"\n✅ Recording complete! {len(local_files)} segments saved to {output}/"
        )

        self.segment_files = []
        self.segment_number = 0

        print(local_files)
        return self.merge_mp4_moviepy(
            local_files, output_path=output_path / "merged_output.mp4"
        )
        # return local_files

    def get_segment_count(self) -> int:
        """Get the current number of recorded segments."""
        return len(self.segment_files)

    def is_recording_active(self) -> bool:
        """Check if segment recording is currently active."""
        return self.segmented_recording

    def merge_mp4_moviepy(self, paths, output_path):
        from moviepy import VideoFileClip, concatenate_videoclips

        clips = [VideoFileClip(p) for p in paths]
        final = concatenate_videoclips(clips, method="compose")

        final.write_videofile(
            output_path, codec="libx264", audio_codec="aac", fps=clips[0].fps
        )

        for c in clips:
            c.close()

        return output_path

    # def concat_mp4_ffmpeg(self, mp4_paths, output_path) -> Path:
    #     """
    #     Concatenate MP4 files into one using ffmpeg (no re-encode).
    #     """
    #     import tempfile

    #     mp4_paths = [Path(p).resolve() for p in mp4_paths]
    #     output_path = Path(output_path).resolve()

    #     with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
    #         for p in mp4_paths:
    #             f.write(f"file '{p.as_posix()}'\n")
    #         list_file = f.name

    #     cmd = [
    #         "ffmpeg",
    #         "-y",
    #         "-f",
    #         "concat",
    #         "-safe",
    #         "0",
    #         "-i",
    #         list_file,
    #         "-c",
    #         "copy",
    #         output_path,
    #     ]

    #     subprocess.run(cmd, check=True, env=self.adb_env)
    #     return output_path
