# data/views.py
# data/views.py
from django.shortcuts import render

def home(request):
    return render(request, 'home.html')  # Render template home.html


import csv
from django.http import HttpResponse
from .models import SalesData
import os
from datetime import datetime

def import_csv(request):
    file_path = os.path.join('D:/University/Data Visualization/final/SuperStoreOrders_no_missing.csv')

    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                # Tạo datetime object từ chuỗi ngày
                order_date = datetime.strptime(row['order_date'], '%Y-%m-%d')

                SalesData.objects.create(
                    order_id=row['order_id'],
                    order_date=order_date,
                    ship_date=row['ship_date'],
                    ship_mode=row['ship_mode'],
                    customer_name=row['customer_name'],
                    segment=row['segment'],
                    state=row['state'],
                    country=row['country'],
                    market=row['market'],
                    region=row['region'],
                    product_id=row['product_id'],
                    category=row['category'],
                    sub_category=row['sub_category'],
                    product_name=row['product_name'],
                    sales=row['sales'],
                    quantity=row['quantity'],
                    discount=row['discount'],
                    profit=row['profit'],
                    shipping_cost=row['shipping_cost'],
                    order_priority=row['order_priority'],
                    year=row['year'],
                    month=order_date.month  # ✅ dùng order_date đã được tạo ở trên
                )

        return HttpResponse('CSV file imported successfully!')
    except FileNotFoundError:
        return HttpResponse('File not found!', status=404)



from django.db.models import Sum
from django.http import JsonResponse
from .models import SalesData

def sales_by_region(request):
    data = SalesData.objects.values('region').annotate(total_sales=Sum('sales')).order_by('-total_sales')
    return JsonResponse({
        'regions': [d['region'] for d in data],
        'sales': [d['total_sales'] for d in data]
    })


from django.db.models import Sum, Avg, FloatField, ExpressionWrapper
from django.http import JsonResponse

def product_performance_data(request):
    data = SalesData.objects.values('sub_category').annotate(
        sum_sales=Sum('sales'),
        avg_discount=Avg('discount'),
        sum_profit=Sum('profit'),
        profit_margin=ExpressionWrapper(Sum('profit') / Sum('sales') * 100, output_field=FloatField())
    ).order_by('-sum_sales')

    return JsonResponse({
        'sub_categories': [d['sub_category'] for d in data],
        'sales': [d['sum_sales'] for d in data],
        'discounts': [d['avg_discount'] for d in data],
        'margins': [d['profit_margin'] for d in data]
    })

def sales_and_profit_by_category(request):
    data = SalesData.objects.values('sub_category').annotate(
        sum_sales=Sum('sales'),
        sum_profit=Sum('profit')
    ).order_by('-sum_sales')[:10]  # Top 10 sub_category

    return JsonResponse({
        'sub_categories': [d['sub_category'] for d in data],
        'sales': [d['sum_sales'] for d in data],
        'profits': [d['sum_profit'] for d in data]
    })

def sales_profit_by_main_category(request):
    data = SalesData.objects.values('category').annotate(
        sum_sales=Sum('sales'),
        sum_profit=Sum('profit')
    ).order_by('-sum_sales')

    return JsonResponse({
        'categories': [d['category'] for d in data],
        'sales': [d['sum_sales'] for d in data],
        'profits': [d['sum_profit'] for d in data]
    })

from collections import defaultdict

def profit_by_sub_category_over_time(request):
    # Lấy dữ liệu lợi nhuận theo sub_category và năm
    data = SalesData.objects.values('sub_category', 'year').annotate(
        total_profit=Sum('profit')
    ).order_by('year')

    # Gom theo sub_category
    chart_data = defaultdict(lambda: [0, 0, 0, 0])  # năm 2011 -> 2014

    year_index = {2011: 0, 2012: 1, 2013: 2, 2014: 3}

    for d in data:
        idx = year_index.get(int(d['year']))
        if idx is not None:
            chart_data[d['sub_category']][idx] = d['total_profit']

    return JsonResponse({
        'labels': ['2011', '2012', '2013', '2014'],
        'datasets': [
            {
                'label': sub,
                'data': profits
            } for sub, profits in chart_data.items()
        ]
    })

def yearly_sales_profit(request):
    raw_data = (SalesData.objects
                .values('year')
                .annotate(
                    total_sales=Sum('sales'),
                    total_profit=Sum('profit')
                )
                .order_by('year'))

    return JsonResponse({
        'labels': [d['year'] for d in raw_data],
        'sales': [d['total_sales'] for d in raw_data],
        'profits': [d['total_profit'] for d in raw_data]
    })

from django.db.models import Sum

def top3_highest_sales_regions(request):
    years = SalesData.objects.values_list('year', flat=True).distinct().order_by('year')
    regions = (SalesData.objects.values('region')
               .annotate(total_sales=Sum('sales'))
               .order_by('-total_sales')[:3])
    region_names = [r['region'] for r in regions]

    data = {}
    for region in region_names:
        region_data = SalesData.objects.filter(region=region).values('year').annotate(sales=Sum('sales'))
        sales_by_year = {str(d['year']): d['sales'] for d in region_data}
        data[region] = [sales_by_year.get(str(y), 0) for y in years]

    return JsonResponse({
        'years': list(years),
        'datasets': [
            {'label': region, 'data': data[region]} for region in region_names
        ]
    })


