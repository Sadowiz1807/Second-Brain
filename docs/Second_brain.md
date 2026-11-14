# Second brain

Mô tả dự án — cập nhật ngày 09/11/2026.

Cập nhật phạm vi: giữ ứng dụng cửa sổ riêng và đưa MCP cùng truy xuất hỗ trợ RAG vào mục tiêu hoàn thành. SB truy xuất ngữ cảnh; agent tạo câu trả lời. Embedding hỗ trợ local và API do user cấu hình.

Tài liệu tổng hợp các yêu cầu đã thống nhất. Các mục ghi “đề xuất kỹ thuật” là phương án triển khai để xem xét, không phải quyết định đã chốt của user.

## Cập nhật ưu tiên — kho storage bản sao

Yêu cầu mới thay thế mô hình quản lý trực tiếp file nguồn trong các mục lịch sử bên dưới: import copy vào `.sb-data/storage`, giữ tên file/cây thư mục, mọi thao tác chỉ trên bản sao. Không tác động nguồn import. Trùng đường dẫn đích thì bỏ qua file đó và báo lỗi, tiếp tục batch. Cho tạo thư mục, nhập cả thư mục, preview nhiều tab chỉ đọc. Bỏ quản lý gộp thành đưa bản sao vào trash. Đăng ký cũ được bỏ metadata để user nhập lại. Chi tiết có hiệu lực: C17 trong [contract.md](contract.md).

## 1. Mục tiêu

Second brain (SB) là kho ghi nhớ cá nhân chạy local, tập hợp workflow, ghi chú, quy tắc ứng xử và tài liệu tham khảo mà user muốn agent sử dụng.

Thay vì thiết lập lặp lại nội dung cho từng agent, user tổ chức tài liệu trong một kho chung. Định hướng sử dụng là agent tìm thông tin phù hợp khi bắt đầu xử lý yêu cầu, đọc hướng dẫn và thực hiện công việc theo nội dung đó.

SB chịu trách nhiệm lưu thông tin quản lý, truy cập tài liệu, tìm kiếm và hiển thị. Agent bên ngoài chịu trách nhiệm hiểu và thực thi workflow. SB không phải hệ thống tự chạy các bước của workflow.

## 2. Phạm vi phát triển hiện tại

- Xây dựng source code cho ứng dụng local gồm UI, lõi quản lý tài liệu, MCP và truy xuất hỗ trợ RAG.
- Hỗ trợ Windows và Linux.
- Quản lý trực tiếp tài liệu hiện có trên máy user.
- Tổ chức tài liệu theo thư mục tác vụ, gán tag và hiển thị graph.
- Mở giao diện bằng lệnh terminal/CMD, hiển thị trong cửa sổ ứng dụng riêng; không yêu cầu user mở trang localhost trong trình duyệt.
- Có thùng rác riêng của dự án.
- Không lưu lịch sử phiên bản tài liệu.

MCP và truy xuất hỗ trợ RAG thuộc phạm vi bắt buộc của bản hoàn thành, không còn để giai đoạn tương lai. UI và MCP sử dụng cùng lõi quản lý tài liệu; MCP có thể phục vụ agent mà không cần mở UI.

Bản release cần hoàn thiện cả UI, MCP và truy xuất RAG, không chỉ là giao diện demo. Có thể triển khai theo từng mốc, nhưng hoàn thành một mốc riêng không đồng nghĩa hoàn thành sản phẩm.

## 3. Nguyên tắc tài liệu

### 3.1. Giữ tài liệu gốc

- User cung cấp tài liệu có chất lượng, nội dung rõ ràng và phù hợp để sử dụng.
- SB giữ nguyên tài liệu gốc, không tự viết lại, diễn giải hoặc sửa nội dung.
- Không yêu cầu xây dựng cơ chế AI đánh giá chất lượng tài liệu.
- Workflow, ghi chú và quy tắc có thể viết bằng ngôn ngữ tự nhiên.
- Không bắt buộc chuyển workflow thành JSON/YAML hoặc một ngôn ngữ thực thi riêng.
- Khi có dữ liệu trích xuất hoặc chỉ mục, chúng chỉ phục vụ đọc và tìm kiếm; tài liệu gốc vẫn là nguồn nội dung chính thức.

### 3.2. Định dạng

Kho cần tiếp nhận tài liệu dạng text và ảnh. Các định dạng được nêu trong yêu cầu gồm TXT, Markdown, Word và PDF; có thể mở rộng sau.

