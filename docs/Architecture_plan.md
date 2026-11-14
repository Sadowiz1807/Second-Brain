# Second Brain — Plan kiến trúc trước coding

Ngày: 09/11/2026. Trạng thái: **đang triển khai nền tảng**; xem [Implementation_status.md](Implementation_status.md). Sơ đồ bên dưới là kiến trúc đích, không phải tất cả module đã tồn tại.

Nguồn yêu cầu: [Second_brain.md](Second_brain.md). Quyết định đã xác nhận được tập hợp trong [contract.md](contract.md). Khi có khác biệt với đề xuất trong plan, yêu cầu/contract đã chốt được ưu tiên; không tự coi phương án dưới đây là quyết định của user.

## Cập nhật kiến trúc storage (ưu tiên thay thế mô hình file trực tiếp bên dưới)

- Import qua `storage.py`: copy file/thư mục vào `<data_dir>/storage`, giữ tên/cấu trúc; đích exclusive, báo xung đột từng file; không tác động nguồn.
- `lifecycle.py` chỉ di chuyển/xóa bản sao storage/trash; path guard chặn nguồn ngoài kho. Trash giữ tên file trong thư mục ID riêng.
- `preview.py` đọc bản sao, trả text/ảnh có giới hạn; UI có cửa sổ preview nhiều tab, không render HTML của tài liệu.
- UI thêm chọn thư mục đích, tạo thư mục, nhập thư mục. Bỏ nút bỏ quản lý riêng vì tương đương đưa vào trash.
- Đăng ký cũ bị bỏ metadata theo yêu cầu user; có backup DB trước thay đổi, không xóa nguồn.
- C17 trong `contract.md` thay thế mọi invariant “không copy/file gốc làm nguồn chính” còn lưu ở các phần kế hoạch lịch sử bên dưới.

## 1. Mục tiêu và ranh giới

### Đã chốt

- Sản phẩm hoàn thành gồm ứng dụng cửa sổ riêng trên Windows/Linux, MCP và truy xuất hỗ trợ RAG.
- Quản lý trực tiếp file gốc; metadata/chỉ mục riêng; không tự sửa nội dung và không lưu lịch sử phiên bản.
- Thư mục tác vụ, tag thủ công, graph tài liệu liên kết qua tag, tìm kiếm, thùng rác vô thời hạn và xóa vĩnh viễn.
- SB truy xuất ngữ cảnh và nguồn; agent tạo câu trả lời và thực thi workflow.
- Embedding hỗ trợ local/API do user cấu hình; không tự gửi dữ liệu ra ngoài hoặc fallback sang API.
- Quyền MCP theo từng agent, thao tác và phạm vi; mặc định chỉ đọc trong phạm vi được cấp.
- Unit test và các test khác của dự án nằm trong `tests/`.
- File `config.yaml` đặt trực tiếp tại thư mục gốc dự án; không tạo thư mục `config/` để chứa file cấu hình.
- UI chia ngang 70% graph bên trái, 30% panel thêm tài liệu bên phải; graph có nền hình vũ trụ, node phát sáng như ngôi sao. Thêm tài liệu bằng file, không có ô nhập nội dung để tạo tài liệu.

### Không thuộc mục tiêu này

LLM sinh câu trả lời bên trong SB, OCR, hiểu nội dung ảnh, workflow engine, AI sinh tag, tự phát hiện mọi mâu thuẫn quy tắc, trình soạn thảo đa định dạng và version history.

## 2. Kiến trúc tổng thể đề xuất

Dùng một codebase Python, chia lõi theo lớp và adapter; tránh microservice ở bản đầu.

```text
User -> Desktop UI (HTML/JS webview) --+
                                     |
Agent -> MCP adapter (stdio) -> Policy+-> Application use cases
                                     |        |
CLI / indexing worker ---------------+        v
                                         Domain rules
                                              |
                       Ports: repositories / files / extractors / embedding
                                              |
                       SQLite + FTS / vector index / filesystem / providers
```

