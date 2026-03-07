<?php
$listing_id = $listing_id ?? get_the_ID();
$price = function_exists('get_field') ? get_field('kkl_price', $listing_id) : '';
$address = function_exists('get_field') ? get_field('kkl_address', $listing_id) : '';
$phone = function_exists('get_field') ? get_field('kkl_phone', $listing_id) : '';
$buy_link = function_exists('get_field') ? get_field('kkl_buy_link', $listing_id) : '';
$chat_link = function_exists('get_field') ? get_field('kkl_chat_link', $listing_id) : '';
$video = function_exists('get_field') ? get_field('kkl_video', $listing_id) : '';
$gallery = function_exists('get_field') ? get_field('kkl_gallery', $listing_id) : [];
$faq = function_exists('get_field') ? get_field('kkl_faq', $listing_id) : [];
$cats = get_the_terms($listing_id, 'listing_category');
$criteria = get_the_terms($listing_id, 'listing_criteria');
?>
<article class="kkl-single">
    <?php echo KKL_Plugin::breadcrumbs($listing_id); ?>
    <header class="kkl-single-header">
        <h1><?php echo esc_html(get_the_title($listing_id)); ?></h1>
        <div class="kkl-meta-grid">
            <span><strong>Danh mục:</strong> <?php echo esc_html($cats[0]->name ?? ''); ?></span>
            <span><strong>Giá:</strong> <?php echo esc_html($price); ?></span>
            <span><strong>Tiêu chí:</strong> <?php echo esc_html($criteria ? implode(', ', wp_list_pluck($criteria, 'name')) : ''); ?></span>
            <span><strong>Địa chỉ:</strong> <?php echo esc_html($address); ?></span>
        </div>
        <div class="kkl-action-row">
            <?php if ($phone) : ?><a href="tel:<?php echo esc_attr($phone); ?>" class="kkl-btn">Liên hệ</a><?php endif; ?>
            <?php if ($buy_link) : ?><a href="<?php echo esc_url($buy_link); ?>" class="kkl-btn kkl-btn-outline">Mua hàng</a><?php endif; ?>
            <?php if ($chat_link) : ?><a href="<?php echo esc_url($chat_link); ?>" class="kkl-btn kkl-btn-outline">Chat support</a><?php endif; ?>
        </div>
    </header>

    <section class="kkl-section"><h2>Mô tả</h2><?php echo wpautop(get_post_field('post_content', $listing_id)); ?></section>

    <?php if ($video) : ?>
        <section class="kkl-section"><h2>Video</h2><div class="kkl-video-wrap"><iframe src="<?php echo esc_url($video); ?>" loading="lazy" allowfullscreen></iframe></div></section>
    <?php endif; ?>

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