Ảnh trước mắt được quản lý như file tài liệu. OCR và hiểu nội dung ảnh chưa thuộc yêu cầu hiện tại. Khả năng tiếp nhận một file không đồng nghĩa với việc đã hỗ trợ tìm kiếm toàn bộ nội dung của định dạng đó.

Đã chốt bản đầu nhận các phần mở rộng `.txt`, `.md`, `.docx`, `.doc`, `.pdf`, `.jpg`, `.jpeg`, `.png`, `.gif`, `.webp`, `.bmp`; định dạng khác chưa nhận. Trích xuất/tìm nội dung/RAG chỉ cho TXT, Markdown, DOCX và PDF có text. DOC cũ, ảnh và PDF scan được quản lý nhưng không OCR/tìm nội dung. PDF hỗn hợp chỉ tìm phần text trích xuất được và công bố giới hạn. File có mật khẩu, hỏng hoặc không đọc được báo trạng thái rõ; không tự phá mật khẩu hay báo index thành công. Khả năng xem trước cụ thể còn là lựa chọn kỹ thuật.

## 4. Lưu trữ và tổ chức thư mục

### 4.1. Sử dụng trực tiếp file hiện có

SB sử dụng trực tiếp file tại vị trí user đang lưu, không mặc định sao chép toàn bộ vào một kho mới. Tài liệu thuộc cùng tác vụ nằm trong cùng thư mục theo cách user tổ chức.

Việc thêm một tài liệu vào SB có nghĩa là ghi nhận tài liệu đó để quản lý. Việc sửa file gốc sẽ thay đổi nội dung mà SB đọc. SB không giữ một bản sao độc lập làm nguồn nội dung chính.

SB cần lưu metadata như định danh, vị trí file và tag mà không làm thay đổi nội dung gốc. Cách lưu metadata là quyết định kỹ thuật, chưa chốt định dạng hay database.

### 4.2. Đồng bộ trạng thái file — đề xuất kỹ thuật

- Khi file thay đổi bên ngoài SB, cập nhật thông tin quản lý và chỉ mục bị ảnh hưởng.
- Khi file mất hoặc không truy cập được, hiển thị trạng thái rõ ràng; không báo rằng tài liệu vẫn sẵn sàng.
- Có cách làm mới dữ liệu và cập nhật vị trí khi user di chuyển file.
- Dùng ID tài liệu độc lập với tên hiển thị để thuận tiện quản lý metadata.

Cách theo dõi thay đổi, xử lý đổi tên và nhận diện file trùng cần được thiết kế sau. Không mặc định đã có khả năng theo dõi mọi thao tác bên ngoài ứng dụng.

## 5. Tag và graph

### 5.1. Tag

- User nhập và gán tag cho tài liệu.
- UI phải có khu vực nhập tag và hiển thị tất cả tag hiện có.
- Một tài liệu có thể có nhiều tag.
- User có thể chọn lại tag hiện có để sử dụng nhất quán.
- Không mặc định sinh tag bằng AI.

### 5.2. Graph

- Một tài liệu là một node.
- Hai tài liệu có ít nhất một tag chung thì có liên kết.
- Tài liệu ở các thư mục khác nhau vẫn có thể liên kết qua tag chung.
- Tài liệu không có tag chung vẫn tồn tại dưới dạng node riêng.
- Liên kết biểu thị sự liên quan qua tag; không tự mang ý nghĩa thứ tự thực hiện, phụ thuộc hay quyền ưu tiên.
- Graph phản ánh thay đổi khi user gán hoặc bỏ tag.

Đề xuất kỹ thuật: lưu quan hệ tài liệu–tag và suy ra các cạnh khi truy vấn hoặc hiển thị. Có thể lọc theo thư mục/tag khi graph lớn; việc lọc không làm mất quan hệ đã xác định trong dữ liệu.

## 6. Truy cập và tìm kiếm

User cần tìm và mở được tài liệu đã quản lý. Đề xuất cho giai đoạn source là tìm theo tên, tag, thư mục và nội dung văn bản đối với những định dạng đã hỗ trợ trích xuất.

SB không cần quét và phân tích lại toàn bộ kho trong mỗi lần tìm. Có thể tạo chỉ mục từ nội dung đã đọc và cập nhật khi file thay đổi. Cấu trúc chỉ mục, database và số liệu hiệu suất sẽ được chọn qua thử nghiệm, không ấn định từ tài liệu mô tả này.