- **Domain:** thực thể và quy tắc tài liệu, tag, graph, thùng rác, quyền; không import Qt, MCP SDK hay thư viện embedding.
- **Application:** điều phối use case, giao dịch, kiểm tra quyền và tính mới dữ liệu; chỉ phụ thuộc domain và các port.
- **Infrastructure:** thực hiện lưu trữ, thao tác file, trích xuất, embedding, chỉ mục và cấu hình.
- **Interfaces:** UI, MCP, CLI chuyển đổi input/output; không tự thực hiện nghiệp vụ bỏ qua application.
- **Bootstrap:** khởi tạo dependency và lifecycle; UI/MCP dùng cùng implementation nhưng có thể chạy độc lập.

Không cần local HTTP backend cho bản đầu. MCP stdio chạy như tiến trình do client khởi chạy; UI là tiến trình riêng. Cả hai sử dụng cùng thư mục dữ liệu, schema và giao thức khóa. Đã chốt transport stdio local cho bản đầu; HTTP/remote ngoài phạm vi bản đầu.

## 3. Công nghệ đề xuất và điểm phải kiểm chứng

| Thành phần | Đề xuất | Cổng kiểm chứng trước khi khóa lựa chọn |
|---|---|---|
| Ngôn ngữ | Python 3.11+ | Phiên bản Python global thực tế và dependency trên Windows/Linux |
| UI | pywebview + HTML/CSS/JS, SVG graph | Đã smoke trên Windows; cần Linux, hardening bridge và graph theo quy mô thử |
| Metadata | SQLite, foreign keys, WAL, migrations | Đồng thời nhiều tiến trình, khóa, phục hồi khi crash |
| Từ khóa | SQLite FTS5 | FTS5 khả dụng, tokenization tiếng Việt và truy vấn có lọc quyền |
| Vector | Adapter SQLite vector, ứng viên sqlite-vec | Wheel/extension trên cả hai OS, filter theo quyền và hiệu năng |
| Local embedding | Adapter sentence-transformers | Mô hình đa ngôn ngữ/tiếng Việt, RAM/CPU, chất lượng và license |
| API embedding | Adapter endpoint embedding cấu hình được | Contract API, batch/rate limit, dimensions và chính sách dữ liệu |
| MCP | Python MCP SDK | Pin phiên bản, lifecycle stdio và khả năng tương thích client |
| Extractor | TXT/MD trực tiếp; python-docx; pypdf | Encoding, bảng, heading, nguồn trang/đoạn và file lỗi |
| Cấu hình | YAML được validate; secrets qua môi trường/keyring | Không ghi khóa API vào repo/log |
| Test | pytest; công cụ Qt test khi cần | Chạy trên Windows và Linux |

Đây là baseline để spike, không phải lựa chọn công nghệ đã được user duyệt. Không chốt model embedding hoặc benchmark khi chưa đo. Coding dùng Python global của máy theo quy ước user; không tự tạo virtualenv. Việc tải model/cài dependency sẽ thuộc bước triển khai được duyệt, không thực hiện trong task tài liệu này.

## 4. Mô hình dữ liệu và trách nhiệm lưu trữ

Các nhóm bảng dự kiến:

- `documents`: ID ổn định, đường dẫn gốc, tên, định dạng, folder ID, trạng thái truy cập, fingerprint hiện hành, thời điểm kiểm tra.
- `folders`: thư mục đã đăng ký và phạm vi quản lý; đăng ký thư mục không mặc định quét toàn bộ ổ đĩa.
- `tags`, `document_tags`: tên hiển thị, khóa chuẩn hóa, quan hệ nhiều-nhiều. Đề xuất chuẩn hóa Unicode, trim và casefold cho khóa; giữ tên hiển thị.
- `chunks`: document ID, fingerprint, ordinal, text, locator nguồn, extractor/chunker version.
- FTS và vector index tham chiếu chunk ID; vector kèm provider/model/dimension/index generation.
- `index_jobs`: hàng đợi bền vững, trạng thái/retry, lease của worker.
- `trash_entries`: đường dẫn cũ, vị trí thùng rác, metadata để khôi phục.
- `file_operations`: journal giao dịch file đang thực hiện để phục hồi crash; không chứa lịch sử nội dung.

Cạnh graph được suy ra từ tag chung, không suy ra từ độ tương đồng embedding. Có phân trang/lọc graph; phải báo rõ phạm vi đang hiển thị, không âm thầm bỏ cạnh.

