# 🚀 Airtest Agent Commands for Cursor

Các lệnh tùy chỉnh dành cho Cursor giúp tương tác nhanh với **Airtest Agent**. Sử dụng Command Palette (Ctrl+Shift+P) và gõ "Airtest" để xem danh sách lệnh.

## 📋 Danh sách lệnh

### 1. Airtest: List Tests
- **Mô tả**: Liệt kê tất cả test case trong thư mục `air_tests`.
- **Lệnh thực thi**: `python -m pixon.tools.airtest_agent.airtest_agent_cli list`
- **Cách dùng**: Chọn lệnh, kết quả hiển thị trong terminal.

### 2. Airtest: Generate Test
- **Mô tả**: Sinh một test case mới dựa trên mô tả bằng ngôn ngữ tự nhiên.
- **Lệnh thực thi**: `python -m pixon.tools.airtest_agent.airtest_agent_cli generate "{{description}}" -o "{{output_file}}"`
- **Inputs**:
  - `description`: Mô tả chi tiết test case (ví dụ: "Test đăng nhập: chạm nút login, nhập user/pass, chờ màn hình chính").
  - `output_file`: Đường dẫn file đầu ra (ví dụ: `tests/test_login.py`).
- **Ví dụ**: Sau khi nhập, agent sẽ sinh code, hiển thị và hỏi xác nhận trước khi ghi.

### 3. Airtest: Review Test
- **Mô tả**: Chỉnh sửa một test case hiện có dựa trên nội dung review.
- **Lệnh thực thi**: `python -m pixon.tools.airtest_agent.airtest_agent_cli review "{{file}}" -r "{{review}}"`
- **Inputs**:
  - `file`: Tên file hoặc đường dẫn (có thể dùng một phần tên, agent sẽ tự tìm).
  - `review`: Nội dung review (ví dụ: "Thêm bước kiểm tra icon thông báo sau khi nhận thưởng").
- **Ví dụ**: Agent sẽ tìm file, hiển thị code mới và hỏi xác nhận trước khi ghi đè.

### 4. Airtest: Help
- **Mô tả**: Hiển thị trợ giúp của CLI.
- **Lệnh thực thi**: `python -m pixon.tools.airtest_agent.airtest_agent_cli --help`
- **Cách dùng**: Xem tất cả tùy chọn có sẵn.

### 5. Airtest: Dry-Run Generate
- **Mô tả**: Sinh test case mới ở chế độ **thử nghiệm** (chỉ hiển thị code, không ghi file).
- **Lệnh thực thi**: `python -m pixon.tools.airtest_agent.airtest_agent_cli generate "{{description}}" -o "{{output_file}}" --dry-run`
- **Inputs**: Tương tự `Generate Test`.
- **Ví dụ**: Dùng để xem trước code trước khi quyết định lưu.

### 6. Airtest: Dry-Run Review
- **Mô tả**: Chỉnh sửa test case theo review ở chế độ **thử nghiệm** (chỉ hiển thị code mới, không ghi file).
- **Lệnh thực thi**: `python -m pixon.tools.airtest_agent.airtest_agent_cli review "{{file}}" -r "{{review}}" --dry-run`
- **Inputs**: Tương tự `Review Test`.

---

## ⚙️ Yêu cầu

- Chạy lệnh từ **thư mục gốc dự án** (project root).
- Module CLI nằm tại `pixon/tools/airtest_agent/`.
- Python 3.10+ và các thư viện: `airtest==1.2.3`, `requests`, `anthropic` (nếu dùng Claude), `python-dotenv` (nếu dùng `.env`).
- Ollama phải được cài đặt và chạy nếu dùng backend `ollama` (mặc định).

---

## 📌 Lưu ý

- Mặc định, agent sẽ **hỏi xác nhận** trước khi ghi file (trừ khi dùng `--force`).
- Sử dụng `--dry-run` để kiểm tra an toàn.
- Backup tự động được tạo (`.bak`) trước khi ghi đè.

Hãy đảm bảo bạn đã cấu hình đúng backend và model trước khi sử dụng (có thể chỉnh trong file `pixon/tools/airtest_agent/airtest_agent_cli.py` hoặc dùng biến môi trường).