Truy xuất hỗ trợ RAG là yêu cầu hiện tại: SB trích xuất văn bản từ các định dạng được hỗ trợ, chia đoạn, lập chỉ mục và tìm ngữ cảnh liên quan kèm nguồn cho agent. SB hỗ trợ tìm kiếm ngữ nghĩa bằng embedding; agent bên ngoài tổng hợp câu trả lời. Không yêu cầu tích hợp LLM sinh câu trả lời trong SB.

Embedding hỗ trợ cả mô hình local và dịch vụ API theo cấu hình user. Chỉ gửi nội dung tài liệu hoặc truy vấn ra API khi user chủ động chọn và cấu hình provider đó; không tự chuyển từ local sang API khi lỗi. Cần hiển thị rõ provider đang dùng và phạm vi dữ liệu gửi đi. Mô hình, thuật toán kết hợp tìm kiếm và cấu hình xử lý cụ thể là lựa chọn kỹ thuật cần kiểm chứng.

Đã chốt: không dùng chunk cũ làm ngữ cảnh hiện hành; file thay đổi phải đánh dấu stale và reindex. File mất, trong trash hoặc ngoài quyền bị loại khỏi kết quả. Semantic search chưa sẵn sàng thì có thể trả keyword-only nếu có dữ liệu hợp lệ, nhưng phải báo rõ chế độ suy giảm. Đổi model/provider không trộn vector khác không gian; không tự fallback sang API.

Chỉ mục là dữ liệu dẫn xuất, không thay thế file gốc và không phải lịch sử phiên bản. Kết quả cần có nguồn, vị trí đoạn và trạng thái độ mới; không trình bày dữ liệu cũ như nội dung hiện hành. Tài liệu không có văn bản trích xuất được vẫn có thể được quản lý nhưng không được quảng bá là hỗ trợ RAG nội dung.

Khi truy xuất cho agent, cần phân biệt:

- Tìm tài liệu: có thể trả thông tin mô tả và đoạn phù hợp.
- Thực hiện workflow: cung cấp đủ hướng dẫn, điều kiện và ngoại lệ; không mặc định một chunk tìm được đã là toàn bộ quy trình.
- Trả lời từ tài liệu tham khảo: trả nội dung liên quan kèm thông tin nguồn.

## 7. Giao diện ứng dụng

Giao diện được mở bằng `sb run` từ CMD global, không cần đứng trong thư mục dự án, và xuất hiện như một cửa sổ ứng dụng riêng trên Windows/Linux. Code chính bằng Python; UI được phép dùng HTML/JS. Triển khai hiện chọn pywebview để hiển thị HTML/CSS/JS trong cửa sổ riêng.

Bố cục đã chốt:

- Chia cửa sổ theo chiều ngang thành hai vùng: 70% bên trái và 30% bên phải.
- Vùng 70% là không gian graph chính, nền là hình vũ trụ. Mỗi node tài liệu hiện hữu phát sáng như một ngôi sao; các cạnh vẫn biểu thị quan hệ tag chung.
- Vùng 30% là khu vực user thêm file tài liệu. Không có ô gõ/dán nội dung để tạo tài liệu mới.
- Thêm file là đăng ký file hiện có, không tự sao chép hoặc thay đổi nội dung file gốc.

Các khu vực/chức năng cần có, được bố trí trong hai vùng và các điều khiển phụ:

- Danh sách thư mục tác vụ và tài liệu.
- Thông tin tài liệu, vị trí file và thao tác mở tài liệu.
- Khu vực nhập/gán tag và danh sách tất cả tag hiện có.
- Graph liên kết các tài liệu qua tag.
- Tìm kiếm và bộ lọc.
- Thùng rác của dự án.

Không xây ô nhập nội dung hoặc trình soạn thảo tạo tài liệu trong phạm vi UI này. Ô tìm kiếm và ô nhập tag là điều khiển metadata, không phải ô nhập nội dung tài liệu. Cách xem trước và mở file được mô tả trong [UI_design.md](UI_design.md); các chi tiết được đánh dấu đề xuất chưa phải quyết định đã chốt.

## 8. Xóa và thùng rác

Quy tắc đã chốt:

1. Xóa tài liệu thông qua SB đưa tài liệu vào thùng rác của dự án.
2. Thùng rác giữ tài liệu vô thời hạn, không tự dọn theo thời gian.
3. Xóa tiếp tài liệu trong thùng rác là xóa vĩnh viễn.