File gốc nằm nguyên tại nơi user lưu. Text/chunk/vector là cache dẫn xuất có thể dựng lại; khi cập nhật phải thay thế dữ liệu cũ, không biến thành kho phiên bản. Cache cũng là dữ liệu nhạy cảm và cần quyền filesystem tương ứng.

## 5. Luồng truy xuất RAG

### 5.1. Lập chỉ mục

1. Đăng ký file và kiểm tra nằm trong phạm vi cho phép; không sao chép file làm nguồn mới.
2. Xác định loại file, đọc an toàn, tính fingerprint và trích xuất văn bản cùng locator.
3. Chia đoạn theo heading/đoạn khi có thể, giữ thứ tự và liên hệ với tài liệu; kích thước/overlap là cấu hình cần đo.
4. Lập FTS; tạo embedding theo provider đã chọn.
5. Chỉ publish generation khi hoàn tất và fingerprint nguồn vẫn khớp; không trộn các model/dimension khác nhau.
6. Hiển thị các trạng thái `pending`, `indexing`, `ready`, `stale`, `unsupported`, `error` độc lập với trạng thái file.

Đã chốt bản đầu nhận `.txt`, `.md`, `.docx`, `.doc`, `.pdf`, `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.bmp`; định dạng khác chưa nhận. Trích xuất/RAG chỉ cho TXT, Markdown, DOCX và PDF có text. DOC cũ, ảnh và PDF scan chỉ được quản lý, không OCR. PDF hỗn hợp chỉ tìm phần text trích xuất được và báo giới hạn; file hỏng/có mật khẩu/không đọc được phải báo trạng thái, không giả đã index thành công.

### 5.2. Truy vấn

1. Xác định principal/quyền, phạm vi thư mục/tài liệu và giới hạn kết quả.
2. Tìm metadata/từ khóa và ngữ nghĩa trên tập tài liệu được phép; đề xuất hybrid search với RRF để hợp nhất ranking.
3. Lọc tài liệu đã trash, mất, không đọc được hoặc có index stale; không dùng chunk cũ làm nguồn hiện hành.
4. Trả `document_id`, tên, locator, đoạn trích, phương thức/rank, fingerprint và trạng thái index. Đường dẫn chỉ trả khi policy cho phép.
5. Cung cấp thao tác đọc tiếp/toàn tài liệu qua phân trang, có `next_cursor`, tổng/phần đã đọc và chỉ báo chưa đầy đủ.

Không coi chunk đơn lẻ là workflow hoàn chỉnh. Agent phải có thể lấy đủ tài liệu gốc hoặc toàn bộ text trích xuất; với nội dung không trích xuất được cần trả trạng thái rõ, không giả định text đã chứa mọi bảng/ảnh.

### 5.3. Provider và dữ liệu ra ngoài

- Cấu hình tách `local` và `api`; chưa cấu hình thì semantic search báo chưa sẵn sàng, metadata/FTS vẫn dùng được.
- Local không gửi nội dung hoặc query ra API embedding. Tải model là thao tác setup riêng có thông báo.
- API chỉ hoạt động sau khi user chủ động cấu hình; UI/config nêu endpoint, model, dữ liệu gửi (chunk và query), cùng phạm vi tài liệu được phép gửi.
- Không log API key, nguyên văn tài liệu/query theo mặc định; cấu hình provider chỉ do user/operator quản trị, không cho agent tự đổi qua tool thường.
- API timeout/rate-limit phải có lỗi và retry giới hạn; có thể trả keyword-only kèm cảnh báo, không giả vờ semantic search thành công.
- Đổi provider/model/dimension tạo generation mới và reindex; không so sánh vector khác không gian. Dọn generation cũ sau chuyển đổi, không giữ làm version history.

## 6. MCP và phân quyền

**Cập nhật ưu tiên:** user đã thay thiết kế quyền chi tiết bên dưới bằng ba boolean `read`, `edit`, `delete` theo agent, áp dụng toàn kho SB. `delete` gồm cả purge không hỏi lại; `edit` gồm đăng ký/bỏ quản lý/tag/relink/refresh/restore. Không chia scope theo thư mục hoặc tài liệu. Xem C16 trong `contract.md`; bảng tool bên dưới chỉ mô tả chức năng, không còn là danh sách quyền riêng cần cấu hình.

