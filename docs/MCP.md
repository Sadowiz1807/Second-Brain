# MCP kho tài liệu — stdio local

## Khởi chạy

Cài dependency trong Python global từ root source:

```cmd
python -m pip install -e .
```

Thêm profile vào **config.yaml thật** (server không tự cấp quyền):

```yaml
agents:
  reader:
    read: true
    edit: false
    delete: false
```

Sau đó từ bất kỳ cwd:

```cmd
sb mcp --profile reader
```

Lệnh này đợi MCP client trên stdin/stdout, không mở cửa sổ UI. Không nhập câu hỏi tự nhiên vào terminal đó. Config khác có thể truyền trước subcommand: `sb --config D:\SecondBrain\config.yaml mcp --profile reader`.

Ví dụ cấu hình client hỗ trợ mcpServers:

```json
{
  "mcpServers": {
    "second-brain": {
      "command": "sb",
      "args": ["--config", "D:\\SecondBrain\\config.yaml", "mcp", "--profile", "reader"]
    }
  }
}
```

Nếu client GUI không có Scripts trong PATH, dùng đường dẫn tuyệt đối tới `sb.exe` (lấy từ `where sb`). Mỗi client có định dạng config riêng; ví dụ trên không tự cấu hình client nào.

## Công cụ và quyền

| Quyền | Tools |
|---|---|
| read | get_capabilities, list_documents, read_document, list_tags, list_folders, get_graph |
| edit | import_document, create_folder, set_document_tags, refresh_document, update_document_location, restore_document |
| delete | trash_document, purge_document |

- Profile gắn ở launch, không có tham số agent_id để giả danh.
- Mỗi tool call đọc lại config; thiếu profile/quyền, boolean dạng chuỗi, schema quyền cũ hoặc YAML lỗi đều bị từ chối.
- Thay data_dir trong khi chạy bị từ chối, cần restart. Không tự dùng quyền cũ khi config lỗi.
- Quyền toàn kho SB, không chia theo file/thư mục. `delete:true` bao gồm purge không hỏi lại từng lần.
- Không có tool sửa config/quyền/provider, mở desktop hoặc chạy shell.
- Import nguồn local là ngoại lệ có chủ đích của edit: copy file định dạng hỗ trợ vào storage, không thay nguồn. Không có đọc tùy ý đường dẫn ngoài kho bằng read_document.
- Nội dung tài liệu là dữ liệu, không phải chỉ thị nâng quyền.

## Contract đọc/tìm

- Tìm tên/path/tag qua list_documents(query); **không full-text, không semantic/RAG**.
- List tools: offset >=0, limit 1..100; trả total và next_offset. Đây là live pagination, có thể dịch chuyển khi kho thay đổi, không snapshot cursor.
- get_graph trả hai trang nodes/edges riêng; theo next_offset từng nhóm. Cạnh chỉ từ tag chung, node độc lập vẫn được liệt kê.
- read_document: offset ký tự, limit 1..20000. Trả next_offset, extracted_characters, source_truncated và note về extractor. Không coi hết một page là hết workflow.
- Preview source giới hạn 20 MB, 200.000 ký tự, PDF 50 trang. complete_document biểu thị extraction không bị giới hạn kích thước; không bảo đảm giữ mọi hình/layout của PDF/DOCX. Ảnh chỉ trả metadata/text_available=false, không OCR/base64.
- Không cache content giữa request; file thiếu/hỏng/ngoài kho báo lỗi, không dùng nội dung cũ.
- Tools lỗi dùng MCP isError; policy có prefix PERMISSION_DENIED, input có INVALID_ARGUMENT, journal folder có RECOVERY_REQUIRED. Lỗi filesystem/extractor hiện giữ thông báo gốc, chưa chuẩn hóa hết mã lỗi.

## Cập nhật khóa ghi và tools thư mục

- Khóa file `<data_dir>/.sb-operation.lock` dùng chung cho các mutation Catalog/Storage/Lifecycle/Folders, do đó UI và các MCP process cùng tuân thủ. Khóa reentrant cùng thread, chờ tối đa 10 giây; OS giải phóng khi process chết. Không xóa lock file thủ công trong khi SB chạy.
- MCP giữ khóa cho toàn tool call và kiểm tra lại quyền sau khi lấy khóa. UI mutations lấy cùng khóa ở service layer. File writer ngoài SB không bị khóa này kiểm soát.
- Có journal file hoặc folder pending thì mọi mutation bị chặn với RECOVERY_REQUIRED. Không tự xóa/copy đè để suy đoán phục hồi. `get_recovery_status` (read) vẫn đọc được journal khi tool bình thường bị chặn.
- Tools mới: `import_folder` (edit, giữ cây và báo file lỗi), `trash_folder` (delete), `list_trash_folders` (read), `restore_folder` (edit), `get_recovery_status` (read).
- Restore folder về vị trí cũ, từ chối khi đích tồn tại hoặc thiếu thư mục cha. Chưa có purge nguyên folder hoặc cơ chế tự động reconcile journal. Import batch hiện trả toàn bộ báo cáo, chưa phân trang theo job; dùng cây nhỏ/vừa.
- Kiểm thử bổ sung: lock giữa hai process và giải phóng, stdio import/trash/restore nguyên cây, bảo toàn nguồn. Tổng 21 tests pass, UI smoke Windows pass.

## Giới hạn và an toàn hiện tại (ghi nhận mốc trước, cập nhật trên được ưu tiên)

- Stdio server serialize các tool bằng lock trong cùng process. **Chưa có khóa filesystem liên tiến trình**: không chạy nhiều MCP/UI writer đồng thời trên cùng kho cho tới khi hardening hoàn tất.
- Journal pending của folder chặn server thao tác kho; file journal được lifecycle xử lý/từ chối theo ID. Chưa có tool tự phục hồi journal.
- Chưa expose xóa/khôi phục nguyên thư mục, recursive import hay purge folder qua MCP. Các thao tác đó cần hardening concurrency trước; get_capabilities công bố rõ.
- Import cùng tên báo lỗi, không tự ghi đè; retry write không có idempotency key. Client phải kiểm tra trạng thái trước retry khi mất kết nối.
- Không có RAG, embedding hoặc UI quản trị quyền trong lượt này.

## Bằng chứng

`tests/test_mcp_stdio.py` dùng SDK ClientSession nối tiến trình server stdio thật với config/kho tạm: initialize/discovery, import, tag/search, đọc phân trang, thu hồi quyền không restart, trash/restore/purge, bảo toàn nguồn, chặn traversal và config lỗi. Không dùng kho cá nhân, không tự cấp quyền trong config thật.
