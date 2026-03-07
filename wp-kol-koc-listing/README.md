# KOL KOC Listing Pro

Plugin WordPress cho listing **KOL/KOC + địa điểm** (nhà hàng, quán ăn, khách sạn, bệnh viện, trường học), tương thích ACF Premium/Pro.

## Điểm nâng cấp chính
- Hồ sơ KOL/KOC chi tiết: social metrics, audience, ngành hàng phù hợp, nền tảng social, lịch sử hợp tác/case study.
- Breadcrumbs hoạt động cho: archive listing, taxonomy, single listing.
- Tự tạo trang khi kích hoạt plugin:
  - `Trang chủ Listing` (`[kkl_home]`)
  - `Danh mục Listing` (`[kkl_archive]`)
  - `Đăng Listing` (`[kkl_submit_form]`)

## 1) Phân loại chuẩn nên dùng

### Danh mục (`listing_category`)
- KOL
- KOC
- Nhà hàng
- Quán ăn
- Khách sạn
- Bệnh viện
- Trường học

### Ngành hàng (`listing_industry`)
- Mỹ phẩm, Thời trang, Mẹ & Bé, Ẩm thực, Công nghệ, Du lịch, Giáo dục, Sức khỏe

### Nền tảng (`listing_platform`)
- TikTok, Facebook, Instagram, YouTube, Shopee Live, Threads

### Tiêu chí linh hoạt (`listing_criteria`)
- Khu vực, mức giá, phong cách content, dịch vụ, hình thức hợp tác...

## 2) Trường thông tin hồ sơ quan trọng
- Cơ bản: giá, địa chỉ, phone, email, link mua, link chat, video, gallery, mô tả profile
- Social: tổng followers, ER, avg views, avg reach
- Tệp người theo dõi: location, age, gender
- Fit: sản phẩm phù hợp, hình thức hợp tác, phong cách nội dung
- Kinh nghiệm: lịch sử hợp tác (brand/campaign/kết quả)
- Social account list: nền tảng + URL + followers từng kênh

## 3) Import Excel hàng loạt
1. Vào `Listings > Import CSV`.
2. Tải file mẫu: `sample-data/kkl-import-template.csv` (10 dòng).
3. Điền dữ liệu trong Excel và lưu dạng CSV UTF-8.
4. Upload file để import.

## 4) Avatar mặc định
Không có ảnh đại diện sẽ tự sinh avatar từ 2 ký tự đầu của tiêu đề.

## 5) Shortcodes
- `[kkl_home]` – landing listing
- `[kkl_archive]` – danh sách + lọc
- `[kkl_search]` – search/filter form
- `[kkl_submit_form]` – form đăng listing frontend
- `[kkl_single id="123"]` – hiển thị bài đơn

## 6) Elementor
Widget: **KKL Listing** (home/archive/search/form).

## 7) Responsive
- Mobile: 2 cột
- Tablet: 3 cột
- Desktop: 4 cột

## 8) Trang đơn
- Header thông tin chính + CTA (liên hệ/mua/chat/email)
- Section rõ ràng: mô tả, chỉ số social, sản phẩm phù hợp, kênh social, lịch sử hợp tác, video, gallery, FAQ
- Related listings: 12 bài cùng danh mục
- Form liên hệ cuối trang

## 9) Cài đặt nhanh
1. Copy thư mục `wp-kol-koc-listing` vào `wp-content/plugins/`.
2. Kích hoạt plugin.
3. Bật **ACF Pro/Premium**.
4. Dùng các trang tự tạo sẵn hoặc chèn shortcode / Elementor widget vào trang riêng.