Nhóm tool dự kiến (tên sẽ chốt trong contract):

| Nhóm | Tool đề xuất | Chính sách |
|---|---|---|
| Đọc | `list_documents`, `get_document`, `read_document`, `list_tags`, `get_graph` | Đọc trong scope, phân trang |
| Truy xuất | `search_documents`, `retrieve_context`, `get_index_status` | Lọc quyền trước khi trả nội dung; nguồn và trạng thái rõ |
| Quản lý | `register_document`, `unregister_document`, `set_document_tags`, `refresh_document` | Cấp quyền riêng theo thao tác và scope |
| Thùng rác | `list_trash`, `trash_document`, `restore_document`, `purge_document` | Quyền riêng theo agent/thao tác/scope; `purge.allow: true` cấp phép trước, không hỏi lại từng lần |

- `config.yaml` khai báo từng agent, allowed operations, allowed roots/document scopes; default deny ngoài phạm vi được cấp, không mặc định đọc toàn máy.
- Identity gắn với cấu hình launch stdio do operator quản lý, không tin `agent_id` do model tự gửi trong tool arguments. Profile launch không phải ranh giới bảo mật với tiến trình cùng user OS có quyền sửa config/file.
- Chuẩn hóa/resolve path, kiểm tra symlink và scope tại thời điểm sử dụng; không để đường dẫn tùy ý vượt quyền.
- Bộ lọc quyền áp dụng cả nội dung, tên/tag, count, graph và trash; graph không tiết lộ node/edge ngoài scope.
- Resource URI dùng ID tài liệu thay vì cho phép đọc tùy ý path. Input được validate, giới hạn kích thước và phân trang, lỗi có mã ổn định.
- Nội dung lấy từ tài liệu là dữ liệu không đáng tin về quyền thực thi; không được tự kích hoạt tool hoặc vượt policy.
- Đã chốt: quyền ghi cấp qua `config.yaml` hoặc UI; UI hiển thị quyền từng agent và lưu về cùng config. Agent không được tự sửa quyền/provider/config.
- `purge.allow: true` cho agent được xóa vĩnh viễn file trong trash thuộc scope mà không cần xác nhận từng lần; mặc định false. Không có bước duyệt UI hay token xác nhận bắt buộc cho mỗi lần purge MCP. UI cấp quyền phải cảnh báo tác động không thể hoàn tác.
- Không hỗ trợ mở ứng dụng desktop từ agent headless ở baseline; UI có thao tác mở bằng ứng dụng mặc định.

## 7. UI, tiến trình nền và nhất quán dữ liệu

Bố cục UI đã chốt: vùng trái chiếm 70% chiều ngang dành cho graph nền hình vũ trụ, mỗi node tài liệu phát sáng như ngôi sao; vùng phải chiếm 30% dành cho thêm file tài liệu. Không có ô gõ/dán nội dung để tạo tài liệu mới.

Các chức năng thư mục, danh sách tài liệu, chi tiết/nguồn/trạng thái, tag, search/filter, trash và cấu hình vẫn được giữ; đề xuất bố trí trong tab/panel và thanh công cụ thay vì thêm cột thứ ba. Thiết kế đầy đủ: [UI_design.md](UI_design.md).

- UI không chạy extractor/embedding trên main thread; chuyển việc nặng qua job queue.
- Một indexing worker giữ lease trên mỗi data directory; nhiều UI/MCP client có thể enqueue nhưng không tạo worker trùng cho cùng job.
- Đã chốt `sb run` mở UI từ CMD global, độc lập cwd. `sb doctor` đã triển khai; lệnh MCP/worker vẫn cần chốt contract.
- Runtime có thể khởi động worker local nếu chưa có; worker giữ lease và phục hồi job khi tiến trình trước chết. MCP không yêu cầu cửa sổ UI.
- SQLite WAL, giao dịch ngắn, busy timeout và khóa tài liệu dùng chung giữa các tiến trình cho thao tác file. Không giữ DB transaction trong suốt thời gian gọi embedding API.
- File watcher là tối ưu; refresh thủ công và reconciliation lúc startup vẫn cần. Không hứa tự nhận diện mọi move/rename ngoài app.
- Trước đọc/retrieval kiểm tra freshness ứng viên; file thay đổi trong lúc đọc/index phải bị đánh dấu lại. Không trả cache cũ khi file đã mất hoặc quyền bị thu hồi.
- DB trong data directory local, không đặt trên network share ở baseline. Khả năng quản lý nguồn file network cần kiểm chứng riêng.

