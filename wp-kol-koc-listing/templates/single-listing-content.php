<?php
$listing_id = $listing_id ?? get_the_ID();
$price = function_exists('get_field') ? get_field('kkl_price', $listing_id) : '';
$address = function_exists('get_field') ? get_field('kkl_address', $listing_id) : '';
$phone = function_exists('get_field') ? get_field('kkl_phone', $listing_id) : '';
$email = function_exists('get_field') ? get_field('kkl_email', $listing_id) : '';
$buy_link = function_exists('get_field') ? get_field('kkl_buy_link', $listing_id) : '';
$chat_link = function_exists('get_field') ? get_field('kkl_chat_link', $listing_id) : '';
$video = function_exists('get_field') ? get_field('kkl_video', $listing_id) : '';
$gallery = function_exists('get_field') ? get_field('kkl_gallery', $listing_id) : [];
$faq = function_exists('get_field') ? get_field('kkl_faq', $listing_id) : [];
$bio = function_exists('get_field') ? get_field('kkl_bio', $listing_id) : '';
$followers = function_exists('get_field') ? get_field('kkl_followers_total', $listing_id) : '';
$er = function_exists('get_field') ? get_field('kkl_engagement_rate', $listing_id) : '';
$avg_views = function_exists('get_field') ? get_field('kkl_avg_views', $listing_id) : '';
$avg_reach = function_exists('get_field') ? get_field('kkl_avg_reach', $listing_id) : '';
$product_fit = function_exists('get_field') ? get_field('kkl_product_fit', $listing_id) : '';
$case_studies = function_exists('get_field') ? get_field('kkl_case_studies', $listing_id) : [];
$social_accounts = function_exists('get_field') ? get_field('kkl_social_accounts', $listing_id) : [];
$audience_location = function_exists('get_field') ? get_field('kkl_audience_location', $listing_id) : '';
$audience_age = function_exists('get_field') ? get_field('kkl_audience_age', $listing_id) : '';
$audience_gender = function_exists('get_field') ? get_field('kkl_audience_gender', $listing_id) : '';
$cats = get_the_terms($listing_id, 'listing_category');
$criteria = get_the_terms($listing_id, 'listing_criteria');
$industries = get_the_terms($listing_id, 'listing_industry');
$platforms = get_the_terms($listing_id, 'listing_platform');
?>
<article class="kkl-single">
    <?php echo KKL_Plugin::breadcrumbs($listing_id); ?>
    <header class="kkl-single-header kkl-section">
        <h1><?php echo esc_html(get_the_title($listing_id)); ?></h1>
        <?php if ($bio) : ?><p><?php echo esc_html($bio); ?></p><?php endif; ?>
        <div class="kkl-meta-grid">
            <span><strong>Danh mục:</strong> <?php echo esc_html($cats[0]->name ?? ''); ?></span>
            <span><strong>Giá:</strong> <?php echo esc_html($price); ?></span>
            <span><strong>Nền tảng:</strong> <?php echo esc_html($platforms ? implode(', ', wp_list_pluck($platforms, 'name')) : ''); ?></span>
            <span><strong>Ngành hàng:</strong> <?php echo esc_html($industries ? implode(', ', wp_list_pluck($industries, 'name')) : ''); ?></span>
            <span><strong>Tiêu chí:</strong> <?php echo esc_html($criteria ? implode(', ', wp_list_pluck($criteria, 'name')) : ''); ?></span>
            <span><strong>Địa chỉ:</strong> <?php echo esc_html($address); ?></span>
        </div>
        <div class="kkl-action-row">
            <?php if ($phone) : ?><a href="tel:<?php echo esc_attr($phone); ?>" class="kkl-btn">Liên hệ</a><?php endif; ?>
            <?php if ($email) : ?><a href="mailto:<?php echo esc_attr($email); ?>" class="kkl-btn kkl-btn-outline">Email</a><?php endif; ?>
            <?php if ($buy_link) : ?><a href="<?php echo esc_url($buy_link); ?>" class="kkl-btn kkl-btn-outline">Mua hàng</a><?php endif; ?>
            <?php if ($chat_link) : ?><a href="<?php echo esc_url($chat_link); ?>" class="kkl-btn kkl-btn-outline">Chat support</a><?php endif; ?>
        </div>
    </header>

    <section class="kkl-section"><h2>Mô tả chi tiết</h2><?php echo wpautop(get_post_field('post_content', $listing_id)); ?></section>

    <section class="kkl-section"><h2>Chỉ số Social</h2>
        <div class="kkl-meta-grid">
            <span><strong>Followers:</strong> <?php echo esc_html($followers ? number_format_i18n((int) $followers) : ''); ?></span>
            <span><strong>ER:</strong> <?php echo esc_html($er !== '' ? $er . '%' : ''); ?></span>
            <span><strong>Avg Views:</strong> <?php echo esc_html($avg_views ? number_format_i18n((int) $avg_views) : ''); ?></span>
            <span><strong>Avg Reach:</strong> <?php echo esc_html($avg_reach ? number_format_i18n((int) $avg_reach) : ''); ?></span>
            <span><strong>Audience location:</strong> <?php echo esc_html($audience_location); ?></span>
            <span><strong>Age/Gender:</strong> <?php echo esc_html(trim($audience_age . ' | ' . $audience_gender, ' |')); ?></span>
        </div>
    </section>

    <?php if ($product_fit) : ?><section class="kkl-section"><h2>Sản phẩm phù hợp</h2><p><?php echo esc_html($product_fit); ?></p></section><?php endif; ?>

    <?php if ($social_accounts) : ?>
        <section class="kkl-section"><h2>Kênh social</h2>
            <ul>
                <?php foreach ($social_accounts as $item) : ?>
                    <li><strong><?php echo esc_html($item['platform'] ?? ''); ?>:</strong> <a href="<?php echo esc_url($item['url'] ?? '#'); ?>" target="_blank" rel="noopener">Link</a> - <?php echo esc_html(!empty($item['followers']) ? number_format_i18n((int) $item['followers']) . ' followers' : ''); ?></li>
                <?php endforeach; ?>
            </ul>
        </section>
    <?php endif; ?>

    <?php if ($case_studies) : ?>
        <section class="kkl-section"><h2>Lịch sử hợp tác</h2>
            <?php foreach ($case_studies as $item) : ?>
                <div class="kkl-case-item"><strong><?php echo esc_html($item['brand'] ?? ''); ?></strong> — <?php echo esc_html($item['campaign'] ?? ''); ?><br><small>Kết quả: <?php echo esc_html($item['result'] ?? ''); ?></small></div>
            <?php endforeach; ?>
        </section>
    <?php endif; ?>

    <?php if ($video) : ?><section class="kkl-section"><h2>Video</h2><div class="kkl-video-wrap"><iframe src="<?php echo esc_url($video); ?>" loading="lazy" allowfullscreen></iframe></div></section><?php endif; ?>

    <?php if ($gallery) : ?>
        <section class="kkl-section"><h2>Hình ảnh</h2><div class="kkl-gallery">
            <?php foreach ($gallery as $image) : ?><img src="<?php echo esc_url($image['sizes']['medium'] ?? $image['url']); ?>" alt="<?php echo esc_attr($image['alt'] ?? ''); ?>"><?php endforeach; ?>
        </div></section>
    <?php endif; ?>

    <?php if ($faq) : ?>
        <section class="kkl-section"><h2>Câu hỏi nhanh</h2>
            <?php foreach ($faq as $item) : ?>
                <details><summary><?php echo esc_html($item['question'] ?? ''); ?></summary><p><?php echo esc_html($item['answer'] ?? ''); ?></p></details>
            <?php endforeach; ?>
        </section>
    <?php endif; ?>

    <section class="kkl-section"><h2>Related listings</h2>
        <div class="kkl-grid">
            <?php
            $related = new WP_Query([
                'post_type' => 'listing',
                'posts_per_page' => 12,
                'post__not_in' => [$listing_id],
                'tax_query' => !empty($cats[0]->term_id) ? [[
                    'taxonomy' => 'listing_category',
                    'field' => 'term_id',
                    'terms' => [$cats[0]->term_id],
                ]] : [],
            ]);
            while ($related->have_posts()) :
                $related->the_post();
                include KKL_PLUGIN_PATH . 'templates/card.php';
            endwhile;
            wp_reset_postdata();
            ?>
        </div>
    </section>
</article>
