# Second Brain — Contracts

Ngày cập nhật: 09/11/2026.
Trạng thái: **chốt yêu cầu/hành vi; đang triển khai từng phần**. Bằng chứng và giới hạn thực tế nằm tại [Implementation_status.md](Implementation_status.md), không suy ra mọi contract đã được thực hiện.

## 1. Mục đích và cách sử dụng

File này lưu các quyết định user đã xác nhận, bao gồm yêu cầu sản phẩm từ các tài liệu hiện có và các contract vừa chốt trước coding. Mục 3 phân biệt rõ những chi tiết kỹ thuật chưa chốt, không biến đề xuất thành yêu cầu đã được duyệt.

Tham chiếu:
- [Second_brain.md](Second_brain.md): đặc tả sản phẩm.
- [Architecture_plan.md](Architecture_plan.md): kiến trúc và mốc triển khai đề xuất.
- [UI_design.md](UI_design.md): yêu cầu UI và đề xuất tương tác.

Contract đã chốt được ưu tiên hơn đề xuất kỹ thuật chưa duyệt. Nếu các tài liệu có mâu thuẫn mới, phải làm rõ và cập nhật đồng bộ, không âm thầm chọn cách diễn giải. Công nghệ, model, tên tool và schema chưa chốt không trở thành bắt buộc chỉ vì xuất hiện trong ví dụ/plan.

## 2. Các contract đã chốt

### C21 — Change background

- Nút `Change background` trên graph mở hộp chọn ảnh của OS.
- Copy ảnh vào thư mục appearance riêng trong data directory; không đăng ký tài liệu, không đưa vào storage/trash.
- Chỉ thay/xóa vĩnh viễn bản background tùy chỉnh SB quản lý sau khi ảnh mới lưu thành công. Không xóa ảnh nguồn user chọn hoặc nền mặc định trong source.
- Lưu lựa chọn qua restart. Ảnh lỗi/hủy picker giữ nguyên nền cũ.
- Implementation: PNG/JPG/JPEG/WebP/BMP/GIF, tối đa 25 MB/20 triệu pixel; chuẩn hóa PNG RGB tĩnh (frame đầu với ảnh động), dùng replace nguyên tử cho một file background.png.


### C20 — Mốc MCP catalog (phạm vi user chọn)

Triển khai MCP cho kho hiện có trước; không gộp embedding/RAG vào lượt này. Lệnh `sb mcp --profile NAME`, stdio local và quyền read/edit/delete giữ nguyên. Contract tool, phân trang, config reload và giới hạn triển khai công bố tại [MCP.md](MCP.md). Một số thao tác folder/journal chưa expose qua MCP; không gọi đây là hoàn thành toàn bộ mục tiêu UI + MCP + RAG.


### C19 — Native picker, cây thư mục và icon (thay thế luồng nhập C18)

- Nút thêm gọi hộp chọn file OS; không có trình duyệt nguồn tự xây. Nút thêm trên toolbar nhập thẳng storage/.
- Thư mục rỗng phải hiện ngay sau khi tạo. Cây thư mục mặc định đóng, click trái mở/đóng.
- Chuột phải thư mục: `add..` nhập file bằng OS vào thư mục đó; `delete` đưa cả cây và nội dung vào trash sau xác nhận. Không có `view` cho thư mục.
- Chuột phải file: `view` preview, `delete` đưa file vào trash. Không xóa nguồn import.
- Thêm/Tạo thư mục là icon nét kiểu New File/New Folder của VS Code, có tooltip và accessible label.
- Native picker hiện chỉ chọn file; quy tắc Open trống để nhập cả thư mục của C18 không còn áp dụng.


### C18 — Nhập chung và thùng rác tối giản (quyết định mới nhất)

