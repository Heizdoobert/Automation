import argparse
import glob
import logging
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

from pixon.pixonwrapper import *

try:
    from pixon.airtouch_fast import MinitouchWrapper

    HAS_MINITOUCH = True
except ImportError:
    HAS_MINITOUCH = False
    MinitouchWrapper = None

logger = logging.getLogger("airtest")
logger.setLevel(logging.INFO)


def _collect_air_paths(argsv: list[str]) -> list[str]:
    raw_names = [a for a in argsv if a.lower().endswith(".air")]
    air_names: list[str] = []
    for name in raw_names:
        if "*" in str(name) or "?" in str(name):
            expanded = glob.glob(name)
            if expanded:
                air_names.extend(expanded)
            else:
                print(f"Warning: No files matching {name}")
        else:
            air_names.append(name)
    return air_names


def run_one(
    air_name: str,
    report_root: Path,
    device_id: str | None,
    recording: bool | str,
    current_dir: Path,
) -> bool:
    air_path = Path(air_name).resolve()
    air_py = air_path / f"{air_path.stem}.py"

    if not air_py.exists():
        print(f"[SKIP] Main script not found: {air_py}")
        return False

    log_dir = air_path / "log"
    shutil.rmtree(log_dir, ignore_errors=True)
    set_logdir(log_dir)

    test_report_dir = report_root / air_path.stem
    test_report_dir.mkdir(parents=True, exist_ok=True)

    auto_setup(str(air_py))
    reset_error_state()

    recorder = None
    recording_path: Path | None = None
    if recording:
        file_name = f"{device_id or 'device'}_record_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        if isinstance(recording, str) and (
            os.path.isdir(recording) or os.path.isfile(recording)
        ):
            recording_path = Path(recording).resolve()
            if recording_path.is_dir():
                recording_path = recording_path / file_name
        else:
            recording_path = test_report_dir / "Recordings" / file_name

        recording_path.parent.mkdir(parents=True, exist_ok=True)

        from pixon.ScrcpyRecorder import ScrcpyRecorder

        scrcpy_exe = current_dir / "scrcpy-win64" / "scrcpy.exe"
        recorder = ScrcpyRecorder(
            output=recording_path, device=device_id, scrcpy_path=str(scrcpy_exe)
        )
        recorder.start()
        print(f"  Recording started → {recording_path}")

    test_passed = True
    try:
        if str(air_path) not in sys.path:
            sys.path.insert(0, str(air_path))

        module_name = air_path.stem
        if module_name in sys.modules:
            del sys.modules[module_name]

        test_module = __import__(module_name)
        if not hasattr(test_module, "main"):
            print(f"  [ERROR] {air_path.stem} has no main() function")
            test_passed = False
        else:
            test_module.main()
            if has_error_state():
                print(
                    f"  [ERROR] {air_path.stem}: test script logged runtime errors"
                )
                test_passed = False

    except Exception as e:
        print(f"  [ERROR] {air_path.stem}: {e}")
        test_passed = False

    finally:
        print(f"  Exporting report -> {test_report_dir}")
        report_generated = False
        try:
            from airtest.report.report import LogToHtml

            script_root_str = str(air_py) if not isinstance(air_py, str) else air_py
            LogToHtml(script_root=str(air_py), export_dir=str(test_report_dir)).report()
            report_generated = True
        except Exception as e:
            print(f"  [WARN] Failed to export report: {e}")

        if not report_generated:
            fallback_report = test_report_dir / "log.html"
            fallback_report.write_text(
                (
                    "<html><body>"
                    f"<h2>Report export failed for {air_path.stem}</h2>"
                    "<p>Airtest LogToHtml failed. Check console output and raw log dir.</p>"
                    f"<p>Raw log dir: {log_dir}</p>"
                    "</body></html>"
                ),
                encoding="utf-8",
            )

        if recorder:
            recorder.stop()
            if recording_path and recording_path.exists():
                (test_report_dir / "Recordings").mkdir(parents=True, exist_ok=True)
                shutil.copy2(recording_path, test_report_dir / f"{air_path.stem}.mp4")

    return test_passed


