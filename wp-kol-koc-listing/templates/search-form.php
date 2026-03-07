<form method="get" class="kkl-search-form">
    <input type="text" name="kkl_keyword" placeholder="Tìm theo tên..." value="<?php echo esc_attr($_GET['kkl_keyword'] ?? ''); ?>">
    <select name="listing_category">
        <option value="">Tất cả danh mục</option>
        <?php foreach (get_terms(['taxonomy' => 'listing_category', 'hide_empty' => false]) as $term) : ?>
            <option value="<?php echo esc_attr($term->slug); ?>" <?php selected($_GET['listing_category'] ?? '', $term->slug); ?>><?php echo esc_html($term->name); ?></option>
        <?php endforeach; ?>
    </select>
    <select name="listing_criteria">
        <option value="">Tất cả tiêu chí</option>
        <?php foreach (get_terms(['taxonomy' => 'listing_criteria', 'hide_empty' => false]) as $term) : ?>
            <option value="<?php echo esc_attr($term->slug); ?>" <?php selected($_GET['listing_criteria'] ?? '', $term->slug); ?>><?php echo esc_html($term->name); ?></option>
        <?php endforeach; ?>
    </select>
    <button type="submit">Tìm kiếm</button>
</form>