Vì SB dùng file hiện có, thao tác xóa tài liệu cần được thể hiện rõ là tác động tới file gốc, không chỉ ẩn node trên graph.

Đề xuất kỹ thuật:

- Tách “bỏ quản lý trong SB” với “đưa file vào thùng rác” để tránh nhầm lẫn.
- Lưu vị trí ban đầu và metadata cần thiết để khôi phục.
- Tài liệu trong thùng rác không xuất hiện trong kết quả tìm kiếm và graph đang hoạt động.
- Khi khôi phục mà vị trí cũ đã có file khác, yêu cầu chọn cách xử lý thay vì tự ghi đè.
- Khi di chuyển file thất bại, giữ nguyên file và thông báo lỗi; không đánh dấu đã xóa thành công.

Không có lịch sử phiên bản: chỉnh sửa nội dung không tạo bản cũ để hoàn tác. Thùng rác phục vụ việc xóa, không phục vụ khôi phục một lần chỉnh sửa.

## 9. Tích hợp agent và MCP

MCP là giao diện truy cập bắt buộc của sản phẩm hoàn thành, cung cấp các nhiệm vụ quản lý và truy xuất của SB theo quyền từng agent. MCP không thay thế UI và không thực thi workflow thay agent. Đã chốt bản đầu dùng stdio local, không triển khai HTTP/remote; UI, MCP và worker dùng chung lõi/dữ liệu, có thể chạy độc lập.

### 9.1. Vai trò

- Agent tìm tài liệu phù hợp khi bắt đầu xử lý yêu cầu của user.
- Agent đọc workflow/quy tắc/tài liệu và tự thực hiện công việc.
- SB cung cấp nội dung và thông tin liên quan qua MCP, gồm tìm kiếm ngữ nghĩa, đoạn trích có nguồn và cách đọc đầy đủ tài liệu; không thực thi workflow thay agent.
- Agent tạo câu trả lời từ ngữ cảnh SB cung cấp; SB không tự gọi LLM để sinh câu trả lời.
- UI và MCP dùng chung quy tắc quản lý tài liệu, tag, graph, tìm kiếm và thùng rác. Thao tác không phù hợp với tiến trình headless, như mở cửa sổ ứng dụng mặc định của hệ điều hành, không bắt buộc cung cấp qua MCP.
- Hành vi chủ động tra cứu cần được thiết lập ở phía agent; chỉ kết nối MCP không bảo đảm agent luôn gọi công cụ.

### 9.2. Quyền

- Mặc định agent được đọc trong phạm vi cho phép.
- Thao tác thay đổi phải được cấp quyền.
- Quyền cấu hình riêng theo agent trong file `config.yaml`; không dùng một công tắc ghi chung cho tất cả agent.
- File `config.yaml` đặt trực tiếp tại thư mục gốc dự án (`D:\SecondBrain\config.yaml` trong workspace hiện tại), không tạo thư mục `config/` để chứa cấu hình.
- Cấu hình cần đủ chi tiết để phân biệt thao tác và phạm vi tài liệu. Profile/scope không được khai báo thì từ chối; không mặc định đọc toàn máy.
- Profile agent gắn với cấu hình launch do operator kiểm soát, không tin `agent_id` trong tool input.
- Quyền đăng ký, bỏ quản lý, sửa tag, refresh, trash, restore và purge được cấp riêng; quyền ghi mặc định không cho phép.
- User cấp quyền qua config hoặc UI; UI hiển thị quyền từng agent và lưu về cùng `config.yaml`. Agent không được tự sửa config/provider/quyền.
- `purge.allow: true` cho phép agent xóa vĩnh viễn file trong trash thuộc scope, không cần hỏi lại từng lần. Mặc định false; đây là cấp phép trước, không phải xác nhận mỗi thao tác.

Schema quyền, cơ chế reload và contract lỗi sẽ được thiết kế trước khi triển khai lớp truy cập agent. Chính sách của SB chỉ kiểm soát truy cập đi qua SB; quyền đọc/ghi file trực tiếp của tiến trình khác còn phụ thuộc quyền hệ điều hành.

### 9.3. Xung đột quy tắc

Nội dung quy tắc không bị giới hạn vào một nhóm chủ đề cố định. Khi phát hiện mâu thuẫn, định hướng là agent nêu rõ vấn đề và hỏi user để làm rõ trong phạm vi được phép.

