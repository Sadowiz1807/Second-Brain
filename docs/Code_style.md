# Quy ước code dễ đọc

Áp dụng `.agent/rule_coding.md` cho toàn bộ Python backend, JavaScript, HTML, CSS và tests. Đây là refactor cách trình bày và tách logic, không thay đổi contract sản phẩm.

## Quy tắc

- Mỗi câu lệnh một dòng; không gộp nhánh điều kiện hoặc thao tác bằng dấu chấm phẩy.
- JavaScript dùng block `{}` cho if/else/loop; khai báo từng biến riêng.
- Dùng tên mô tả và biến trung gian cho kết quả API, điều kiện lọc, checksum, đường dẫn đích và thông báo xác nhận.
- Tách callback lồng sâu thành hàm có tên khi hợp lý; không ép mọi biểu thức ngắn thành nhiều dòng.
- HTML/CSS có thụt dòng, mỗi thuộc tính CSS một dòng; không minify source.
- Tests nằm trong `tests/`.

## Công cụ

Python dùng Black 26.10.1, cấu hình trong `pyproject.toml`, độ dài dòng 88. Frontend dùng Prettier 3.10.1, cấu hình `.prettierrc.json`. ESLint 9 có quy tắc cấu trúc tại `eslint.config.mjs` (không phải kiểm chứng đầy đủ ngữ nghĩa JavaScript).

```sh
python -m black app tests
npx --yes eslint@9 --fix "app/second_brain/desktop/*.js"
npx --yes prettier@3.10.1 --write "app/second_brain/desktop/*.{js,css,html}"
npx --yes prettier@3.10.1 --parser html --write app/second_brain/desktop/universe.svg
```

Chạy ESLint sửa block trước Prettier để định dạng lại block vừa thêm. SVG dùng parser HTML riêng. Các lệnh npx có thể tải công cụ từ npm khi chưa có cache; không thêm dependency runtime vào UI.

## Kiểm tra

```sh
python -m black --check app tests
npx --yes eslint@9 "app/second_brain/desktop/*.js"
npx --yes prettier@3.10.1 --check "app/second_brain/desktop/*.{js,css,html}"
python -m pytest -q
node --check app/second_brain/desktop/app.js
node --check app/second_brain/desktop/import-ui.js
python tests/ui_smoke.py
```

Smoke mở cửa sổ thật. Formatter/lint pass không thay thế kiểm thử chức năng hoặc review bảo mật.