- Thêm và Tạo thư mục đặt cùng một khu vực; bỏ nút Nhập thư mục riêng và bộ chọn đích cố định trên panel. Chọn đích trong hộp thoại thao tác.
- Hộp chọn riêng: chọn file rồi Open -> nhập file đã chọn; không chọn file rồi Open -> nhập toàn thư mục hiện tại, đệ quy. Hiển thị rõ đối tượng sẽ nhập trước Open.
- Tab Thùng rác chỉ hiện cây thư mục/file. Không hiện import, tag, đường dẫn, trạng thái hoặc panel chi tiết.
- Click file trash để preview chỉ đọc. Menu chuột phải (hoặc Shift+F10) cung cấp xem, khôi phục, chọn đích khôi phục khác và xóa vĩnh viễn.
- Preview trash đọc bản sao trong trash, không tự khôi phục và không truy cập nguồn import.


### C17 — Storage bản sao và preview (quyết định mới nhất)

C17 thay thế mọi mô tả bên dưới về quản lý trực tiếp file nguồn, xóa nguồn và bỏ quản lý chỉ xóa metadata.

- `.sb-data/storage` (tương ứng `<data_dir>/storage`) là kho tài liệu chính. Import COPY nguồn vào kho; không sửa, di chuyển hoặc xóa nguồn ngoài kho.
- Giữ nguyên tên file, ID chỉ trong metadata. Trash có thể dùng thư mục ID riêng nhưng tên file bên trong giữ nguyên.
- Có tạo/chọn thư mục đích trong storage và nhập toàn thư mục đệ quy, giữ cây nguồn. Không đi theo symlink/junction.
- Trùng tại cùng thư mục đích: không ghi đè/đổi tên, không lưu file đó; tiếp tục file khác và báo từng lỗi. Cùng tên ở thư mục khác được phép.
- Bỏ quản lý được gộp vào Đưa vào thùng rác: di chuyển bản sao storage sang trash, giữ ID/tag để restore. Purge chỉ xóa bản sao trong trash và metadata.
- Restore chỉ về storage, không ghi đè. Chọn đích khác/hủy khi xung đột.
- User chọn bỏ đăng ký cũ và tự nhập lại. Chỉ xóa metadata cũ, không chạm file nguồn; bản ghi ngoài storage bị chặn thao tác file.
- Preview chỉ đọc, nhiều tài liệu qua tab riêng. TXT/MD text, DOCX/PDF text trích xuất, ảnh hiển thị hình; DOC cũ/scan/mật khẩu báo giới hạn. Không thêm trình soạn thảo.
- UI mở ứng dụng mặc định cũng mở bản sao trong storage, không nguồn import.

Triển khai hiện giới hạn preview 20 MB/file, text 200.000 ký tự, PDF 50 trang; đây là giới hạn kỹ thuật được công bố, chưa phải benchmark chất lượng RAG.


### C16 — Quyền rộng true/false (quyết định mới nhất, thay thế C08/C09 về scope và cách chia quyền)

- Mỗi agent có ba công tắc `read`, `edit`, `delete`, giá trị boolean; thiếu quyền mặc định false.
- Áp dụng toàn bộ kho tài liệu đã được SB quản lý; không cấu hình scope theo thư mục/từng tài liệu, không chia quyền nhỏ theo từng tool.
- `read`: xem/tìm/đọc tài liệu và thông tin kho.
- `edit`: thêm tài liệu, bỏ quản lý, gán tag, cập nhật vị trí, làm mới và khôi phục. Không cho sửa nội dung file gốc hoặc cấu hình/provider/quyền.
- `delete`: đưa vào thùng rác và xóa vĩnh viễn; quyền đã cấp là đủ, không hỏi lại từng lần qua MCP.
- User cấp quyền bằng config hoặc UI; UI hiển thị ba công tắc cho từng agent. Agent không tự cấp quyền.
- Quyền áp dụng từ request tiếp theo; config lỗi thì từ chối. Không cần UI đang mở để dùng quyền đã cấp.
- Toàn kho SB không có nghĩa được đọc/xóa đường dẫn tùy ý ngoài kho. Identity vẫn gắn profile launch, không tin agent_id trong tool arguments.
- Các đề cập scope thư mục/tài liệu và `purge.allow` bên dưới là lịch sử bị thay thế bởi C16, không được dùng làm contract triển khai mới.

Ví dụ schema quyền đã thống nhất về ý nghĩa:

```yaml
agents:
  my_agent:
    read: true
    edit: false
    delete: false
```

