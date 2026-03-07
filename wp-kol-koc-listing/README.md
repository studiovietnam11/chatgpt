# KOL KOC Listing Pro

Plugin WordPress dành cho hệ thống listing KOL/KOC và địa điểm (nhà hàng, quán ăn, khách sạn, bệnh viện, trường học) tương thích ACF Premium.

## 1) Cấu trúc phân loại gợi ý chuẩn

### Danh mục chính (`listing_category`)
- KOL
- KOC
- Nhà hàng
- Quán ăn
- Khách sạn
- Bệnh viện
- Trường học

### Tiêu chí lọc (`listing_criteria`)
Ví dụ theo nhu cầu vận hành:
- Khu vực: miền bắc, miền trung, miền nam.
- Mức giá: bình dân, tầm trung, cao cấp.
- Hình thức nội dung: livestream, video ngắn, bài viết.
- Dịch vụ: đặt bàn, take-away, bảo hiểm, nội trú...

## 2) Trường thông tin quan trọng (ACF)
- Giá (`kkl_price`)
- Địa chỉ (`kkl_address`)
- Số điện thoại (`kkl_phone`)
- Link mua (`kkl_buy_link`)
- Link chat (`kkl_chat_link`)
- Video URL (`kkl_video`)
- Gallery (`kkl_gallery`)
- FAQ ngắn (`kkl_faq`)

## 3) Import Excel hàng loạt
1. Vào `Listings > Import CSV`.
2. Tải file mẫu: `sample-data/kkl-import-template.csv` (10 dòng dữ liệu).
3. Điền dữ liệu trong Excel và lưu lại định dạng CSV UTF-8.
4. Upload để import.

## 4) Avatar mặc định
Nếu listing không có ảnh đại diện, plugin tự tạo ảnh SVG từ 2 ký tự đầu của tiêu đề.

## 5) Shortcode
- Trang chủ listing: `[kkl_home]`
- Trang danh mục/listing: `[kkl_archive]`
- Form tìm kiếm/lọc: `[kkl_search]`
- Form đăng listing frontend: `[kkl_submit_form]`
- Hiển thị đơn theo ID: `[kkl_single id="123"]`

## 6) Elementor
Widget: **KKL Listing**
- Chế độ Trang chủ
- Chế độ Archive
- Chế độ Search form
- Chế độ Form đăng listing

## 7) Responsive
- Mobile: 2 cột.
- Tablet: 3 cột.
- Desktop: 4 cột.

## 8) Breadcrumbs
Plugin tạo breadcrumbs: `Trang chủ / Danh mục / Bài đơn` cho single listing.

## 9) Trang đơn
- Header thông tin chính + nút Liên hệ / Mua hàng / Chat support.
- Section rõ ràng: Mô tả, Video, Hình ảnh, FAQ ngắn.
- Related listings: 12 bài cùng danh mục.
- Form liên hệ ở cuối trang.

## 10) Cài đặt nhanh
1. Copy thư mục `wp-kol-koc-listing` vào `wp-content/plugins/`.
2. Kích hoạt plugin.
3. Đảm bảo đã bật **ACF Pro/Premium**.
4. Tạo trang và chèn shortcode hoặc dùng Elementor widget.
