<form method="get" class="kkl-search-form" action="<?php echo esc_url(get_post_type_archive_link('listing') ?: ''); ?>">
    <input type="text" name="kkl_keyword" placeholder="Tìm theo tên, mô tả..." value="<?php echo esc_attr($_GET['kkl_keyword'] ?? ''); ?>">

    <select name="listing_category">
        <option value="">Danh mục</option>
        <?php foreach (get_terms(['taxonomy' => 'listing_category', 'hide_empty' => false]) as $term) : ?>
            <option value="<?php echo esc_attr($term->slug); ?>" <?php selected($_GET['listing_category'] ?? '', $term->slug); ?>><?php echo esc_html($term->name); ?></option>
        <?php endforeach; ?>
    </select>

    <select name="listing_industry">
        <option value="">Ngành hàng</option>
        <?php foreach (get_terms(['taxonomy' => 'listing_industry', 'hide_empty' => false]) as $term) : ?>
            <option value="<?php echo esc_attr($term->slug); ?>" <?php selected($_GET['listing_industry'] ?? '', $term->slug); ?>><?php echo esc_html($term->name); ?></option>
        <?php endforeach; ?>
    </select>

    <select name="listing_platform">
        <option value="">Nền tảng</option>
        <?php foreach (get_terms(['taxonomy' => 'listing_platform', 'hide_empty' => false]) as $term) : ?>
            <option value="<?php echo esc_attr($term->slug); ?>" <?php selected($_GET['listing_platform'] ?? '', $term->slug); ?>><?php echo esc_html($term->name); ?></option>
        <?php endforeach; ?>
    </select>

    <select name="listing_criteria">
        <option value="">Tiêu chí</option>
        <?php foreach (get_terms(['taxonomy' => 'listing_criteria', 'hide_empty' => false]) as $term) : ?>
            <option value="<?php echo esc_attr($term->slug); ?>" <?php selected($_GET['listing_criteria'] ?? '', $term->slug); ?>><?php echo esc_html($term->name); ?></option>
        <?php endforeach; ?>
    </select>

    <button type="submit">Tìm kiếm</button>
</form>