Không tự chuyển quyền cũ sang quyền rộng hơn. Cấu hình kiểu cũ cần user xem lại trước khi chuyển đổi.


### C01 — Sản phẩm và trách nhiệm

- Bản hoàn thành gồm UI local, MCP và truy xuất hỗ trợ RAG, hoạt động trên Windows/Linux.
- SB quản lý/truy xuất nội dung; agent bên ngoài tạo câu trả lời và thực thi workflow.
- Không có LLM sinh câu trả lời trong SB, workflow engine, OCR, AI sinh tag hay version history trong phạm vi này.
- Không coi demo UI hoặc chỉ có MCP stub là hoàn thành sản phẩm.

**Kiểm chứng:** cả UI, MCP và retrieval hoạt động; không yêu cầu LLM generator để sử dụng kho.

### C02 — File gốc và nhập tài liệu

- Đăng ký file đang có, giữ vị trí gốc; không sao chép file làm nguồn chính mới, không tự sửa nội dung.
- UI thêm tài liệu bằng file, không có ô gõ/dán để tạo nội dung tài liệu.
- Metadata và chỉ mục là dữ liệu riêng/dẫn xuất, không thay thế nguồn gốc và không phải lịch sử phiên bản.

**Kiểm chứng:** sau đăng ký, đường dẫn và nội dung file gốc giữ nguyên; UI không có editor tạo tài liệu.

### C03 — Ma trận định dạng bản đầu

| Phần mở rộng | Quản lý/tag/graph/mở bằng ứng dụng mặc định | Trích xuất/tìm nội dung/RAG |
|---|---|---|
| `.txt`, `.md` | Có | Có, với file đọc/trích xuất được |
| `.docx` | Có | Có, trong giới hạn extractor được công bố |
| `.pdf` có text | Có | Có, trên text trích xuất được |
| `.pdf` scan | Có | Không OCR, không hứa tìm nội dung |
| `.pdf` hỗn hợp | Có | Chỉ phần text trích xuất được; báo giới hạn |
| `.doc` cũ | Có | Không ở bản đầu |
| `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.bmp` | Có | Không OCR/hiểu ảnh |
| Phần mở rộng khác | Chưa nhận ở bản đầu | Không |

File có mật khẩu, hỏng, không truy cập được hoặc extractor lỗi phải có trạng thái rõ; không phá mật khẩu hoặc báo index thành công. Mở file phụ thuộc ứng dụng mặc định của OS; thiếu ứng dụng thì báo lỗi, không coi đó là lỗi làm mất tài liệu. Preview tích hợp chưa chốt.

**Kiểm chứng:** ma trận test từng định dạng; phân biệt file được quản lý với file có thể tìm nội dung.

### C04 — Tag và graph

- User nhập/gán tag; một tài liệu có nhiều tag; UI hiển thị toàn bộ tag hiện có.
- Mỗi tài liệu là một node, hai tài liệu có tag chung thì có liên kết, kể cả khác thư mục.
- Node không chung tag vẫn tồn tại; thay tag làm graph cập nhật.
- Cạnh không biểu thị thứ tự, phụ thuộc workflow hay độ tương đồng embedding.

**Kiểm chứng:** thêm/bỏ tag thay đổi đúng cạnh, node độc lập không biến mất.

### C05 — UI 70/30

- Chia ngang: trái 70% graph, phải 30% khu vực thêm file.
- Graph có nền hình vũ trụ; mỗi node tài liệu hiện hữu sáng như ngôi sao.
- Không thay panel thêm file bằng ô nhập nội dung/chat.
- Tag, tìm kiếm, thư mục/tài liệu và thùng rác vẫn phải truy cập được.

Các màu, hiệu ứng, drag/drop, layout algorithm, tab và asset cụ thể trong `UI_design.md` vẫn là đề xuất cần kiểm chứng.

**Kiểm chứng:** quan sát bố cục và luồng thêm file trên cả hai OS; không nhầm sao nền trang trí với node tài liệu.

### C06 — Vị trí cấu hình

