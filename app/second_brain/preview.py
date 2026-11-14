"""Bounded, read-only previews of managed copies, never arbitrary source paths."""

from pathlib import Path
import base64
import mimetypes
from .storage import contained


def preview(catalog, identifier):
    with catalog.connect() as db:
        row = db.execute(
            "SELECT path,name FROM documents WHERE id=?", (identifier,)
        ).fetchone()
        if not row:
            raise ValueError("Không tìm thấy tài liệu")
        if db.execute(
            "SELECT 1 FROM file_operations WHERE document_id=?", (identifier,)
        ).fetchone():
            raise ValueError("Tài liệu có thao tác gián đoạn, chưa thể xem")
        trash = db.execute(
            "SELECT stored_path FROM trash_entries WHERE document_id=?", (identifier,)
        ).fetchone()
    path = contained(
        Path(trash["stored_path"] if trash else row["path"]),
        catalog.database.parent / ("trash" if trash else "storage"),
    )
    if path.stat().st_size > 20 * 1024 * 1024:
        raise ValueError(
            "Preview giới hạn 20 MB; hãy mở bản sao bằng ứng dụng mặc định"
        )
    extension = path.suffix.lower()
    result = {"name": row["name"], "kind": "text", "content": "", "limited": False}
    if extension in (".jpg", ".jpeg", ".png", ".gif", ".webp", ".bmp"):
        result.update(
            kind="image",
            content="data:"
            + (mimetypes.guess_type(path.name)[0] or "image/png")
            + ";base64,"
            + base64.b64encode(path.read_bytes()).decode(),
        )
        return result
    if extension in (".txt", ".md"):
        text = path.read_text(encoding="utf-8-sig", errors="replace")
    elif extension == ".docx":
        from docx import Document
        import zipfile

        with zipfile.ZipFile(path) as archive:
            if sum(item.file_size for item in archive.infolist()) > 50 * 1024 * 1024:
                raise ValueError("DOCX giải nén quá lớn để preview")
        doc = Document(path)
        text = "\n".join(p.text for p in doc.paragraphs)
        text += "\n" + "\n".join(
            " | ".join(c.text for c in row.cells)
            for table in doc.tables
            for row in table.rows
        )
        result["note"] = "Văn bản trích xuất; không giữ layout/ảnh của DOCX."
    elif extension == ".pdf":
        from pypdf import PdfReader

        pdf = PdfReader(path)
        if pdf.is_encrypted:
            raise ValueError("PDF có mật khẩu; mở bản sao bằng ứng dụng mặc định")
        parts = []
        for i, page in enumerate(pdf.pages):
            if i >= 50 or sum(map(len, parts)) > 200000:
                result["limited"] = True
                break
            parts.append(f"--- Trang {i+1} ---\n" + (page.extract_text() or ""))
        text = "\n".join(parts)
        result["note"] = (
            "Chỉ text PDF, không OCR; tối đa 50 trang. PDF scan có thể không có nội dung trích xuất."
        )
    else:
        raise ValueError(
            "Định dạng chưa hỗ trợ preview; mở bản sao bằng ứng dụng mặc định"
        )
    result["limited"] = result["limited"] or len(text) > 200000
    result["content"] = text[:200000]
    return result
