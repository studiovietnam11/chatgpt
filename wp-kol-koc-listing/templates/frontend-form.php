<?php if (!empty($_GET['kkl_submitted'])) : ?><p class="kkl-success">Đã gửi listing, chờ duyệt.</p><?php endif; ?>
<form method="post" class="kkl-frontend-form">
    <?php wp_nonce_field('kkl_submit_listing_action', 'kkl_submit_listing_nonce'); ?>
    <input type="hidden" name="kkl_submit_listing" value="1">
    <div class="kkl-form-grid">
        <input type="text" name="title" placeholder="Tên hồ sơ/listing" required>
        <input type="text" name="price" placeholder="Giá booking / giá dịch vụ">
        <input type="text" name="address" placeholder="Địa chỉ">
        <input type="text" name="phone" placeholder="Số điện thoại">
        <input type="number" name="followers_total" placeholder="Tổng followers">
        <input type="number" step="0.01" name="engagement_rate" placeholder="Engagement rate (%)">

        <select name="category" required>
            <option value="">Chọn danh mục</option>
            <?php foreach (get_terms(['taxonomy' => 'listing_category', 'hide_empty' => false]) as $term) : ?>
                <option value="<?php echo esc_attr($term->slug); ?>"><?php echo esc_html($term->name); ?></option>
            <?php endforeach; ?>
        </select>

        <input type="text" name="industry" placeholder="Ngành hàng phù hợp (cách nhau |)">
        <input type="text" name="platform" placeholder="Nền tảng social (cách nhau |)">
        <input type="text" name="criteria" placeholder="Tiêu chí (cách nhau |)">
    </div>
    <textarea name="product_fit" placeholder="Sản phẩm phù hợp để hợp tác" rows="3"></textarea>
    <textarea name="description" placeholder="Mô tả chi tiết hồ sơ" rows="5" required></textarea>
    <button type="submit">Gửi listing</button>
</form>