- `config.yaml` nằm trực tiếp tại thư mục gốc dự án: `D:\SecondBrain\config.yaml` trong workspace hiện tại.
- Không tạo thư mục `config/` chứa file, không đặt bản cấu hình thứ hai trong data directory.
- User có thể cấu hình/cấp quyền qua file hoặc UI; UI lưu về cùng file cấu hình.
- MCP/UI phải dùng cùng cấu hình và lõi nghiệp vụ, không có hai chính sách mâu thuẫn.

Schema YAML hoàn chỉnh, resolve đường dẫn khi chạy từ cwd khác và cơ chế reload thuộc phần còn mở.

### C07 — MCP transport và runtime

- Bản đầu dùng **stdio local**; HTTP/remote ngoài phạm vi bản đầu.
- UI, MCP và worker dùng chung lõi/dữ liệu, có thể chạy độc lập.
- MCP hoạt động khi UI không mở; UI hoạt động khi không có agent kết nối.
- MCP cung cấp các chức năng quản lý/truy xuất theo quyền, không thực thi workflow.

**Kiểm chứng:** client khởi chạy và gọi MCP qua stdio khi không có UI; UI và MCP cùng phản ánh dữ liệu đã cập nhật.

### C08 — Identity, scope và quyền

- Profile agent gắn với cấu hình launch do operator quản lý, không tin `agent_id` do tool caller tự khai trong input.
- Có scope đọc rõ; thiếu profile hoặc scope thì từ chối, không mặc định đọc toàn máy.
- Mặc định chỉ đọc trong scope đã cấp; mọi quyền ghi mặc định không cho phép.
- Quyền đăng ký, bỏ quản lý, sửa tag, refresh, đưa vào trash, restore và purge được cấp riêng theo agent/thao tác/scope.
- `allow: true` là cấp phép cho thao tác tương ứng, không phải công tắc ghi chung cho mọi agent.
- User cấp/thu hồi qua config hoặc UI; UI hiển thị agent nào được phép thao tác gì trong phạm vi nào.
- Agent không được tự sửa config, provider hoặc quyền.
- Quyền chỉ kiểm soát truy cập qua SB; không thay thế quyền filesystem của OS và không chống được tiến trình cùng tài khoản có quyền sửa config trực tiếp.

**Kiểm chứng:** agent ngoài scope hoặc thiếu quyền bị từ chối; không thể giả profile qua tool input; UI và file config phản ánh cùng quyền.

### C09 — Purge MCP là quyền cấp trước

**Quyết định xác nhận trực tiếp:** khi user cấp `purge.allow: true`, agent được xóa vĩnh viễn file trong trash thuộc scope **mà không hỏi lại từng lần**.

- Mặc định purge không được cho phép.
- Không yêu cầu `confirm=true`, approval token, dialog duyệt mỗi request hay UI phải đang mở để thực hiện quyền đã cấp.
- Quyền purge không mở rộng scope và không cho phép agent tự cấp thêm quyền.
- UI cấp quyền phải hiển thị rõ quyền xóa vĩnh viễn, không thể hoàn tác bằng SB.
- Đây là quyền quản lý/xóa file, không bổ sung chức năng viết lại nội dung file gốc vào phạm vi sản phẩm.
- Xác nhận khi user trực tiếp bấm purge trên UI là đề xuất UX riêng, không phải gate của MCP.

`purge.allow` mô tả ý nghĩa quyền đã chốt; cấu trúc YAML bao quanh, tên profile/scope vẫn phải hoàn thiện trước implementation.

**Kiểm chứng:** false/thiếu quyền -> từ chối; true + đúng scope + file trong trash -> thực hiện được không hỏi lại; true nhưng ngoài scope -> từ chối.

### C10 — Thùng rác

- Xóa tài liệu qua SB đưa file gốc vào thùng rác riêng của dự án.
- Giữ vô thời hạn, không tự dọn theo thời gian.
- Xóa tiếp trong trash là xóa vĩnh viễn.
- Thùng rác không phải lịch sử phiên bản để hoàn tác sửa nội dung.

Chi tiết transaction/recovery, restore collision và cross-volume move còn phải đóng contract kỹ thuật trước viết thao tác file phá hủy.

### C11 — Embedding và dữ liệu ra ngoài

