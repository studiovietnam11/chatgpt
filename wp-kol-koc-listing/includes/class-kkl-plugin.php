<?php
if (!defined('ABSPATH')) {
    exit;
}

class KKL_Plugin
{
    private static $instance;

    public static function instance()
    {
        if (!self::$instance) {
            self::$instance = new self();
        }

        return self::$instance;
    }

    private function __construct()
    {
        add_action('init', [$this, 'register_post_type_and_taxonomies']);
        add_action('init', [$this, 'register_shortcodes']);
        add_action('wp_enqueue_scripts', [$this, 'enqueue_assets']);
        add_action('acf/init', [$this, 'register_acf_fields']);
        add_action('template_include', [$this, 'handle_template_include']);
        add_filter('manage_listing_posts_columns', [$this, 'admin_columns']);
        add_action('manage_listing_posts_custom_column', [$this, 'admin_column_values'], 10, 2);
        add_filter('post_type_link', [$this, 'listing_permalink'], 10, 2);
        add_action('admin_menu', [$this, 'register_import_page']);
        add_action('admin_post_kkl_import_csv', [$this, 'handle_import_csv']);
        add_action('admin_init', [$this, 'create_default_terms']);
        add_action('init', [$this, 'handle_frontend_submission']);
        add_action('elementor/widgets/register', [$this, 'register_elementor_widgets']);
        add_filter('the_content', [$this, 'append_contact_form_on_single']);

        register_activation_hook(KKL_PLUGIN_FILE, [$this, 'activate']);
    }

    public function activate()
    {
        $this->register_post_type_and_taxonomies();
        $this->create_default_terms();
        flush_rewrite_rules();
    }

    public function register_post_type_and_taxonomies()
    {
        register_post_type('listing', [
            'labels' => [
                'name' => __('Listings', 'kol-koc-listing'),
                'singular_name' => __('Listing', 'kol-koc-listing'),
                'add_new_item' => __('Add new listing', 'kol-koc-listing'),
            ],
            'public' => true,
            'has_archive' => 'danh-muc-listing',
            'rewrite' => ['slug' => '%listing_category%'],
            'supports' => ['title', 'editor', 'thumbnail', 'excerpt'],
            'show_in_rest' => true,
            'menu_icon' => 'dashicons-store',
        ]);

        register_taxonomy('listing_category', ['listing'], [
            'labels' => [
                'name' => __('Listing Categories', 'kol-koc-listing'),
                'singular_name' => __('Listing Category', 'kol-koc-listing'),
            ],
            'hierarchical' => true,
            'public' => true,
            'show_in_rest' => true,
            'rewrite' => ['slug' => 'danh-muc'],
        ]);

        register_taxonomy('listing_criteria', ['listing'], [
            'labels' => [
                'name' => __('Criteria', 'kol-koc-listing'),
                'singular_name' => __('Criterion', 'kol-koc-listing'),
            ],
            'hierarchical' => false,
            'public' => true,
            'show_in_rest' => true,
            'rewrite' => ['slug' => 'tieu-chi'],
        ]);
    }

    public function listing_permalink($post_link, $post)
    {
        if ('listing' !== $post->post_type) {
            return $post_link;
        }

        $terms = get_the_terms($post->ID, 'listing_category');
        if ($terms && !is_wp_error($terms)) {
            return str_replace('%listing_category%', $terms[0]->slug, $post_link);
        }

        return str_replace('%listing_category%', 'listing', $post_link);
    }

    public function create_default_terms()
    {
        $defaults = ['Nhà hàng', 'Quán ăn', 'Khách sạn', 'Bệnh viện', 'Trường học', 'KOL', 'KOC'];
        foreach ($defaults as $term) {
            if (!term_exists($term, 'listing_category')) {
                wp_insert_term($term, 'listing_category');
            }
        }
    }

    public function enqueue_assets()
    {
        wp_enqueue_style('kkl-style', KKL_PLUGIN_URL . 'assets/css/kkl-style.css', [], '1.0.0');
        wp_enqueue_script('kkl-script', KKL_PLUGIN_URL . 'assets/js/kkl-script.js', ['jquery'], '1.0.0', true);
    }