def generate_summary_report(results: list[tuple[str, bool]], report_root: Path) -> None:
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Daily Mission Test Summary</title>
        <style>
            table { border-collapse: collapse; width: 80%; margin: 20px auto; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .pass { color: green; font-weight: bold; }
            .fail { color: red; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1 style="text-align:center;">Daily Mission Test Summary</h1>
        <table>
            <tr>
                <th>Test Name</th>
                <th>Result</th>
                <th>Report Link</th>
            </tr>
    """
    for name, passed in results:
        test_dir = report_root / name
        log_file = None

        for pattern in ["log.html", "*.log/log.html", "*/log.html"]:
            matches = list(test_dir.glob(pattern))
            if matches:
                log_file = matches[0]
                break

        if log_file:
            rel_path = log_file.relative_to(report_root).as_posix()
            link_html = f'<a href="{rel_path}" target="_blank">View Report</a>'
        else:
            link_html = '<span style="color:gray;">No report</span>'

        result_class = "pass" if passed else "fail"
        result_text = "PASS" if passed else "FAIL"
        html_content += f"""
            <tr>
                <td>{name}</td>
                <td class="{result_class}">{result_text}</td>
                <td>{link_html}</td>
            </tr>
        """
    html_content += """
        </table>
    </body>
    </html>
    """
    summary_file = report_root / "index.html"
    summary_file.write_text(html_content, encoding="utf-8")
    print(f"Summary report generated: {summary_file}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Airtest batch runner")
    parser.add_argument("--report", type=Path, required=False)
    parser.add_argument("--device", type=str, required=False)
    parser.add_argument(
        "--recording", nargs="?", default=False, const=True, required=False
    )

    args, argsv = parser.parse_known_args(argv)

    air_names = _collect_air_paths(list(argsv))
    if not air_names:
        raise ValueError(
            "No .air file specified. Pass one or more .air paths as arguments."
        )

    current_dir = Path(__file__).resolve().parent

    device_id = None
    if args.device:
        try:
            if args.device.lower().startswith("android://"):
                connect_device(args.device)
                device_id = args.device.split("///")[-1]
            else:
                connect_device(f"android://127.0.0.1:5037/{args.device}")
                device_id = args.device
            print(f"Connected to device: {device_id}")
        except Exception as e:
            print(f"Failed to connect device {args.device}: {e}")
            return 1
    else:
        try:
            init_device()
            if G.DEVICE:
                device_id = getattr(G.DEVICE, "serialno", None)
        except Exception as e:
            print(f"Failed to connect device: {e}")
            return 1

    mt_wrapper = None
    if HAS_MINITOUCH and device_id:
        try:
            mt_wrapper = MinitouchWrapper(serial=device_id)
            mt_wrapper.start()
            print(f"Minitouch daemon started for {device_id}")

            def airtest_touch(pos, **kwargs):
                if isinstance(pos, (list, tuple)) and len(pos) >= 2:
                    x, y = int(pos[0]), int(pos[1])
                else:
                    x, y = int(pos), kwargs.get("y", 0)
                mt_wrapper.touch(x, y)
                return pos

            def airtest_swipe(p1, p2=None, **kwargs):
                if p2 is None:
                    print(
                        "Warning: swipe with vector not fully supported by airtouch-fast"
                    )
                    return
                start = (
                    (int(p1[0]), int(p1[1]))
                    if isinstance(p1, (list, tuple))
                    else (0, 0)
                )
                end = (
                    (int(p2[0]), int(p2[1]))
                    if isinstance(p2, (list, tuple))
                    else (0, 0)
                )
                duration = kwargs.get("duration", 0.5)
                mt_wrapper.swipe(start, end, duration=duration)
                return p2

            if G.DEVICE:
                G.DEVICE.touch = airtest_touch
                G.DEVICE.swipe = airtest_swipe
                print(
                    "Airtest touch/swipe methods replaced with airtouch-fast (wrapper applied)."
                )

        except Exception as e:
            print(f"Warning: MinitouchWrapper failed: {e}")

    report_root = (
        Path(args.report).resolve()
        if args.report
        else (Path.cwd().resolve() / "reports")
    )
    report_root.mkdir(parents=True, exist_ok=True)

    results: list[tuple[str, bool]] = []
    for air_name in air_names:
        test_name = Path(air_name).stem
        print(f"\n{'=' * 60}\n  Running: {test_name}\n{'=' * 60}")

        passed = run_one(air_name, report_root, device_id, args.recording, current_dir)
        results.append((test_name, passed))
        print(f"  -> {test_name}: {'PASSED PASS' if passed else 'FAILED FAIL'}")

    generate_summary_report(results, report_root)

    if mt_wrapper:
        try:
            mt_wrapper.stop()
            print("Minitouch daemon stopped.")
        except Exception as e:
            print(f"Warning: failed to stop MinitouchWrapper: {e}")

    total = len(results)
    passed_cnt = sum(1 for _, ok in results if ok)
    failed = total - passed_cnt

    print(f"\n{'=' * 60}\n  TEST SUMMARY  ({passed_cnt}/{total} passed)\n{'=' * 60}")
    for name, ok in results:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    print(f"{'=' * 60}\n")

    return failed


if __name__ == "__main__":
    raise SystemExit(main())