- Hỗ trợ provider local và API do user cấu hình.
- Chỉ gửi nội dung/query ra API khi user chủ động chọn/cấu hình provider đó.
- Không tự fallback local -> API khi lỗi.
- UI thể hiện provider đang dùng và dữ liệu có thể gửi đi.
- SB trả ngữ cảnh có nguồn; agent tổng hợp câu trả lời.

Model, endpoint contract, chunk size, batch, timeout và cấu hình opt-in chi tiết chưa chốt.

### C12 — Freshness, retrieval và chế độ suy giảm

- Không trả chunk cũ như nội dung hiện hành.
- File thay đổi được đánh dấu stale và reindex; file mất, trong trash hoặc ngoài quyền bị loại khỏi kết quả.
- Semantic search chưa sẵn sàng thì có thể trả keyword-only nếu có dữ liệu hợp lệ và phải báo chế độ suy giảm.
- Kết quả có nguồn, locator, trạng thái index và cách đọc tiếp/phân trang.
- Không âm thầm cắt workflow hoặc coi chunk là toàn bộ hướng dẫn.
- Đổi model/provider không trộn vector thuộc các không gian khác nhau.
- Không gửi query tới API khác để che lỗi provider hiện tại.

**Kiểm chứng:** sửa/xóa file, đổi model, thu hồi scope và lỗi provider đều có test; kết quả không giả vờ index cũ là hiện hành hoặc keyword-only là semantic.

### C14 — Ngôn ngữ và lệnh global (user chốt bổ sung)

- Code chính bằng Python; UI được phép dùng HTML/JS.
- Lệnh mở UI là `sb run`, dùng được từ CMD global, không cần đứng trong thư mục project.
- Cấu hình/assets phải resolve độc lập cwd. UI vẫn mở cửa sổ riêng.
- Lựa chọn triển khai hiện tại là pywebview + HTML/CSS/JS; không còn dùng PySide6 làm baseline UI.

**Kiểm chứng:** cài entry point vào Python global, gọi từ cwd ngoài project; kiểm tra cửa sổ desktop và config đúng nguồn.

### C13 — Quy ước triển khai và test

- Tests nằm trong `D:\SecondBrain\tests`, không rải trong source hoặc ngoài project.
- Coding dùng Python global theo quy ước user; không tự tạo/đổi virtualenv.
- Tài liệu/plan không phải bằng chứng triển khai; kết quả test phải ghi rõ OS và phạm vi thực sự đã chạy.

### C15 — Bổ sung từ ảnh tham chiếu UI

User chọn triển khai giao diện và các chức năng trong ảnh `Second Brain giữa dải ngân hà.png`, không chỉ dựng mockup.

- Khôi phục gặp đích đã tồn tại hoặc thư mục cũ không còn: chọn vị trí/tên mới hoặc hủy; không ghi đè. MCP trả `restore_conflict` và chỉ thử lại với đích trong scope.
- Bỏ quản lý: giữ nguyên file gốc, xóa đăng ký/tag liên kết/chỉ mục của tài liệu. Thêm lại không tự khôi phục tag cũ; không xóa tag của tài liệu khác.
- File di chuyển ngoài SB: user chọn lại vị trí và xác nhận; giữ ID/tag, không tự quét ổ đĩa/ghép file. Từ chối đường dẫn đã thuộc tài liệu khác.
- Quyền config/UI thay đổi áp dụng từ request MCP tiếp theo; config lỗi thì từ chối, không dùng quyền cũ. Thao tác file đang chạy hoàn tất hoặc phục hồi an toàn. UI ghi config nguyên tử.
- Nền tinh vân dựng bằng đồ họa local tương tự ảnh, không dùng nguyên screenshot làm background hoặc tạo tài liệu mẫu giả.

**Trạng thái:** các thao tác catalog/UI đã bắt đầu triển khai; MCP/reload quyền chưa triển khai. Không coi quyết định quyền là chức năng đã có.

## 3. Contract còn cần hoàn thiện trước coding từng phần

Không cần hỏi lại mục tiêu sản phẩm. Các quyết định dưới đây cần có bản thiết kế cụ thể; chỉ hỏi user khi lựa chọn làm thay đổi hành vi, dữ liệu hoặc quyền của họ. Chưa có giá trị kỹ thuật cuối cùng thì không đánh dấu đã chốt.

