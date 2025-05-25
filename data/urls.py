# data/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('import_csv/', views.import_csv, name='import_csv'),
    path('sales-by-region/', views.sales_by_region, name='sales_by_region'),
    path('product-performance/', views.product_performance_data, name='product_performance'),
    path('category-sales-profit/', views.sales_and_profit_by_category, name='category-sales-profit'),
    path('sales-profit-by-category/', views.sales_profit_by_main_category, name='sales-profit-by-category'),
    path('profit-over-time/', views.profit_by_sub_category_over_time, name='profit-over-time'),
    path('yearly-sales-profit/', views.yearly_sales_profit),
    path('top3-highest-sales-regions/', views.top3_highest_sales_regions),
    path('top3-lowest-sales-regions/', views.top3_lowest_sales_regions),
    path('revenue-growth/', views.revenue_growth_top_vs_bottom),
    path('category-by-top-regions/', views.category_sales_by_top_regions),
    path('top10-profit-countries/', views.top10_profit_countries),
    path('bottom10-profit-countries/', views.bottom10_profit_countries),
    path('avg-discount-by-category/', views.avg_discount_by_category),
    path('profit-by-category/', views.profit_by_category),
    path('profit-by-segment/', views.profit_by_segment),
    path('overview-kpis/', views.overview_kpis),
    path('shipping-mode-distribution/', views.shipping_mode_distribution),
    path('order-distribution-by-country/', views.order_distribution_by_country),
    path('segment-trend-over-years/', views.segment_trend_over_years),
    path('shipping-mode-over-time/', views.shipping_mode_over_time, name='shipping-mode-over-time'),
    path('segment-revenue-distribution/', views.segment_revenue_distribution),
    path('segment-category-profit/', views.segment_category_profit),
]