    public function register_acf_fields()
    {
        if (!function_exists('acf_add_local_field_group')) {
            return;
        }

        acf_add_local_field_group([
            'key' => 'group_kkl_listing',
            'title' => 'Thông tin Listing',
            'fields' => [
                ['key' => 'field_kkl_price', 'label' => 'Giá', 'name' => 'kkl_price', 'type' => 'text'],
                ['key' => 'field_kkl_address', 'label' => 'Địa chỉ', 'name' => 'kkl_address', 'type' => 'text'],
                ['key' => 'field_kkl_phone', 'label' => 'Số điện thoại', 'name' => 'kkl_phone', 'type' => 'text'],
                ['key' => 'field_kkl_buy_link', 'label' => 'Link mua hàng', 'name' => 'kkl_buy_link', 'type' => 'url'],
                ['key' => 'field_kkl_chat_link', 'label' => 'Link chat support', 'name' => 'kkl_chat_link', 'type' => 'url'],
                ['key' => 'field_kkl_video', 'label' => 'Video URL', 'name' => 'kkl_video', 'type' => 'url'],
                ['key' => 'field_kkl_gallery', 'label' => 'Gallery', 'name' => 'kkl_gallery', 'type' => 'gallery'],
                ['key' => 'field_kkl_faq', 'label' => 'FAQ ngắn', 'name' => 'kkl_faq', 'type' => 'repeater', 'sub_fields' => [
                    ['key' => 'field_kkl_q', 'label' => 'Câu hỏi', 'name' => 'question', 'type' => 'text'],
                    ['key' => 'field_kkl_a', 'label' => 'Trả lời', 'name' => 'answer', 'type' => 'textarea'],
                ]],
            ],
            'location' => [[['param' => 'post_type', 'operator' => '==', 'value' => 'listing']]],
        ]);
    }

    public function register_shortcodes()
    {
        add_shortcode('kkl_home', [$this, 'shortcode_home']);
        add_shortcode('kkl_archive', [$this, 'shortcode_archive']);
        add_shortcode('kkl_search', [$this, 'shortcode_search']);
        add_shortcode('kkl_submit_form', [$this, 'shortcode_submit_form']);
        add_shortcode('kkl_single', [$this, 'shortcode_single']);
    }

    public function shortcode_home($atts)
    {
        return $this->render_listing_grid(['posts_per_page' => 12, 'show_search' => true]);
    }

    public function shortcode_archive($atts)
    {
        $category = !empty($_GET['listing_category']) ? sanitize_text_field($_GET['listing_category']) : '';
        return $this->render_listing_grid(['posts_per_page' => 16, 'category' => $category]);
    }

    public function shortcode_search($atts)
    {
        ob_start();
        include KKL_PLUGIN_PATH . 'templates/search-form.php';
        return ob_get_clean();
    }

    public function shortcode_submit_form($atts)
    {
        ob_start();
        include KKL_PLUGIN_PATH . 'templates/frontend-form.php';
        return ob_get_clean();
    }

    public function shortcode_single($atts)
    {
        $atts = shortcode_atts(['id' => 0], $atts);
        $post = get_post((int) $atts['id']);
        if (!$post || 'listing' !== $post->post_type) {
            return '';
        }

        ob_start();
        $listing_id = $post->ID;
        include KKL_PLUGIN_PATH . 'templates/single-listing-content.php';
        return ob_get_clean();
    }