| ID | Contract còn mở | Cần định nghĩa | Phải hoàn tất trước |
|---|---|---|---|
| O01 | Config schema và reload | Version schema, cấu trúc agent/operation/scope, path resolution, validation, ghi atomic, xử lý config lỗi, thời điểm thu hồi quyền có hiệu lực | Config loader và authorization |
| O02 | MCP API | Tên tool/resource, JSON input/output, error codes, pagination/cursor, giới hạn response, idempotency/retry, stdout protocol vs stderr logs | MCP handlers |
| O03 | File identity/path | ID, canonical path Windows/Linux, symlink, file trùng, move/rename, scope kiểm tra trước/sau resolve | Đăng ký và đọc file |
| O04 | Storage/consistency | Schema, migrations, transaction, khóa liên tiến trình, worker lease, recovery, data directory | Persistence và worker |
| O05 | Trash/restore/purge | State machine, journal, thao tác khác ổ đĩa, đích trùng, partial failure, retry, thứ tự xóa cache/metadata/file | Bất kỳ file operation phá hủy nào |
| O06 | Retrieval response | Chunk/locator schema, fingerprint, freshness check, read continuation, truncated/complete, status/error/degraded | Extractor và retrieval API |
| O07 | Embedding provider | Model local, API tương thích nào, secrets, opt-in scope, timeout/retry, dimensions, đổi generation | Gọi model/API thật |
| O08 | UI state/bindings | DTO/events, trạng thái import/search/selection, loading/error, cập nhật quyền, DPI/min size | UI implementation |
| O09 | Nghiệm thu/hiệu năng | Corpus, query labels, Recall@k/MRR, kho thử, latency/RAM, graph scale và ma trận OS | Khóa baseline và tuyên bố hoàn thành |

### Ưu tiên xử lý

1. O01, O03, O04: nền tảng config, identity và dữ liệu; quyết định framework/database được ghi ADR sau spike.
2. O05 trước triển khai trash/purge; không bắt đầu thao tác phá hủy với semantics chưa rõ.
3. O06, O07 và khung O09 trước retrieval thực tế.
4. O02 trước MCP handlers; O08 trước UI coding, dùng contract lõi chung.

Có thể thực hiện spike công nghệ sau khi user cho phép coding; không cần chốt sẵn mọi con số trước spike. Nhưng phải khóa contract liên quan trước viết module production tương ứng.

## 4. Những phương án CHƯA được coi là đã chốt

- Python đã chốt; UI hiện chọn pywebview + HTML/JS. SQLite catalog đã triển khai; FTS/vector/model/extractor còn cần kiểm chứng.
- `sb run` đã chốt. Tên MCP tool cụ thể, cấu trúc JSON/YAML quyền đầy đủ chưa là contract public cuối cùng.
- Model embedding, endpoint cụ thể, threshold chất lượng/latency chưa được chọn.
- Không chốt cơ chế approval token cho purge; phương án đó đã được thay bằng quyền cấp trước qua config/UI.
- Không thêm editor tạo nội dung, OCR, MCP remote hay LLM generator chỉ vì thuận tiện kỹ thuật.

## 5. Lịch sử quyết định của lượt chốt này

| Quyết định | Kết quả user xác nhận |
|---|---|
| Transport | Stdio local cho bản đầu |
| Phạm vi định dạng | Chấp nhận ma trận tại C03 |
| Quyền ghi/purge | Cho phép purge qua MCP; quyền cấp qua config hoặc UI |
| Ý nghĩa allow | `purge.allow: true` + scope là đủ; không xác nhận từng lần |
| Retrieval stale/degraded | Không dùng chunk cũ làm hiện hành; keyword-only được phép khi công bố suy giảm |

Không coi mọi quyết định trên là chức năng đã có; đối chiếu Implementation_status.md để biết phần đã triển khai. Khi O01–O09 được chốt, chuyển từng quyết định sang mục 2 kèm tiêu chí kiểm chứng và cập nhật các tài liệu liên quan.