## 8. Xóa, khôi phục và phục hồi lỗi

- Phân biệt bỏ quản lý (giữ file gốc) và đưa vào trash (di chuyển file gốc); UI/tool ghi rõ tác động.
- Trash là thư mục riêng của SB trong data directory, không phải Recycle Bin OS; giữ vô thời hạn.
- Ghi journal dự định thao tác; giữ khóa tài liệu; di chuyển file; commit metadata/index state; hoàn tất journal.
- Không có transaction nguyên tử chung giữa DB và filesystem: phải có recovery lúc startup và fault-injection test.
- Cùng filesystem ưu tiên rename; khác ổ đĩa dùng copy tới file tạm, verify, hoàn tất đích rồi mới xóa nguồn. Nếu thất bại không báo thành công; ghi trạng thái cần phục hồi, không xóa bản duy nhất.
- Trash loại tài liệu khỏi active graph/search ngay khi trạng thái được commit; chặn truy xuất trong giai đoạn chuyển tiếp.
- Restore kiểm tra đích; không tự ghi đè file khác. Khôi phục metadata/tag và enqueue reindex sau khi file được khôi phục an toàn.
- Purge xóa file trash và dữ liệu dẫn xuất, không tự chạy theo thời gian. Qua MCP, kiểm tra quyền `purge.allow: true` và scope, không hỏi lại từng lần. Với user trực tiếp thao tác trên UI, dialog xác nhận là đề xuất UX riêng, không phải bước duyệt MCP.

## 9. Bố trí thư mục dự kiến

Cây dưới đây là kế hoạch; chưa tạo các module rỗng trong task này.

```text
SecondBrain/
├── .agent/
│   ├── overview.md
│   └── rule_coding.md
├── docs/
│   ├── Second_brain.md            # Yêu cầu sản phẩm đã chốt
│   ├── Architecture_plan.md       # Plan này
│   ├── UI_design.md               # Bố cục 70/30, graph vũ trụ, panel thêm file
│   ├── contract.md                # Quyết định đã chốt và contract còn mở
│   ├── adr/                       # Quyết định công nghệ sau spike
│   ├── contracts/                 # MCP, config, lỗi và quyền
│   └── testing/                   # Ma trận định dạng/OS, đánh giá RAG
├── app/
│   └── second_brain/
│       ├── __init__.py
│       ├── __main__.py
│       ├── bootstrap.py           # Dependency composition, lifecycle
│       ├── domain/
│       │   ├── documents.py
│       │   ├── tags.py
│       │   ├── graph.py
│       │   ├── trash.py
│       │   └── permissions.py
│       ├── application/
│       │   ├── ports/             # Repository, file, extractor, embedding contracts
│       │   ├── dto/               # Input/output độc lập UI/MCP
│       │   └── services/          # Documents, tags, graph, search, indexing, trash
│       ├── infrastructure/
│       │   ├── persistence/       # SQLite repositories và migrations/
│       │   ├── filesystem/        # Path guard, locking, watcher, trash operations
│       │   ├── extraction/        # TXT, Markdown, DOCX, PDF adapters
│       │   ├── retrieval/         # Chunking, FTS, vector adapter, ranking
│       │   ├── embedding/         # Local/API adapters, batching
│       │   ├── jobs/              # Queue, lease, worker, recovery
│       │   └── configuration.py   # Đọc/validate YAML; không phải thư mục config
│       └── interfaces/
│           ├── cli/               # Entry commands
│           ├── desktop/           # Qt windows, views, viewmodels, assets
│           └── mcp/               # Server, tools, resources, auth context
├── tests/
│   ├── unit/                      # Domain và use cases với fake ports
│   ├── integration/               # DB, file ops, providers, MCP và concurrency
│   ├── e2e/                       # Desktop và agent-client workflows
│   ├── retrieval/                 # Corpus nhỏ, query/qrels, kiểm tra nguồn
│   ├── fixtures/                  # File tổng hợp; không chứa tài liệu cá nhân
│   └── conftest.py
├── scripts/                       # Dev/build/check helpers; không đặt test ở đây
├── config.yaml                   # Cấu hình thực tế tại root; không chứa secret
├── config.example.yaml           # Mẫu tại root, không chứa đường dẫn cá nhân
├── pyproject.toml                 # Package mapping tới app/, CLI entrypoint, pytest
├── README.md                      # Setup, chạy UI/MCP và giới hạn
└── .gitignore
```