    private function render_listing_grid($args)
    {
        $query_args = [
            'post_type' => 'listing',
            'posts_per_page' => $args['posts_per_page'] ?? 12,
            's' => !empty($_GET['kkl_keyword']) ? sanitize_text_field($_GET['kkl_keyword']) : '',
        ];

        $tax_query = [];
        $category = $args['category'] ?? (!empty($_GET['listing_category']) ? sanitize_text_field($_GET['listing_category']) : '');
        if ($category) {
            $tax_query[] = ['taxonomy' => 'listing_category', 'field' => 'slug', 'terms' => $category];
        }

        if (!empty($_GET['listing_criteria'])) {
            $tax_query[] = ['taxonomy' => 'listing_criteria', 'field' => 'slug', 'terms' => sanitize_text_field($_GET['listing_criteria'])];
        }

        if ($tax_query) {
            $query_args['tax_query'] = $tax_query;
        }

        $query = new WP_Query($query_args);

        ob_start();
        if (!empty($args['show_search'])) {
            include KKL_PLUGIN_PATH . 'templates/search-form.php';
        }

        echo '<div class="kkl-grid">';
        while ($query->have_posts()) {
            $query->the_post();
            include KKL_PLUGIN_PATH . 'templates/card.php';
        }
        wp_reset_postdata();
        echo '</div>';

        return ob_get_clean();
    }

    public function handle_template_include($template)
    {
        if (is_singular('listing')) {
            return KKL_PLUGIN_PATH . 'templates/single-listing.php';
        }

        if (is_post_type_archive('listing') || is_tax('listing_category')) {
            return KKL_PLUGIN_PATH . 'templates/archive-listing.php';
        }

        return $template;
    }

    public function admin_columns($columns)
    {
        $columns['kkl_price'] = 'Giá';
        $columns['kkl_category'] = 'Danh mục';

        return $columns;
    }

    public function admin_column_values($column, $post_id)
    {
        if ('kkl_price' === $column) {
            echo esc_html(get_field('kkl_price', $post_id));
        }

        if ('kkl_category' === $column) {
            echo esc_html(wp_strip_all_tags(get_the_term_list($post_id, 'listing_category', '', ', ')));
        }
    }

    public function register_import_page()
    {
        add_submenu_page(
            'edit.php?post_type=listing',
            'Import CSV',
            'Import CSV',
            'manage_options',
            'kkl-import',
            [$this, 'render_import_page']
        );
    }

    public function render_import_page()
    {
        ?>
        <div class="wrap">
            <h1>Import Listing từ CSV (Excel)</h1>
            <p><a href="<?php echo esc_url(KKL_PLUGIN_URL . 'sample-data/kkl-import-template.csv'); ?>" class="button button-secondary">Tải file mẫu (10 dòng)</a></p>
            <form method="post" action="<?php echo esc_url(admin_url('admin-post.php')); ?>" enctype="multipart/form-data">
                <?php wp_nonce_field('kkl_import_nonce'); ?>
                <input type="hidden" name="action" value="kkl_import_csv" />
                <input type="file" name="csv_file" accept=".csv" required>
                <button type="submit" class="button button-primary">Import</button>
            </form>
        </div>
        <?php
    }

    public function handle_import_csv()
    {
        if (!current_user_can('manage_options') || !check_admin_referer('kkl_import_nonce')) {
            wp_die('Permission denied');
        }

        if (empty($_FILES['csv_file']['tmp_name'])) {
            wp_safe_redirect(admin_url('edit.php?post_type=listing&page=kkl-import'));
            exit;
        }

        $handle = fopen($_FILES['csv_file']['tmp_name'], 'r');
        $headers = fgetcsv($handle);
        while (($row = fgetcsv($handle)) !== false) {
            $data = array_combine($headers, $row);
            $post_id = wp_insert_post([
                'post_type' => 'listing',
                'post_title' => sanitize_text_field($data['title'] ?? ''),
                'post_content' => wp_kses_post($data['description'] ?? ''),
                'post_status' => 'publish',
            ]);
            if (is_wp_error($post_id) || !$post_id) {
                continue;
            }

            $category = sanitize_text_field($data['category'] ?? '');
            if ($category) {
                wp_set_object_terms($post_id, $category, 'listing_category', false);
            }

            $criteria_raw = !empty($data['criteria']) ? explode('|', $data['criteria']) : [];
            $criteria = array_map('sanitize_text_field', $criteria_raw);
            if ($criteria) {
                wp_set_object_terms($post_id, $criteria, 'listing_criteria', false);
            }

            if (function_exists('update_field')) {
                update_field('kkl_price', sanitize_text_field($data['price'] ?? ''), $post_id);
                update_field('kkl_address', sanitize_text_field($data['address'] ?? ''), $post_id);
                update_field('kkl_phone', sanitize_text_field($data['phone'] ?? ''), $post_id);
                update_field('kkl_buy_link', esc_url_raw($data['buy_link'] ?? ''), $post_id);
                update_field('kkl_chat_link', esc_url_raw($data['chat_link'] ?? ''), $post_id);
            }
        }
        fclose($handle);

        wp_safe_redirect(admin_url('edit.php?post_type=listing'));
        exit;
    }

