<?php get_header(); ?>
<main class="kkl-container kkl-single-page">
    <?php while (have_posts()) : the_post(); ?>
        <?php include KKL_PLUGIN_PATH . 'templates/single-listing-content.php'; ?>
    <?php endwhile; ?>
</main>
<?php get_footer(); ?>