def top3_lowest_sales_regions(request):
    years = SalesData.objects.values_list('year', flat=True).distinct().order_by('year')
    regions = (SalesData.objects.values('region')
               .annotate(total_sales=Sum('sales'))
               .order_by('total_sales')[:3])
    region_names = [r['region'] for r in regions]

    data = {}
    for region in region_names:
        region_data = SalesData.objects.filter(region=region).values('year').annotate(sales=Sum('sales'))
        sales_by_year = {str(d['year']): d['sales'] for d in region_data}
        data[region] = [sales_by_year.get(str(y), 0) for y in years]

    return JsonResponse({
        'years': list(years),
        'datasets': [
            {'label': region, 'data': data[region]} for region in region_names
        ]
    })

def revenue_growth_top_vs_bottom(request):
    years = SalesData.objects.values_list('year', flat=True).distinct().order_by('year')

    top_regions = (SalesData.objects.values('region')
                   .annotate(total_sales=Sum('sales'))
                   .order_by('-total_sales')[:3])
    bottom_regions = (SalesData.objects.values('region')
                      .annotate(total_sales=Sum('sales'))
                      .order_by('total_sales')[:3])

    top_names = [r['region'] for r in top_regions]
    bottom_names = [r['region'] for r in bottom_regions]

    def get_sales(regions):
        data = SalesData.objects.filter(region__in=regions).values('year').annotate(sales=Sum('sales'))
        lookup = {str(d['year']): d['sales'] for d in data}
        return [lookup.get(str(y), 0) for y in years]

    return JsonResponse({
        'years': list(years),
        'top': get_sales(top_names),
        'bottom': get_sales(bottom_names),
    })

from django.db.models import Sum
def category_sales_by_top_regions(request):
    # Lấy 3 khu vực có tổng doanh thu cao nhất
    top_regions = (SalesData.objects.values('region')
                   .annotate(total_sales=Sum('sales'))
                   .order_by('-total_sales')[:3])
    top_region_names = [r['region'] for r in top_regions]

    # Lấy doanh thu theo ngành hàng và khu vực (chỉ lọc top 3 vùng)
    raw_data = (SalesData.objects
                .filter(region__in=top_region_names)
                .values('sub_category', 'region')
                .annotate(sales=Sum('sales')))

    # Gom nhóm ngành hàng và tổng doanh thu
    subcat_totals = {}
    region_data = {region: {} for region in top_region_names}

    for row in raw_data:
        cat = row['sub_category']
        region = row['region']
        sales = row['sales']

        subcat_totals[cat] = subcat_totals.get(cat, 0) + sales
        region_data[region][cat] = sales

    # Sắp xếp ngành hàng theo tổng doanh thu giảm dần
    sorted_subcats = sorted(subcat_totals.keys(), key=lambda x: subcat_totals[x], reverse=True)

    # Chuẩn hóa dữ liệu cho Chart.js
    datasets = []
    for region in top_region_names:
        datasets.append({
            'label': region,
            'data': [region_data[region].get(cat, 0) for cat in sorted_subcats]
        })

    return JsonResponse({
        'labels': sorted_subcats,
        'datasets': datasets
    })


def top10_profit_countries(request):
    data = (SalesData.objects.values('country')
            .annotate(total_profit=Sum('profit'))
            .order_by('-total_profit')[:10])

    return JsonResponse({
        'labels': [d['country'] for d in data],
        'profits': [d['total_profit'] for d in data]
    })


def bottom10_profit_countries(request):
    data = (SalesData.objects.values('country')
            .annotate(total_profit=Sum('profit'))
            .order_by('total_profit')[:10])

    return JsonResponse({
        'labels': [d['country'] for d in data],
        'profits': [d['total_profit'] for d in data]
    })

def avg_discount_by_category(request):
    data = (SalesData.objects
            .values('category')
            .annotate(avg_discount=Avg('discount'))
            .order_by('category'))

    return JsonResponse({
        'categories': [d['category'] for d in data],
        'avg_discounts': [round(d['avg_discount'] * 100, 2) for d in data]  # chuyển % và làm tròn
    })


def profit_by_category(request):
    data = (SalesData.objects
            .values('category')
            .annotate(total_profit=Sum('profit'))
            .order_by('category'))

    return JsonResponse({
        'categories': [d['category'] for d in data],
        'profits': [d['total_profit'] for d in data]
    })

def profit_by_segment(request):
    data = (SalesData.objects
            .values('segment')
            .annotate(
                total_profit=Sum('profit'),
                total_sales=Sum('sales')
            )
            .order_by('-total_sales'))

    return JsonResponse({
        'segments': [d['segment'] for d in data],
        'sales': [d['total_sales'] for d in data],
        'profits': [d['total_profit'] for d in data]
    })

