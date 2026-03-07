<?php if (!empty($_GET['kkl_submitted'])) : ?><p class="kkl-success">Đã gửi listing, chờ duyệt.</p><?php endif; ?>
<form method="post" class="kkl-frontend-form">
    <?php wp_nonce_field('kkl_submit_listing_action', 'kkl_submit_listing_nonce'); ?>
    <input type="hidden" name="kkl_submit_listing" value="1">
    <div class="kkl-form-grid">
        <input type="text" name="title" placeholder="Tên listing" required>
        <input type="text" name="price" placeholder="Giá">
        <input type="text" name="address" placeholder="Địa chỉ">
        <input type="text" name="phone" placeholder="Số điện thoại">
        <select name="category" required>
            <option value="">Chọn danh mục</option>
            <?php foreach (get_terms(['taxonomy' => 'listing_category', 'hide_empty' => false]) as $term) : ?>
                <option value="<?php echo esc_attr($term->slug); ?>"><?php echo esc_html($term->name); ?></option>
            <?php endforeach; ?>
        </select>
        <input type="text" name="criteria" placeholder="Tiêu chí (cách nhau bằng dấu phẩy)">
    </div>
    <textarea name="description" placeholder="Mô tả chi tiết" rows="5" required></textarea>
    <button type="submit">Gửi listing</button>
</form>