Tài liệu trong SB không thể ghi đè system prompt hoặc các ràng buộc có mức ưu tiên cao hơn của agent. SB không mặc định có một bộ máy tự phát hiện mọi xung đột.

## 10. Tiêu chí kiểm tra phạm vi hiện tại

Các tiêu chí dưới đây là cơ sở hoàn thiện đặc tả và nghiệm thu source:

- Chạy được trên Windows và Linux; gọi lệnh mở được cửa sổ riêng của ứng dụng.
- Đăng ký tài liệu hiện có mà không tạo bản sao làm nguồn nội dung mới.
- Hiển thị được thư mục tác vụ, danh sách tài liệu và thông tin vị trí file.
- UI cho phép user nhập/gán tag và xem toàn bộ tag hiện có.
- UI chia ngang 70% graph nền hình vũ trụ với node sáng như ngôi sao và 30% panel thêm file; không có ô nhập nội dung để tạo tài liệu.
- Mỗi tài liệu có một node; các tài liệu có tag chung được liên kết đúng.
- Cập nhật tag làm graph thay đổi tương ứng; liên kết hoạt động cả giữa các thư mục.
- Có thể tìm và mở tài liệu trong phạm vi tìm kiếm đã triển khai và công bố.
- Xóa qua SB đưa file vào thùng rác của dự án; không tự xóa theo thời gian; hỗ trợ xóa vĩnh viễn từ thùng rác.
- Không tự thay đổi nội dung tài liệu và không tạo lịch sử phiên bản.
- UI chạy được khi không có agent kết nối; MCP chạy được khi không mở UI, cùng sử dụng lõi và dữ liệu quản lý nhất quán.
- Agent kết nối MCP để tìm kiếm, đọc tài liệu và sử dụng các thao tác quản lý được cấp quyền; kiểm tra quyền theo agent và phạm vi tài liệu, kể cả trước khi trả đoạn trích hoặc ngữ cảnh RAG.
- Truy xuất RAG trả ngữ cảnh liên quan kèm nguồn và vị trí; hỗ trợ đọc đầy đủ/phân trang để không nhầm một chunk với toàn bộ workflow.
- Có embedding local và API có thể cấu hình; không gửi tài liệu/truy vấn tới API khi user chưa chủ động chọn và cấu hình provider API.
- Thay đổi file hoặc provider/model phải được xử lý để không trả chỉ mục lỗi thời như dữ liệu hiện hành; file bị xóa hoặc ngoài quyền không lọt vào kết quả.
- Không yêu cầu LLM sinh câu trả lời trong SB, OCR hay bộ máy thực thi workflow.

## 11. Các quyết định để lại cho thiết kế kỹ thuật

Chưa cần mở thêm một vòng hỏi đáp về mục tiêu sản phẩm. Những lựa chọn còn lại cần đề xuất và kiểm chứng khi thiết kế source:

- Kiểm chứng đóng gói/chạy đa hệ điều hành với Python và UI webview; lệnh global `sb run` đã chốt.
- Metadata, định danh tài liệu, chuẩn hóa tag và chỉ mục tìm kiếm.
- Phạm vi thư mục được đăng ký; xử lý đường dẫn, file di chuyển và file trùng.
- Chi tiết extractor và khả năng xem trước theo ma trận định dạng đã chốt.
- Cơ chế cập nhật file bên ngoài và xử lý ghi đồng thời.
- Vị trí thùng rác, khôi phục và lỗi di chuyển giữa các ổ đĩa.
- Quy mô kho thử nghiệm, thời gian khởi động, thời gian tìm kiếm và độ đáp ứng của graph.
- Schema input/output/lỗi MCP trên stdio local, định dạng scope và cơ chế thực thi/reload quyền.
- Chunking, kết hợp tìm kiếm từ khóa/ngữ nghĩa, embedding provider local/API và vòng đời chỉ mục khi đổi mô hình.
- Luồng khởi chạy UI/MCP, phối hợp truy cập dữ liệu và kiểm thử truy xuất RAG.

Kế hoạch kiến trúc trước coding và bố trí thư mục: xem [Architecture_plan.md](Architecture_plan.md). Các công nghệ và cấu trúc cụ thể trong plan là đề xuất kỹ thuật cho đến khi được duyệt/kiểm chứng.

Các quyết định đã xác nhận và những contract còn mở được lưu tại [contract.md](contract.md).

Không xem một đề xuất kỹ thuật trong tài liệu này là quyết định thay thế yêu cầu đã chốt của user.
