<?php
/**
 * Plugin Name: KOL KOC Listing Pro
 * Description: Plugin listing địa điểm và KOL/KOC với import CSV, ACF fields, shortcode, filter, Elementor widgets.
 * Version: 1.0.0
 * Author: Codex
 * Text Domain: kol-koc-listing
 */

if (!defined('ABSPATH')) {
    exit;
}

define('KKL_PLUGIN_FILE', __FILE__);
define('KKL_PLUGIN_PATH', plugin_dir_path(__FILE__));
define('KKL_PLUGIN_URL', plugin_dir_url(__FILE__));

require_once KKL_PLUGIN_PATH . 'includes/class-kkl-plugin.php';

KKL_Plugin::instance();
