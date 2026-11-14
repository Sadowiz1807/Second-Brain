# Second Brain — Thiết kế UI

Ngày: 09/11/2026. Trạng thái: tài liệu thiết kế trước coding, chưa có UI triển khai.

Tham chiếu: [Đặc tả sản phẩm](Second_brain.md) · [Plan kiến trúc](Architecture_plan.md).

## Cập nhật panel nhập và tab Trash — C18

Hai nút Thêm/Tạo thư mục chung một thanh. Không còn nút Nhập thư mục hoặc form chọn storage trên panel. Hộp thoại Thêm duyệt thư mục: chọn file để nhập file, không chọn file thì Open nhập cây thư mục hiện tại; đích lưu chọn trong dialog. Tạo thư mục có dialog riêng chọn thư mục cha/tên.

Trash chỉ hiện cây thư mục/file, click xem nội dung; các thao tác restore/purge trong menu chuột phải hoặc Shift+F10. Không hiển thị import/metadata/tag/status. C18 thay thế bố cục cũ bên dưới.

## Cập nhật UI storage và preview

Theo C17, import hiện copy vào kho, không đăng ký nguồn ngoài máy. Panel thêm chọn thư mục đích trong storage, Tạo thư mục, Nhập thư mục. Báo rõ copy thành công/lỗi từng file; giữ tên, không ghi đè. Nút Xem nội dung mở preview chỉ đọc, giữ nhiều tài liệu qua tab; ảnh xem trực tiếp, DOCX/PDF xem text có giới hạn. Đóng cửa sổ xem để chọn thêm tài liệu, các tab đã mở vẫn giữ. Mở file là mở bản sao; không có nút bỏ quản lý riêng. Các mô tả “không sao chép” bên dưới là lịch sử bị thay thế.

## 1. Yêu cầu đã chốt

1. Ứng dụng mở bằng lệnh và hiển thị cửa sổ riêng trên Windows/Linux.
2. Bố cục chia **theo chiều ngang, trái 70% — phải 30%**.
3. Vùng trái là không gian chính hiển thị graph, có **nền hình vũ trụ**.
4. Mỗi node tài liệu hiện hữu **phát sáng như một ngôi sao**.
5. Vùng phải là khu vực **thêm file tài liệu**. Không có ô gõ/dán nội dung để tạo tài liệu mới.
6. Tài liệu được đăng ký tại vị trí gốc, không tự sao chép hoặc sửa nội dung.
7. Mỗi tài liệu là một node; cạnh nối chỉ hình thành khi có tag chung. Tài liệu không có tag chung vẫn hiện thành node độc lập.
8. Giữ chức năng quản lý thư mục/tài liệu, tag, tìm kiếm, thông tin nguồn, thùng rác và trạng thái truy xuất.

Các chi tiết màu sắc, tab, thao tác chuột, hiệu ứng và component dưới đây là **đề xuất thiết kế** để hiện thực hóa yêu cầu, không phải các lựa chọn user đã duyệt riêng.

