# Screw Land Automation Test

Dự án automation test cho game Screw Land sử dụng Airtest.

## Cấu trúc thư mục

- `common/`: Các lớp dùng chung (BasePage)
- `pages/`: Các Page Object tương ứng với từng màn hình
- `pixon/`: Thư viện wrapper Airtest và các tiện ích
- `tests/`: Các bộ test, mỗi test nằm trong thư mục `.air`

## Yêu cầu

- Python 3.7+
- Airtest
- Tesseract OCR (cài đặt và cấu hình đường dẫn trong `pixonwrapper.py`)

## Cách chạy

```bash
python pixon_run.py tests/DailyMission/test_new_user.air --device Android://127.0.0.1:5037/emulator-5554