`config.yaml` nằm tại `D:\SecondBrain\config.yaml` trong workspace hiện tại, không nằm trong data directory. Đề xuất không commit cấu hình cá nhân; chỉ commit `config.example.yaml`. UI, MCP và worker phải resolve cùng đường dẫn config tuyệt đối, không phụ thuộc thư mục làm việc của MCP client. Khi triển khai bản đóng gói, cơ chế chỉ định đường dẫn config cần được kiểm chứng; không tự chuyển file sang một thư mục config khác.

Không tạo module chỉ để khớp sơ đồ khi chưa có trách nhiệm cụ thể. `application` không phụ thuộc `interfaces`/`infrastructure`; adapter có thể phụ thuộc port và domain. Tránh hai implementation nghiệp vụ riêng cho UI và MCP.

### Dữ liệu runtime — ngoài source tree

Đề xuất dùng `platformdirs` để chọn vị trí theo OS, cho phép user cấu hình data directory:

```text
<SB_DATA_DIR>/
├── metadata.sqlite3              # Metadata, FTS, chunk và vector nếu adapter hỗ trợ
├── trash/                        # Tên theo ID; không xung đột tên file
├── cache/                        # Dữ liệu trích xuất tạm, có thể tái tạo
├── models/                       # Model local hoặc tham chiếu cache được cấu hình
├── locks/
└── logs/                         # Không log nội dung/secret theo mặc định
```

Secrets nằm ngoài YAML/source; file gốc nằm tại đường dẫn user đăng ký. Nếu spike chọn vector store riêng, bổ sung `indexes/` và contract đồng bộ/rebuild; không tự đổi kiến trúc lưu trữ mà thiếu ADR.

## 10. Các mốc triển khai sau khi duyệt plan

### M0 — Khóa contract và kiểm chứng rủi ro
- [x] Chốt stdio local và ma trận định dạng bản đầu trong `contract.md`.
- [ ] Duyệt baseline stack và cách triển khai provider.
- [ ] Spike webview/SVG graph, vector extension, local embedding, FTS tiếng Việt trên Windows/Linux.
- [x] Chốt nguyên tắc profile/scope, quyền cấp trước qua config/UI, purge không hỏi lại khi được cấp, và RAG không trả cache cũ như dữ liệu hiện hành.
- [ ] Hoàn thiện schema scope/config, reload quyền, input/output/error MCP và cơ chế API opt-in; các mục này chưa được coi là đã triển khai.
- [ ] Xây corpus tổng hợp, kích thước kho thử và ngân sách RAM/latency; ghi ADR.

Điều kiện qua mốc: không còn blocker nền tảng; các lựa chọn được ghi rõ thay vì giả định đã chạy được.

### M1 — Nền tảng quản lý tài liệu
- [ ] Package/CLI/config/migrations, domain và repository ports.
- [ ] Đăng ký, bỏ quản lý, thư mục, tag, graph; kiểm tra đường dẫn/quyền.
- [ ] Unit/integration test và lưu trữ bền vững sau restart.

### M2 — File lifecycle và trash
- [ ] Trạng thái file, refresh, journal, khóa và recovery.
- [ ] Trash/restore/purge; thử lỗi giữa các bước, khác ổ đĩa và đích trùng.
- [ ] Chứng minh không tự ghi đè hoặc làm mất bản file duy nhất trong các ca đã thử.

### M3 — Search và RAG
- [ ] Extractors, chunk locator, FTS, local/API embedding và vector generations.
- [ ] Queue/worker lease, refresh/reindex, hybrid retrieval và full-read pagination.
- [ ] Kiểm thử chất lượng, nguồn, stale data, API opt-in và lỗi provider.

