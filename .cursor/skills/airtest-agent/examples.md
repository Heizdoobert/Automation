## Example: Understand project structure

User: "Cho tôi biết cấu trúc dự án"

Assistant:
- Identify repo root by locating `air_tests/`, `pages/`, `common/`, `pixon/`.
- Summarize the main directories and (if requested) the count of relevant files.

## Example: Read and summarize a test case

User: "Xem test tc01_daily_mission"

Assistant:
1. Find matching files under `air_tests/` (e.g., `air_tests/DailyMission/tc01_daily_mission.air/tc01_daily_mission.py`).
2. Read the file.
3. Summarize:
   - Step flow (touch/wait/assert).
   - Templates used (all `Template("images/...")`).
   - Assertions and success criteria.

## Example: Generate a new test case

User: "Viết test đăng nhập: chạm nút login, nhập username, password, chờ màn hình chính"

Assistant:
1. Propose a test flow and request missing template names if needed.
2. Produce a full `.py` file that uses relative `images/...` templates.
3. Validate syntax.
4. Ask for a save path and explicit confirmation before writing.

## Example: Edit a test case from review

User: "Review file tc01_daily_mission: thêm bước kiểm tra icon thông báo sau khi nhận thưởng"

Assistant:
1. Locate and read the file.
2. Add an `assert_exists(Template("images/..."), "...")` step at the correct point.
3. Validate syntax.
4. Show updated code and ask for explicit confirmation; recommend backup.