def sales_by_region(request):
    data = SalesData.objects.values('region').annotate(total_sales=Sum('sales')).order_by('-total_sales')
    return JsonResponse({
        'regions': [d['region'] for d in data],
        'sales': [d['total_sales'] for d in data]
    })

def overview_kpis(request):
    from django.db.models import Avg, Sum, FloatField, ExpressionWrapper

    total = SalesData.objects.aggregate(
        sum_sales=Sum('sales'),
        sum_profit=Sum('profit'),
        sum_qty=Sum('quantity'),
        avg_discount=Avg('discount'),
        avg_sales=Avg('sales'),
        avg_profit=Avg('profit'),
        profit_margin=ExpressionWrapper(Sum('profit') / Sum('sales') * 100, output_field=FloatField())
    )

    return JsonResponse({
        'sum_sales': round(total['sum_sales'], 0),
        'sum_profit': round(total['sum_profit'], 0),
        'sum_qty': total['sum_qty'],
        'avg_discount': round(total['avg_discount'] * 100, 2),
        'avg_sales': round(total['avg_sales'], 0),
        'avg_profit': round(total['avg_profit'], 0),
        'profit_margin': round(total['profit_margin'], 2),
    })

from django.db.models import Count
def shipping_mode_distribution(request):
    data = (SalesData.objects
            .values('ship_mode')
            .annotate(count=Count('id'))
            .order_by('-count'))

    return JsonResponse({
        'ship_modes': [d['ship_mode'] for d in data],
        'counts': [d['count'] for d in data]
    })
    
from geopy.geocoders import Nominatim
from django.db.models import Count
from django.http import JsonResponse
import time

geolocator = Nominatim(user_agent="geoapi")

def order_distribution_by_country(request):
    raw = (SalesData.objects
           .values('country')
           .annotate(count=Count('id'))
           .order_by('-count'))

    countries, counts, lats, lons = [], [], [], []

    for row in raw:
        country = row['country']
        try:
            location = geolocator.geocode(country)
            if location:
                countries.append(country)
                counts.append(row['count'])
                lats.append(location.latitude)
                lons.append(location.longitude)
                time.sleep(1)  # tránh bị chặn do gửi quá nhanh
        except Exception as e:
            print(f"Lỗi tra toạ độ {country}: {e}")

    return JsonResponse({
        'countries': countries,
        'counts': counts,
        'lats': lats,
        'lons': lons
    })


def segment_trend_over_years(request):
    segments = SalesData.objects.values_list('segment', flat=True).distinct()
    years = SalesData.objects.values_list('year', flat=True).distinct().order_by('year')
    years = list(years)

    data = {}
    for segment in segments:
        sales_by_year = (
            SalesData.objects.filter(segment=segment)
            .values('year')
            .annotate(total_sales=Sum('sales'), total_profit=Sum('profit'))
            .order_by('year')
        )
        sales = {entry['year']: entry['total_sales'] for entry in sales_by_year}
        profits = {entry['year']: entry['total_profit'] for entry in sales_by_year}

        data[segment] = {
            'sales': [sales.get(y, 0) for y in years],
            'profit': [profits.get(y, 0) for y in years]
        }

    return JsonResponse({
        'years': years,
        'data': data
    })

def shipping_mode_over_time(request):
    years = SalesData.objects.values_list('year', flat=True).distinct().order_by('year')
    ship_modes = SalesData.objects.values_list('ship_mode', flat=True).distinct()

    data = {}

    for mode in ship_modes:
        sales_by_year = (
            SalesData.objects.filter(ship_mode=mode)
            .values('year')
            .annotate(sales=Sum('sales'), profit=Sum('profit'))
        )
        sales_dict = {entry['year']: entry['sales'] for entry in sales_by_year}
        profit_dict = {entry['year']: entry['profit'] for entry in sales_by_year}

        data[mode] = {
            'sales': [sales_dict.get(year, 0) for year in years],
            'profit': [profit_dict.get(year, 0) for year in years]
        }

    return JsonResponse({
        'years': list(years),
        'data': data
    })

def segment_revenue_distribution(request):
    data = (
        SalesData.objects.values('segment')
        .annotate(total_sales=Sum('sales'))
        .order_by('-total_sales')
    )
    return JsonResponse({
        'labels': [d['segment'] for d in data],
        'values': [d['total_sales'] for d in data]
    })

def segment_category_profit(request):
    categories = ['Furniture', 'Office Supplies', 'Technology']
    segments = SalesData.objects.values_list('segment', flat=True).distinct()

    datasets = []
    for category in categories:
        profits = []
        for segment in segments:
            total = SalesData.objects.filter(segment=segment, category=category).aggregate(Sum('profit'))['profit__sum'] or 0
            profits.append(total)

        datasets.append({
            'label': category,
            'data': profits
        })

    return JsonResponse({
        'segments': list(segments),
        'datasets': datasets
    })