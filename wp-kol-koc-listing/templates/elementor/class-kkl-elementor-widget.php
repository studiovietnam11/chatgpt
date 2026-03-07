<?php
if (!defined('ABSPATH')) {
    exit;
}

class KKL_Elementor_Widget extends \Elementor\Widget_Base
{
    public function get_name()
    {
        return 'kkl_listing_widget';
    }

    public function get_title()
    {
        return 'KKL Listing';
    }

    public function get_icon()
    {
        return 'eicon-posts-grid';
    }

    public function get_categories()
    {
        return ['general'];
    }

    protected function register_controls()
    {
        $this->start_controls_section('content_section', ['label' => 'Cài đặt']);
        $this->add_control('mode', [
            'label' => 'Kiểu hiển thị',
            'type' => \Elementor\Controls_Manager::SELECT,
            'default' => 'home',
            'options' => [
                'home' => 'Trang chủ',
                'archive' => 'Archive',
                'search' => 'Search form',
                'form' => 'Form đăng listing',
            ],
        ]);
        $this->end_controls_section();
    }

    protected function render()
    {
        $settings = $this->get_settings_for_display();
        switch ($settings['mode']) {
            case 'archive':
                echo do_shortcode('[kkl_archive]');
                break;
            case 'search':
                echo do_shortcode('[kkl_search]');
                break;
            case 'form':
                echo do_shortcode('[kkl_submit_form]');
                break;
            default:
                echo do_shortcode('[kkl_home]');
        }
    }
}
