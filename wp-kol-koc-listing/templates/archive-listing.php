<?php get_header(); ?>
<main class="kkl-container">
    <?php echo KKL_Plugin::breadcrumbs(); ?>
    <h1><?php echo is_tax() ? single_term_title('', false) : 'Danh sách Listing'; ?></h1>
    <?php echo do_shortcode('[kkl_archive]'); ?>
</main>
<?php get_footer(); ?>
