import argparse
import os
import sys
import logging
import shutil

from datetime import datetime
from pathlib import Path
from pixon.pixonwrapper import *

# off airtest console logging
logger = logging.getLogger("airtest")
logger.setLevel(logging.ERROR)

# parse command line arguments
parser = argparse.ArgumentParser(description="Run exporter")
parser.add_argument("--report", type=Path, required=False)
parser.add_argument("--device", type=str, required=False)
parser.add_argument("--recording", nargs="?", default=False, const=True, required=False)

args, argsv = parser.parse_known_args()

# --- find .air project ---
air_name = next((a for a in argsv if a.lower().endswith(".air")), None)

if not air_name:
    raise ValueError("No .air file specified in arguments")

current_dir = Path(__file__).resolve().parent
air_path = Path(air_name).resolve()
air_py = air_path / f"{air_path.stem}.py"

if not air_py.exists():
    raise FileNotFoundError(f"Main airtest file not found: {air_py}")

# --- setup Airtest ---
auto_setup(str(air_py))

# connect device
device_id = None
if args.device:
    try:
        if args.device.lower().startswith("android://"):
            connect_device(args.device)
            device_id = args.device.split("///")[-1]
        else:
            connect_device(f"Android://127.0.0.1:5037/{args.device}")
            device_id = args.device
        print(f"Connected to device: {device_id}")
    except Exception as e:
        print(f"Failed to connect device {args.device}: {e}")
        sys.exit(1)
else:
    print("No device specified, exiting.")
    sys.exit(1)

# set up report path
log_dir = air_path / "log"
shutil.rmtree(log_dir, ignore_errors=True)
set_logdir(log_dir)
report_path = air_path.parent / "Reports"
if args.report:
    report_path = Path(args.report).resolve()

# set up recording
recorder = None
if args.recording:
    file_name = f'{device_id}_record_{datetime.now().strftime("%Y%m%d_%H%M%S")}.mp4'
    if os.path.isdir(args.recording) or os.path.isfile(args.recording):
        recording_path: Path = Path(args.recording).resolve()
        if recording_path.is_dir():
            recording_path = recording_path / file_name
    else:
        recording_path = (
            report_path.resolve() / "Recordings" / f"{air_name}" / file_name
        )

    from pixon.ScrcpyRecorder import ScrcpyRecorder

    recorder = ScrcpyRecorder(
        output=recording_path,
        device=device_id,
        scrcpy_path=current_dir / "scrcpy-win64" / "scrcpy.exe",
    )
    recorder.start()
    print("Start recording ...")

# run the test module
sys.path.insert(0, str(air_path))
module_name = air_path.stem
test_module = __import__(module_name)
if hasattr(test_module, "main"):
    test_module.main()


if report_path:
    from airtest.report.report import LogToHtml

    print(f"Exporting log to {report_path} from {ST.LOG_DIR}")
    try:
        LogToHtml(script_root=air_py, export_dir=report_path).report()
    except Exception as e:
        print(f"Failed to export report: {e}")

if recorder:
    recorder.stop()
    print("Copy recording to report")
    shutil.copy2(recording_path, report_path / f"{air_name.replace('.air', '.log')}")


# stop the adb server
from airtest.core.android.adb import ADB

adb: ADB = G.DEVICE.adb
adb.kill_server()
