# Implementation status — 09/11/2026

## Change background

- Thêm nút đúng tên trên thanh điều khiển graph, gọi OS picker lọc ảnh. Python Background validate/decode trước, ghi tạm + fsync + os.replace vào `.sb-data/appearance/background.png` dưới shared lock. Bản cũ bị thay vĩnh viễn, không dùng trash; nguồn và universe.svg giữ nguyên.
- Frontend tải nền đã lưu khi mở UI, cập nhật sau chọn; hủy/lỗi không thay nền. Giới hạn và ảnh động ghi ở C21.
- 23 tests passed, gồm thay nền/persistence/bảo toàn nguồn/ảnh hỏng giữ nền cũ; desktop smoke Windows pass. Chưa tự động kiểm thử thao tác native picker end-to-end hoặc Linux.

## MCP shared lock và thư mục — 14/11/2026

- Thêm `locking.py`/filelock: service mutations của UI/MCP dùng chung khóa data directory, reentrant; MCP khóa cả tool request và recheck quyền sau khi lấy khóa.
- Journal pending chặn mọi mutation, có tool read `get_recovery_status`; không tự suy đoán/xóa dữ liệu để phục hồi. Chưa có automatic recovery hoặc purge folder.
- Thêm MCP import_folder, trash_folder, list_trash_folders, restore_folder; stdio integration test cover cây thư mục và bảo toàn nguồn. Có test multiprocessing xác nhận contender bị chặn và khóa được giải phóng.
- 21 tests passed, UI smoke Windows pass. Chưa test Linux, crash tại mọi điểm I/O, hoặc writer ngoài SB. UI read snapshots không khóa cùng transaction filesystem, có thể tạm hiển thị trạng thái thay đổi; mutations đã serialize. Batch import báo cáo chưa phân trang.

## MCP catalog stdio — 14/11/2026

- User chọn MCP kho hiện có trước, không triển khai RAG trong lượt này. `sb mcp --profile NAME` chạy headless stdio bằng MCP SDK 1.30.0.
- Tools đọc metadata/text có phân trang, tag/graph/folders, import một file, tạo folder, sửa tag, refresh/relink, trash/restore/purge file. Chính sách read/edit/delete reload config mỗi request, fail closed; không tự cấp profile vào config thật.
- Kiểm thử ClientSession SDK với subprocess stdio thật, config/storage tạm: initialize, discovery, import, search/tag, đọc phân trang, revoke delete, restore/purge bảo toàn nguồn, traversal và YAML lỗi. Toàn suite 20 tests pass, UI smoke pass.
- Hướng dẫn client/permission/error/giới hạn tại `docs/MCP.md`. Chưa kiểm thử kết nối app client bên ngoài (Claude/Cursor/Pi), Linux, multi-process writer. Chưa expose folder deletion/restore, recursive import hoặc journal recovery qua MCP; chưa có lock file liên tiến trình. Không coi catalog MCP là hoàn thành sản phẩm/RAG.

## Icon và node ngôi sao — 14/11/2026

- Đã đo WebView trước sửa: button 34×34 CSS px, display block, SVG 22×22. Sau sửa: vùng bấm 34×34, flex căn giữa, SVG 17×17; hai icon chung style. Hợp nhất `.import-box`, bỏ các override !important của toolbar.
- Graph tách sang `desktop/graph.js`: gradient radial dùng chung, core r=2.8, near glow/halo và tia ellipse mảnh, không blur/drop-shadow từng node. Hit target trong suốt r=17; vòng chọn cyan r=12 và focus nét đứt.
- Cạnh mảnh non-scaling, nhấn cạnh liên quan và giảm cạnh khác. Nhãn mặc định chỉ hiện ở <=12 node và zoom >=0.8; hover/focus/selected vẫn hiện. Tooltip giữ tên đầy đủ. Layout và quan hệ tag không thay đổi.
- Pan/zoom chỉ cập nhật transform, không dựng lại graph/tree; node/label được inverse-scale để giữ kích thước màn hình. Chọn node chỉ cập nhật class khi dữ liệu/viewport không đổi, giữ focus.
- Kiểm chứng bằng pywebview thật, fixture trong RAM, không dùng kho thật: ảnh cùng cửa sổ 1280×800 và cùng 9 tài liệu tại `tests/artifacts/before/selected.png`, `tests/artifacts/after/selected.png`; 80 node tại `tests/artifacts/after/dense.png`.
- `tests/ui_visual_check.py`: computed styles, hit testing cách tâm 10px, node DOM identity/focus giữ sau zoom, core rộng ~5.6px sau zoom, Space chọn node đồng bộ panel, pan không thay node, lọc còn 1 node đều pass. 19 pytest pass; desktop smoke pass; ESLint pass. Đây là DOM interaction trong WebView, không phải automation thao tác chuột người thật.
- DPI thực tế máy 100%; đã kiểm tra thêm WebView2 force-device-scale-factor 1.25/1.5, báo devicePixelRatio tương ứng và cùng metrics CSS, ảnh tại `tests/artifacts/scale125`/`scale150`. Không đổi DPI Windows, chưa kiểm tra multi-monitor/native DPI thực 125/150%.
- Chưa kiểm chứng native picker end-to-end trong lượt này (binding nativeAdd/choose_files giữ nguyên), hover bằng chuột thật, tooltip OS, benchmark tải lớn hoặc Linux. Không thay backend/import/storage/tag/trash.

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
