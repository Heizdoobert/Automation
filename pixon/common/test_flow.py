import time
from typing import Any, Callable

import pixon.pixonwrapper as wrapper


def log_step(message: str) -> None:
    """Write a normalized step log that can be reused across test suites."""
    wrapper.log_info(f"[STEP] {message}")


def run_step(name: str, action: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    """Execute one step with consistent start/end/duration logging."""
    start = time.time()
    log_step(f"START: {name}")
    try:
        result = action(*args, **kwargs)
        return result
    finally:
        elapsed = time.time() - start
        log_step(f"END: {name} ({elapsed:.2f}s)")


def ensure_home(
    home: Any,
    close_popups: Callable[[Any], None],
    retries: int = 3,
    settle_seconds: float = 1.0,
) -> None:
    """Ensure the app returns to home using provided page object and popup handler."""
    close_popups(home)
    if home.is_at_home():
        close_popups(home)
        return

    for attempt in range(retries):
        log_step(f"ensure_home attempt {attempt + 1}/{retries}")
        if home.go_home(force=True):
            time.sleep(settle_seconds)
            close_popups(home)
            if home.is_at_home():
                log_step("ensure_home resolved")
                return
        wrapper.log_warning(f"ensure_home attempt {attempt + 1} failed")

    raise AssertionError("Not at home after navigation")
