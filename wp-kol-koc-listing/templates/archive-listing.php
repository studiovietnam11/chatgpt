<?php get_header(); ?>
<main class="kkl-container">
    <h1><?php post_type_archive_title(); ?></h1>
    <?php echo do_shortcode('[kkl_archive]'); ?>
</main>
<?php get_footer(); ?>