    public function handle_frontend_submission()
    {
        if (empty($_POST['kkl_submit_listing']) || !wp_verify_nonce($_POST['kkl_submit_listing_nonce'] ?? '', 'kkl_submit_listing_action')) {
            return;
        }

        $post_id = wp_insert_post([
            'post_type' => 'listing',
            'post_title' => sanitize_text_field($_POST['title'] ?? ''),
            'post_content' => wp_kses_post($_POST['description'] ?? ''),
            'post_status' => 'pending',
        ]);

        if (!$post_id || is_wp_error($post_id)) {
            return;
        }

        $category = sanitize_text_field($_POST['category'] ?? '');
        if ($category) {
            wp_set_object_terms($post_id, $category, 'listing_category', false);
        }

        $criteria = !empty($_POST['criteria']) ? array_map('sanitize_text_field', explode(',', $_POST['criteria'])) : [];
        if ($criteria) {
            wp_set_object_terms($post_id, $criteria, 'listing_criteria', false);
        }

        if (function_exists('update_field')) {
            update_field('kkl_price', sanitize_text_field($_POST['price'] ?? ''), $post_id);
            update_field('kkl_address', sanitize_text_field($_POST['address'] ?? ''), $post_id);
            update_field('kkl_phone', sanitize_text_field($_POST['phone'] ?? ''), $post_id);
        }

        wp_safe_redirect(add_query_arg('kkl_submitted', '1', wp_get_referer()));
        exit;
    }

    public function append_contact_form_on_single($content)
    {
        if (!is_singular('listing') || !in_the_loop() || !is_main_query()) {
            return $content;
        }

        ob_start();
        include KKL_PLUGIN_PATH . 'templates/contact-form.php';
        return $content . ob_get_clean();
    }

    public static function default_avatar($title)
    {
        $letters = mb_substr(trim($title), 0, 2);
        $svg = sprintf('<svg xmlns="http://www.w3.org/2000/svg" width="300" height="300"><rect width="100%%" height="100%%" fill="#5b6cff"/><text x="50%%" y="54%%" dominant-baseline="middle" text-anchor="middle" fill="#fff" font-size="120" font-family="Arial">%s</text></svg>', esc_html(mb_strtoupper($letters)));

        return 'data:image/svg+xml;base64,' . base64_encode($svg);
    }

    public function register_elementor_widgets($widgets_manager)
    {
        if (!class_exists('Elementor\\Widget_Base')) {
            return;
        }
        require_once KKL_PLUGIN_PATH . 'templates/elementor/class-kkl-elementor-widget.php';
        $widgets_manager->register(new KKL_Elementor_Widget());
    }

    public static function breadcrumbs($post_id = 0)
    {
        if (!$post_id) {
            $post_id = get_the_ID();
        }

        $parts = ['<a href="' . esc_url(home_url('/')) . '">Trang chủ</a>'];
        $terms = get_the_terms($post_id, 'listing_category');
        if ($terms && !is_wp_error($terms)) {
            $parts[] = '<a href="' . esc_url(get_term_link($terms[0])) . '">' . esc_html($terms[0]->name) . '</a>';
        }
        $parts[] = esc_html(get_the_title($post_id));

        return '<nav class="kkl-breadcrumbs">' . implode(' <span>/</span> ', $parts) . '</nav>';
    }
}