### M4 — MCP
- [ ] Stdio server, tools/resources, profile binding, quyền và error contract.
- [ ] Kiểm thử bằng MCP client thật: đọc/tìm/RAG, write được cấp và write bị từ chối.
- [ ] Chặn rò rỉ scope trong snippet/count/tag/graph, traversal và tool input giả danh.

### M5 — Desktop UI
- [ ] Triển khai bố cục ngang 70/30, nền hình vũ trụ và node ngôi sao theo `UI_design.md`.
- [ ] Panel thêm file không có ô nhập nội dung tài liệu; hoàn thiện folder/document views, tag, search, trash và provider/index status.
- [ ] Khởi chạy cửa sổ riêng; mở file bằng ứng dụng mặc định; thao tác nặng không khóa UI.
- [ ] UI và MCP chạy đồng thời và nhìn thấy cùng trạng thái dữ liệu.

### M6 — Nghiệm thu và hướng dẫn chạy
- [ ] Kiểm thử Windows/Linux, đóng gói/cài đặt và startup/recovery.
- [ ] Đối chiếu toàn bộ mục 10 trong đặc tả; không chỉ kiểm tra demo UI.
- [ ] Công bố support matrix, giới hạn, benchmark và cách cấu hình MCP/provider.

MCP/RAG là điều kiện hoàn thành sản phẩm, dù được xây sau lõi. Chưa có ước lượng thời gian đáng tin trước M0.

## 11. Chiến lược kiểm thử và nghiệm thu

- **Domain:** quan hệ tag/graph, nhiều tag chung không sinh cạnh trùng, node độc lập, quyền mặc định.
- **File safety:** missing/unreadable, rename ngoài app, symlink, Unicode/case đường dẫn, disk full, crash/copy lỗi, restore collision và purge.
- **Concurrency:** hai MCP session + UI + worker, job lease hết hạn, retry idempotent, migration lock.
- **Retrieval:** query tiếng Việt, lexical/semantic/hybrid, locator đúng, phân trang không mất đoạn, không trả trash/stale/ngoài scope.
- **Privacy:** local mode không gọi embedding API; API mode chỉ gửi phạm vi được cho phép; logs không chứa secret/nội dung.
- **Providers:** mock cho test deterministic; smoke test local thật/API thật là bài opt-in dùng dữ liệu tổng hợp, không dùng tài liệu cá nhân.
- **RAG quality:** đo Recall@k/MRR trên tập query–tài liệu gán nhãn, độ đúng citation và latency. Ngưỡng chấp nhận phải chốt ở M0, không tự bịa số liệu.
- **Desktop/MCP e2e:** thêm file -> tag -> graph -> tìm -> đọc -> trash -> restore; agent bị từ chối thao tác thiếu quyền.
- **Cross-platform:** chạy suite trên cả Windows và Linux; kết quả một OS không được báo là chứng minh cả hai.

## 12. Rủi ro và quyết định còn cần khóa

1. Vector backend/model chưa kiểm chứng khả năng cài đặt và hiệu năng thực tế.
2. File gốc có thể đổi ngoài ứng dụng; watcher không bảo đảm nhận mọi sự kiện, cần reconciliation và kiểm tra lúc sử dụng.
3. Giao dịch file + DB không nguyên tử; cần journal/recovery, không chỉ try/except.
4. Graph theo tag phổ biến có thể rất dày; phải lọc/paginate minh bạch.
5. API embedding tạo ranh giới dữ liệu ra ngoài; cấu hình opt-in cần hiểu được, không chỉ một field kỹ thuật.
6. Stdio profile là cách gán chính sách cho client tin cậy, không chống được tiến trình cùng tài khoản OS cố sửa cấu hình.
7. Khả năng trích xuất Word/PDF không đồng nghĩa giữ nguyên mọi layout/bảng; phải công bố giới hạn và giữ đường truy cập file gốc.

Bước tiếp theo sau duyệt tài liệu: thực hiện M0, cập nhật ADR và contract, rồi mới triển khai các mốc coding. Không coi plan là bằng chứng đã có source hoặc test chạy thành công.
