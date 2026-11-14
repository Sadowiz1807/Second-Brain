# Implementation status — 09/11/2026

## Refactor readability — 14/11/2026

- Áp dụng rule coding mới cho toàn bộ Python trong app/tests và HTML/CSS/JS/SVG của desktop: format đa dòng, block điều kiện/loop rõ, khai báo biến riêng.
- Tách biến trung gian cho lọc tài liệu, checksum import, thông báo xác nhận, kết quả copy và báo cáo lỗi. Tách callback restore folder khỏi menu lồng nhau; thay nhánh ternary lồng trong action UI bằng if rõ ràng.
- Thêm `.prettierrc.json`, `eslint.config.mjs`, cấu hình Black trong pyproject và hướng dẫn `docs/Code_style.md`. Không đổi contract chức năng trong lượt này.
- Kiểm tra: Black check 15 file pass; ESLint pass; Prettier check pass; JS syntax pass; 19 tests passed; desktop smoke Windows pass. Chưa kiểm tra tương tác E2E đầy đủ hoặc Linux.

## Cập nhật cây thư mục/native picker — 14/11/2026

- Cây render từ danh sách folder trên disk, gồm folder rỗng, không chỉ suy từ document. Mặc định đóng; giữ trạng thái mở trong phiên.
- Toolbar icon Thêm dùng OS picker nhập storage/; menu thư mục add.. nhập đúng đích. Tạo thư mục bằng dialog nhỏ, không có UI duyệt nguồn tự xây trong luồng nhập.
- File menu view/delete, folder menu add../delete. Xóa folder rename cả cây vào trash cùng filesystem, gồm cả file chưa đăng ký; ghi pending trước thao tác và chỉ commit metadata sau rename. Không fallback xóa cây khi rename lỗi.
- Có khôi phục cả folder từ menu trash; chưa có purge cả folder và UI recovery pending. Lỗi/crash giữa filesystem và DB vẫn cần xử lý journal thủ công; chưa chứng minh concurrency đa tiến trình.
- Icon SVG tự vẽ, tham khảo Product Icon Reference của VS Code (https://code.visualstudio.com/api/references/icons-in-labels); không tải thư viện icon ngoài.
- 19 tests pass; JS syntax và desktop smoke Windows pass. Chưa E2E toàn bộ native dialog hoặc Linux.

## Cập nhật panel nhập và trash — 14/11/2026

- Thêm/Tạo thư mục cùng thanh; bỏ nút Nhập thư mục và form đích cố định. `import_picker.py` + `import-ui.js` duyệt nguồn, checkbox chọn file và Open theo ngữ cảnh; đích chọn trong dialog.
- Trash chỉ hiện nhóm thư mục/file; click preview bản sao trong trash; menu chuột phải/Shift+F10 cho restore/purge. Không có panel metadata/import trong tab này.
- 17 tests pass, hai file JS qua syntax check, desktop smoke Windows pass. Chưa có test tự động end-to-end mọi thao tác dialog/menu hoặc Linux. Cây trash hiện nhóm theo thư mục ban đầu, không trình bày các bucket ID vật lý.

## Cập nhật storage và preview — 14/11/2026

- Copy import vào `.sb-data/storage`, giữ tên/cây thư mục, không ghi đè; tạo/chọn thư mục và nhập cả cây với báo cáo từng file.
- Path guard giới hạn lifecycle vào storage/trash; nguồn bên ngoài không bị xóa. Trash giữ tên gốc trong bucket ID.
- Preview nhiều tab: text/ảnh, DOCX/PDF trích xuất giới hạn; chưa phải indexing/RAG. Cài python-docx/pypdf vào Python global.
- Bỏ 1 đăng ký legacy chỉ ở metadata; backup DB: `.sb-data/metadata-before-storage-20261114-140725.sqlite3`. Không di chuyển/xóa nguồn.
- 15 tests passed, JS syntax và desktop smoke Windows pass. Chưa tự động hóa native folder/save dialog hoặc test Linux; race với tiến trình bên ngoài và crash import vẫn cần hardening. Crash giữa copy và DB có thể để file chưa đăng ký trong storage, không tự xóa file đó.
- Chưa có MCP/RAG/quản trị quyền; preview hiện mở từng tài liệu rồi giữ tab để chuyển, chưa có chọn hàng loạt bằng checkbox.

## Cập nhật UI theo ảnh tham chiếu

- UI đã đổi theo phong cách ảnh `Second Brain giữa dải ngân hà.png`: tinh vân SVG local, node tia sáng, nhãn nền tối, vòng chọn cyan, panel tab, chip tag, cây thư mục và thanh zoom/pan/vừa khung. Giữ tỷ lệ 70/30.
- Bổ sung lọc tag/thư mục, mở file bằng OS, refresh, chọn lại vị trí, bỏ quản lý, trash/restore/purge với xác nhận UI.
- Restore không ghi đè, có chọn đích khác. File operation có journal trước I/O; copy đích exclusive, verify hash và fsync trước xóa nguồn. Lỗi/crash giữ journal và khóa tài liệu; chưa có UI xử lý recovery, cần kiểm tra thủ công. Chưa chứng minh an toàn trước mọi race với tiến trình ngoài SB.
- Chưa có kéo-thả file: import đang dùng picker, UI không hiển thị lời hứa kéo-thả. Settings hiện chỉ báo thông tin, chưa có màn hình cấp quyền. MCP/RAG vẫn chưa triển khai. Không được coi đã hoàn thành mọi chức năng trong ảnh.
- Kiểm thử sau cập nhật: 11 tests passed; JS syntax pass; desktop smoke Windows pass (bridge, 70/30, background). Chưa có screenshot comparison hoặc test Linux; chưa tự động hóa mọi click/drag/file dialog.

Các mục bên dưới là ghi nhận mốc nền tảng trước cập nhật này; nếu khác thì phần cập nhật trên được ưu tiên.

## Contract triển khai bổ sung

- Ngôn ngữ chính: Python (user chốt). HTML/JS được phép cho UI.
- Lệnh chính: `sb run`, gọi từ CMD global không cần cwd dự án (user chốt).
- Lựa chọn triển khai: pywebview + HTML/CSS/JS, SQLite cho catalog; chưa khóa backend vector/model RAG.
- Entry point cài qua `pip install -e .` trong Python global. Editable install cần giữ source tại đường dẫn đã cài.
- Config resolution: `--config` > `SB_CONFIG` > `config.yaml` tại root source; đường dẫn data tương đối tính theo config, không tính theo cwd.
- Config v1 hiện chỉ validate schema version, data_dir và kiểu agents. Chưa triển khai schema quyền đầy đủ; chưa expose MCP hoặc thao tác ghi/xóa của agent.
- SQLite schema v1: documents/tags/document_tags. ID UUID; canonical path dùng resolve và normcase, đăng ký trùng đường dẫn trả ID hiện có. Không tự phát hiện file trùng nội dung hoặc move/rename.
- Tag: Unicode NFC, trim, casefold cho khóa; giữ tên hiển thị đầu tiên. Tối đa 100 tag/request, 100 ký tự/tag. Cạnh suy ra tag chung.
- Không có thao tác phá hủy file ở mốc này; contract recovery/permission chưa hoàn tất thì không bật trash/purge.

## Đã triển khai

- `sb run`: desktop window HTML/JS, Python bridge local; `sb doctor`: in đường dẫn config/data/runtime.
- UI ngang 70/30, hình nền vũ trụ SVG tự tạo local, node phát sáng.
- Chọn nhiều file qua dialog; đăng ký file gốc, không copy/sửa nội dung; lỗi riêng từng file.
- SQLite persistence, nhận diện đăng ký trùng path, tag editor và tag list, cạnh graph theo tag.
- Tìm tên/path/tag phía UI, chọn node/danh sách và xem đường dẫn/trạng thái file.
- Config tại root, data tại `.sb-data` theo config. Không tạo virtualenv.

## Chưa triển khai — không coi sản phẩm hoàn thành

MCP; quyền/reload config qua UI; RAG/extractors/embedding; full-text search; trash/restore/purge; file watcher/worker; mở file mặc định; graph pan/zoom/layout quy mô lớn; phân trang; folder view; đóng gói standalone. Snapshot hiện kiểm tra file đồng bộ, phù hợp thử nhỏ, chưa đạt mục tiêu hiệu năng kho lớn.

HTML được pywebview phục vụ từ loopback nội bộ; user không cần mở browser. Bridge hiện chỉ cho đăng ký file từ picker, đọc catalog và sửa tag; không có API đọc path tùy ý hoặc xóa file. Cần hardening/kiểm thử bridge trước mở rộng.

## Bằng chứng kiểm thử

- Python global Windows 3.13.5; pywebview 6.2.1 được cài.
- `python -m pytest -q`: 6 passed.
- `cmd.exe /d /c sb doctor` chạy với cwd là thư mục temp: resolve đúng `D:\SecondBrain\config.yaml`.
- `python tests/ui_smoke.py`: cửa sổ thật mở/đóng, bridge tồn tại, CSS columns 548.797px/235.203px (~70/30), ảnh nền universe.svg tải từ loopback.
- `node --check app/second_brain/desktop/app.js`: pass.
- Chưa kiểm thử Linux, chưa test đầy đủ tương tác picker/tag bằng automation hoặc đánh giá hình ảnh thủ công. Smoke không chứng minh toàn bộ UI đạt nghiệm thu.

## Tiếp theo

Hoàn thiện contract quyền/config và file lifecycle; chia nhỏ adapter/use case khi thêm module; bổ sung integration tests. Sau đó triển khai trash an toàn, extraction/retrieval, MCP và UI hoàn chỉnh theo plan.
