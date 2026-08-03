# Nguồn PDF đã ghi nhận (Lab 7 — K3 University Services)

Danh sách các tài liệu PDF tìm thấy trong quá trình khảo sát nguồn. Crawler mặc định
`scripts/fetch_public_pages.py` **không** xử lý PDF (chỉ nhận `text/html` / `text/plain`),
nên các nguồn này được đánh dấu để phát triển sau (scan/OCR nếu cần).

## PDF từ policy.vinuni.edu.vn

| Tài liệu | URL PDF | Phiên bản | Ghi chú |
|----------|---------|-----------|---------|
| Library Access & Services Policy | https://policy.vinuni.edu.vn/wp-content/uploads/2025/07/POL-LLR-001-V4.0_Library-Access-Services-Policy_9.7.2025_Clean.pdf | POL-LLR-001-V4.0 (Jul 09 2025) | Trang HTML có đủ text — không cần PDF |

> Trang policy tại `policy.vinuni.edu.vn/all-policies/...` đều có khối "PDF version" ở cuối
> (đường dẫn dạng `/wp-content/uploads/<năm>/<tháng>/..._Clean.pdf`). Nếu một policy chỉ có
> PDF mà thiếu text HTML, ta có thể dùng `marker-pdf` hoặc `pymupdf4llm` (mẹo trong exercises.md)
> để trích text/OCR thay vì copy tay.

## PDF từ registrar.vinuni.edu.vn (SharePoint)

| Tài liệu | URL PDF | Ghi chú |
|----------|---------|---------|
| SIS Registration Guide | https://vinuniversity-my.sharepoint.com/:b:/g/personal/registrar_vinuni_edu_vn/ERa3wXb4kBNPoRj7Xcnato4BRJ_GXxS1Oi-KUP0Pmw-uWg?e=gD3Xwv | Cần đăng nhập? Sharepoint nội bộ — kiểm tra quyền trước khi dùng |
| Registration Troubleshooting Guide | https://vinuniversity-my.sharepoint.com/:b:/g/personal/registrar_vinuni_edu_vn/EeCtOn-YTEdIiD1oxrDjDj4BJml0nAgEdPSvaDsV2EfYgQ?e=4k8YTh | Cần đăng nhập? Sharepoint nội bộ — kiểm tra quyền trước khi dùng |

> Hai file này trỏ vào SharePoint nội bộ (login). Theo `docs/DATA_COLLECTION.md`, nội dung sau
> đăng nhập không được dùng; chỉ dùng nếu URL công khai truy cập được.