## 2. Bố cục tổng thể

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ Second Brain                           [Trạng thái index] [Cài đặt]      │
├─────────────────────────────────────────────────┬────────────────────────┤
│                  70% chiều ngang                │    30% chiều ngang     │
│ [Tìm kiếm…] [Lọc tag/thư mục]                    │ [Tài liệu] [Thùng rác]│
│                                                 │                        │
│             NỀN HÌNH VŨ TRỤ                     │    [+ Thêm file]       │
│                                                 │  Kéo-thả file vào đây │
│      ✦────────✦                                 │                        │
│       ╲        ╲               ✦                │  Tài liệu đã chọn      │
│        ✦────────✦                               │  Tên / đường dẫn       │
│                                                 │  Tag / trạng thái      │
│                  ✦────────✦                     │                        │
│                                                 │  Danh sách tài liệu    │
│ [−] [+] [Vừa khung] [Về tâm]                     │  và nhóm theo thư mục  │
├─────────────────────────────────────────────────┴────────────────────────┤
│ Đang hiện N/M tài liệu · Bộ lọc · Provider · Tiến độ / lỗi có thể xem     │
└──────────────────────────────────────────────────────────────────────────┘
```

- Tỷ lệ 70/30 áp dụng cho chiều rộng hữu dụng của vùng nội dung, không tính viền cửa sổ và đường phân cách.
- Thanh tiêu đề/trạng thái gọn; không tạo sidebar thứ ba chiếm phần graph.
- Đề xuất giữ tỷ lệ khi resize, không tự chuyển thành bố cục dọc. Chiều rộng tối thiểu cần kiểm chứng theo DPI và độ dài nhãn tiếng Việt.
- Panel phải cuộn nội bộ; đường dẫn dài xuống dòng hoặc rút gọn kèm tooltip/copy đầy đủ, không ép graph thu hẹp.
- Dialog xác nhận/cài đặt chỉ xuất hiện khi cần, không thay đổi bố cục chính mặc định.

## 3. Không gian graph — 70%

### 3.1. Hình nền vũ trụ

- Sử dụng ảnh vũ trụ/tinh vân làm nền, không chỉ dùng màu nền trơn.
- Đề xuất bảng màu tối: xanh đen, tím than, điểm sáng xanh lam/trắng; lớp phủ tối giữ node và chữ rõ trên ảnh.
- Ảnh được đóng gói local cùng ứng dụng, không cần tải từ internet khi mở UI. Asset cụ thể và quyền sử dụng phải được xác định trước phát hành.
- Nền là lớp trang trí, không tham gia graph và không nhận sự kiện chọn tài liệu.
- Sao trang trí trong ảnh phải mờ và nhỏ hơn node thật. Node có hit area, hover và nhãn để không nhầm ảnh nền với tài liệu.
- Đề xuất nền tĩnh cho bản đầu. Parallax, nền động hoặc nhấp nháy liên tục không phải yêu cầu bắt buộc.

### 3.2. Node ngôi sao

Mỗi tài liệu có một tâm sáng và quầng sáng mềm. Các node đang hiển thị đều có ánh sáng nền, không chỉ node được chọn.

| Trạng thái | Biểu hiện đề xuất |
|---|---|
| Bình thường | Lõi trắng/xanh nhạt, halo mềm |
| Hover | Halo rõ hơn; tooltip tên, loại file và tag |
| Được chọn | Viền/halo nổi bật, hiện tên và đồng bộ panel chi tiết |
| Kết quả tìm kiếm | Vòng đánh dấu khác trạng thái chọn, không đổi quan hệ graph |
| Đang lập chỉ mục | Badge tiến trình nhỏ; node vẫn tồn tại |
| File mất/không đọc được | Badge cảnh báo và nhãn trạng thái; không giả là file sẵn sàng |
| Không hỗ trợ trích xuất | Badge thông tin; vẫn là tài liệu được quản lý |
| Trong thùng rác | Không xuất hiện trên graph đang hoạt động |

Ánh sáng chỉ là cách biểu diễn tài liệu, không phải cam kết RAG đã sẵn sàng. Không dùng độ sáng để suy ra độ quan trọng, độ tin cậy hoặc quyền ưu tiên workflow. Trạng thái cần icon/text, không chỉ phân biệt bằng màu.

### 3.3. Cạnh và bố trí node

- Cạnh là đường sáng mảnh, độ tương phản thấp hơn node; chỉ nối tài liệu có tag chung.
- Hai tài liệu chung nhiều tag vẫn dùng một cạnh, có thể xem danh sách tag chung qua tương tác.
- Chọn node làm nổi các cạnh liên quan, giảm nhiễu từ phần còn lại nhưng không thay đổi dữ liệu.
- Không có cạnh từ embedding similarity; kết quả semantic search không tự thêm liên kết.
- Đề xuất layout tự động và ổn định sau cập nhật, tránh toàn bộ graph nhảy vị trí khi thêm một file.
- Node độc lập không bị bỏ qua. Khi graph lớn, lọc hoặc giới hạn view phải hiện số lượng/phạm vi; không âm thầm cắt dữ liệu.

### 3.4. Tương tác đề xuất

- Click node: chọn tài liệu, hiện chi tiết bên phải nhưng giữ nút thêm file dễ truy cập.
- Hover: tooltip ngắn; tên dài không che toàn graph.
- Kéo nền để pan, cuộn để zoom; có nút zoom/vừa khung/về tâm cho người không dùng chuột.
- Nếu cho kéo node, thao tác chỉ đổi vị trí hiển thị, không di chuyển file hay thay tag.
- Mở file qua nút rõ ràng ở panel; không gán hành vi phá hủy vào thao tác click node.
- Kết quả tìm kiếm có danh sách bổ trợ để user không buộc phải tìm bằng thị giác giữa nhiều ngôi sao.

## 4. Panel thêm tài liệu — 30%

### 4.1. Thêm bằng file, không nhập nội dung

Đề xuất khu vực đầu panel gồm:

- Nút **Thêm file** mở bộ chọn file hệ điều hành, hỗ trợ chọn một hoặc nhiều file.
- Vùng **Kéo-thả file tài liệu vào đây** là cách nhập tương đương.
- Nhắc ngắn: “Quản lý file tại vị trí gốc — không tạo bản sao”.
- Danh sách file chờ đăng ký: tên, loại, đường dẫn và lỗi nếu có.
- Chọn/nhập tag và nút xác nhận thêm vào SB.

**Không có:** textarea nội dung, editor Markdown, chức năng dán văn bản để tạo file, chat input hoặc nút yêu cầu SB sinh tài liệu.

Ô nhập tag và ô tìm kiếm vẫn có vì chúng không phải nơi nhập nội dung tài liệu. Chọn hàng loạt/thả file là đề xuất tiện dụng; không coi user đã yêu cầu tự quét thư mục đệ quy. Việc quản lý thư mục phản ánh đường dẫn file được thêm.

### 4.2. Quy trình thêm file

1. User chọn/thả file.
2. UI kiểm tra đường dẫn, khả năng đọc và trùng đăng ký; lỗi hiển thị theo từng file.
3. User gán tag mới hoặc chọn tag hiện có; cho phép thêm tài liệu chưa có tag.
4. Xác nhận đăng ký bằng application service; không sửa nội dung file.
5. Tài liệu đăng ký thành công xuất hiện thành ngôi sao; nếu có tag chung thì có cạnh.
6. Indexing chạy nền, trạng thái hiển thị riêng. File không trích xuất được vẫn được quản lý trong phạm vi định dạng được hỗ trợ.
7. Nếu embedding API đang chọn, UI phải thông báo dữ liệu nào sẽ được gửi và tuân thủ phạm vi cho phép trước khi enqueue tác vụ gửi nội dung.

Không hiện node giả như đăng ký thành công khi thao tác thất bại. Với nhiều file, báo số thành công/lỗi và cho thử lại các file lỗi, không đăng ký trùng các file đã thành công.

### 4.3. Tag và thông tin tài liệu

- Tag editor dạng chip; cho chọn lại tag cũ và xem tất cả tag, kể cả khi chưa chọn node.
- Thêm/bỏ tag cập nhật graph sau khi lưu thành công; lỗi lưu không được thể hiện như đã cập nhật.
- Chi tiết gồm tên file, đường dẫn, định dạng, thư mục, tag, khả năng truy cập và trạng thái index.
- Nút đề xuất: **Mở file**, **Làm mới**, **Bỏ quản lý**, **Đưa vào thùng rác**.
- Không có chỉnh sửa nội dung file trong panel. Nếu có preview về sau, phải là chỉ đọc và công bố định dạng hỗ trợ.

### 4.4. Danh sách và thư mục

- Đề xuất danh sách tài liệu theo nhóm thư mục hoặc bộ lọc thư mục trong panel.
- Chọn dòng tài liệu đồng bộ node graph và ngược lại.
- Danh sách hỗ trợ bàn phím và tên file đầy đủ, không bắt user chỉ dùng graph để điều hướng.
- Khi node nằm ngoài bộ lọc graph, UI báo rõ và cung cấp thao tác hiện tài liệu thay vì giả nó không tồn tại.

## 5. Tìm kiếm và RAG trên UI

- Thanh tìm kiếm gọn đặt ở đầu vùng graph; lọc tag/thư mục và xóa bộ lọc dễ thấy.
- Đề xuất hiển thị kết quả trong tab/panel bên phải; giữ lối quay về thêm file, không mở cột thứ ba.
- Kết quả gồm tên, đoạn liên quan, nguồn/vị trí và trạng thái. Chọn kết quả focus node tương ứng nếu thuộc view hiện tại.
- Hiển thị chế độ keyword/semantic/hybrid thực tế; nếu chỉ chạy keyword thì báo rõ.
- Không trình bày một đoạn tìm được là toàn bộ workflow. Có thao tác đọc thêm/mở file nguồn.
- UI không có hộp chat yêu cầu SB sinh câu trả lời; agent bên ngoài đảm nhiệm tổng hợp.
- Provider lỗi/chưa cấu hình không ngăn user quản lý file; công bố giới hạn tìm kiếm lúc đó.

## 6. Thùng rác và thao tác an toàn

Đề xuất tab Thùng rác trong panel phải, không hiển thị file trash như sao của graph đang hoạt động.

- Hiện tên, vị trí ban đầu, trạng thái và thao tác khôi phục/xóa vĩnh viễn.
- Phân biệt **Bỏ quản lý** (giữ file gốc) và **Đưa vào thùng rác** (di chuyển file gốc).
- Xác nhận thao tác di chuyển/xóa với tên và đường dẫn file, không dùng thông báo mơ hồ “xóa node”.
- Khi user trực tiếp bấm xóa vĩnh viễn trên UI, đề xuất dialog xác nhận và nêu rõ không thể hoàn tác bằng SB. Đây không phải bước xác nhận cho purge qua MCP: agent đã có `purge.allow: true` trong scope được phép thực hiện mà không hỏi lại từng lần.
- Khôi phục bị trùng đích phải hỏi cách xử lý; không tự ghi đè.
- Thùng rác không tự dọn theo thời gian. Lỗi file operation phải còn được nhìn thấy, không chỉ toast thoáng qua.

## 7. Cài đặt và phản hồi trạng thái

**Quyết định mới nhất:** màn hình quyền chỉ có ba công tắc `read`, `edit`, `delete` cho từng agent, áp dụng toàn kho SB. Không có bộ chọn scope thư mục/tài liệu hay công tắc từng tool. `delete` cho phép cả xóa vĩnh viễn không hỏi lại qua MCP; phải cảnh báo rõ khi cấp. C16 trong `contract.md` thay thế mọi mô tả quyền chi tiết còn lưu dưới đây.

- Nút Cài đặt mở dialog, không chiếm cố định phần graph.
- File cấu hình nằm tại root dự án: `D:\SecondBrain\config.yaml`; không tạo thư mục `config/` hay một bản config thứ hai trong runtime data directory.
- Đề xuất dialog hiển thị đường dẫn config đang dùng, provider/model/endpoint và trạng thái indexing; không lộ secret.
- Cấu hình API phải có thông báo nội dung chunk và query có thể được gửi tới endpoint; không tự fallback từ local sang API.
- Quyền của agent do user/operator quản trị, không để thao tác graph hoặc file import ngầm mở quyền ghi MCP.
- Đã chốt: UI hiển thị từng agent, scope và quyền theo thao tác; user có thể cấp/thu hồi quyền qua UI, lưu vào cùng `config.yaml` tại root.
- Quyền ghi mặc định tắt. Cấp `purge.allow: true` phải hiển thị rõ: agent được xóa vĩnh viễn trong scope mà không hỏi lại từng lần. Không yêu cầu UI đang mở để agent sử dụng quyền đã cấp.
- Agent không được tự thay đổi quyền/config/provider. Schema và thời điểm reload quyền cần hoàn thiện theo [contract.md](contract.md).
- Trạng thái nền: đang đăng ký, đang trích xuất, đang embedding, sẵn sàng, chưa cấu hình, stale, lỗi, không hỗ trợ.

## 8. Empty/loading/error states

| Tình huống | Phản hồi UI đề xuất |
|---|---|
| Kho rỗng | Nền vũ trụ còn hiển thị, không tạo node tài liệu giả; hướng dẫn dùng Thêm file |
| Không có kết quả | Nêu bộ lọc/truy vấn, cho xóa bộ lọc |
| Đang tải graph | Chỉ báo tải, không giả rằng kho rỗng |
| Đang indexing | Node đã đăng ký vẫn hiện; trạng thái RAG chưa sẵn sàng |
| File bị mất | Badge và đường dẫn, cho cập nhật vị trí/làm mới theo chức năng được triển khai |
| Thao tác lỗi | Thông báo cụ thể và cách thử lại; không báo thành công |
| Graph bị giới hạn | Hiện N/M và bộ lọc/phạm vi đang áp dụng |
| Ảnh nền không tải được | Nền tối dự phòng và cảnh báo phù hợp; ứng dụng không crash |

## 9. Khả năng sử dụng và hiệu năng

- Tương phản chữ đủ rõ trên nền vũ trụ; panel phải có nền tối ổn định, không đặt form trực tiếp trên tinh vân sáng.
- Focus bàn phím rõ, Tab đi được tới nút/field chính; danh sách tài liệu là cách truy cập thay thế cho graph.
- Không yêu cầu animation liên tục; nếu bổ sung hiệu ứng phải có chế độ giảm chuyển động. Không dùng nhấp nháy mạnh.
- Halo dùng kỹ thuật cache/draw phù hợp, không bắt mỗi node có một hiệu ứng blur nặng; kiểm chứng trên máy mục tiêu.
- Pan/zoom không kích hoạt lại extraction/embedding. Layout lớn và indexing không chặn UI thread.
- Nhãn có thể hiện theo hover/selection/zoom để giảm chồng chữ, nhưng vẫn có danh sách truy cập tên đầy đủ.
- Kiểm tra DPI scaling Windows/Linux, font tiếng Việt và màn hình hẹp. Ngưỡng node/latency phải đo trong M0, không coi thiết kế là bằng chứng hiệu năng.

## 10. Ánh xạ component đề xuất

Trong `app/second_brain/interfaces/desktop/`:

```text
desktop/
├── main_window.py             # Shell 70/30, toolbar, status
├── graph/
│   ├── view.py                # Pan/zoom, selection
│   ├── scene.py               # Đồng bộ nodes/edges và layout
│   └── items.py               # Star node, edge, badges
├── panels/
│   ├── document_import.py     # File picker/drop zone, không editor
│   ├── document_details.py
│   ├── document_list.py
│   ├── tag_editor.py
│   ├── search_results.py
│   └── trash.py
├── dialogs/
│   ├── settings.py
│   └── confirmations.py
├── viewmodels/                # Trạng thái UI và gọi application use cases
└── assets/
    ├── backgrounds/          # Ảnh vũ trụ local có quyền sử dụng
    └── icons/
