# Second Brain

Ứng dụng quản lý tài liệu local, Python backend + HTML/CSS/JS trong cửa sổ pywebview.

## Chạy trên máy hiện tại

Đã cài editable vào Python global. Từ CMD ở bất kỳ thư mục nào:

```cmd
sb run
sb doctor
```

Config mặc định: `D:\SecondBrain\config.yaml`, không phụ thuộc cwd. Có thể chỉ định rõ:

```cmd
sb --config D:\SecondBrain\config.yaml run
```

UI mở cửa sổ riêng, không cần mở browser. Windows cần WebView2 runtime. Linux chưa được kiểm thử; pywebview cần backend GUI tương ứng của hệ điều hành.

## Cài đặt từ source

Trong thư mục dự án, dùng Python global:

```cmd
python -m pip install -e .
```

Đảm bảo thư mục Scripts của Python nằm trong PATH. Editable install tham chiếu source: nếu di chuyển project cần cài lại. Không tự tạo config nếu thiếu; sao chép `config.example.yaml` thành `config.yaml` và chỉnh trước khi chạy. Không đặt secret trong repo.

## Trạng thái

Đã có thêm file, tag, graph 70/30 nền vũ trụ, tìm tên/path/tag và lưu metadata SQLite. **Chưa có MCP, RAG, thùng rác hoặc UI quản trị quyền**. Không phải bản release hoàn chỉnh.

Đăng ký file giữ nguyên nguồn; không có xóa/sửa nội dung file trong bản này. Nền SVG được tạo cho dự án, không tải asset bên ngoài.

## Kiểm thử

```cmd
python -m pytest -q
python tests/ui_smoke.py
```

Lệnh smoke mở rồi đóng cửa sổ thật. Tất cả test nằm trong `tests/`.

Xem [contract](docs/contract.md), [UI design](docs/UI_design.md), [architecture](docs/Architecture_plan.md) và [trạng thái triển khai](docs/Implementation_status.md).
