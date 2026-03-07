<?php
$image = get_the_post_thumbnail_url(get_the_ID(), 'medium');
if (!$image) {
    $image = KKL_Plugin::default_avatar(get_the_title());
}
$price = function_exists('get_field') ? get_field('kkl_price') : '';
$followers = function_exists('get_field') ? get_field('kkl_followers_total') : '';
$terms = get_the_terms(get_the_ID(), 'listing_category');
$criteria = get_the_terms(get_the_ID(), 'listing_criteria');
$industries = get_the_terms(get_the_ID(), 'listing_industry');
$platforms = get_the_terms(get_the_ID(), 'listing_platform');
?>
<article class="kkl-card">
    <a href="<?php the_permalink(); ?>" class="kkl-thumb-wrap"><img src="<?php echo esc_url($image); ?>" alt="<?php the_title_attribute(); ?>"></a>
    <div class="kkl-card-body">
        <div class="kkl-meta-row">
            <span class="kkl-chip"><?php echo esc_html($terms[0]->name ?? 'Chưa phân loại'); ?></span>
            <?php if ($price) : ?><span class="kkl-price"><?php echo esc_html($price); ?></span><?php endif; ?>
        </div>
        <h3><?php the_title(); ?></h3>
        <?php if ($followers) : ?><p><strong>Followers:</strong> <?php echo esc_html(number_format_i18n((int) $followers)); ?></p><?php endif; ?>
        <p class="kkl-criteria"><strong>Nền tảng:</strong> <?php echo esc_html($platforms ? implode(', ', wp_list_pluck($platforms, 'name')) : ''); ?></p>
        <p class="kkl-criteria"><strong>Ngành hàng:</strong> <?php echo esc_html($industries ? implode(', ', wp_list_pluck($industries, 'name')) : ''); ?></p>
        <p class="kkl-criteria"><strong>Tiêu chí:</strong> <?php echo esc_html($criteria ? implode(', ', wp_list_pluck($criteria, 'name')) : ''); ?></p>
        <a class="kkl-btn" href="<?php the_permalink(); ?>">Xem chi tiết</a>
    </div>
</article>