```

Đây là sơ đồ dự kiến, không cần tạo file rỗng ngay. UI không tự ghi DB hoặc di chuyển file; mọi thao tác qua application service dùng chung với MCP. Tests đặt trong `tests/`, không đặt cạnh module UI.

## 11. Checklist nghiệm thu UI

- [ ] Mở cửa sổ riêng bằng lệnh trên Windows và Linux.
- [ ] Hai vùng ngang 70/30 rõ ràng; không xuất hiện cột thứ ba mặc định.
- [ ] Graph dùng hình nền vũ trụ local; mỗi node đang hiển thị phát sáng như sao.
- [ ] Phân biệt node thật với sao trang trí; kho rỗng không có node giả.
- [ ] Panel phải cho thêm file, không có ô gõ/dán nội dung tạo tài liệu.
- [ ] Đăng ký không sao chép/sửa file gốc; có lỗi riêng cho file không hợp lệ.
- [ ] Node độc lập vẫn hiện, cạnh theo tag đúng và cập nhật khi tag thay đổi.
- [ ] Chọn node/danh sách đồng bộ chi tiết; mở được file nguồn.
- [ ] Tìm kiếm có nguồn và trạng thái thực tế, không có LLM chat nội bộ.
- [ ] Indexing không đóng băng UI; node phát sáng không bị hiểu là RAG đã ready.
- [ ] Trash/restore/purge có thông báo đúng tác động tới file thật.
- [ ] Bộ lọc/phạm vi graph và kết quả bị giới hạn được công bố rõ.
- [ ] Bàn phím, DPI, tương phản và hiệu năng được kiểm tra trên cả hai OS.

## 12. Chi tiết còn cần kiểm chứng

Không còn câu hỏi chặn việc viết tài liệu này. Trước coding/duyệt visual cần xác định asset vũ trụ cụ thể, màu/typography, kích thước tối thiểu, thuật toán layout và ngân sách hiệu năng. Các phần đó là chi tiết thiết kế còn mở; không thay đổi yêu cầu cốt lõi 70/30, node ngôi sao và thêm tài liệu bằng file.
