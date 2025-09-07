from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta, datetime
import json
from olxscraper.searches.models import Item, Category, Search, SearchResult


def get_dashboard_stats(today, week_ago):
    recent_items_week = Item.objects.filter(created__gte=week_ago).count()
    recent_items_today = Item.objects.filter(created__date=today).count()
    active_categories = Category.objects.filter(
        address__search__searchresult__item__created__gte=week_ago,
        address__search__searchresult__was_found=True
    ).distinct().count()

    return {
        'recent_items_today': recent_items_today,
        'recent_items_week': recent_items_week,
        'active_categories': active_categories,
    }


def get_category_tiles(now, today):
    categories = Category.objects.all()
    category_tiles = []
    
    for category in categories:
        searches_today = Search.objects.filter(
            address__category=category,
            created__date=today
        ).count()
        
        total_searches = Search.objects.filter(
            address__category=category
        ).count()
        
        items_found = SearchResult.objects.filter(
            search__address__category=category,
            was_found=True
        ).count()
        
        last_search = Search.objects.filter(
            address__category=category
        ).order_by('-created').first()
        
        hours_since_last = None
        time_ago_formatted = None
        if last_search:
            delta = now - last_search.created
            hours_since_last = int(delta.total_seconds() / 3600)
            
            total_seconds = int(delta.total_seconds())
            
            if total_seconds < 86400:  # Less than 24 hours
                if total_seconds < 3600:  # Less than 1 hour
                    minutes = total_seconds // 60
                    time_ago_formatted = f"{minutes}m ago"
                else:  # Between 1-24 hours
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    if minutes > 0:
                        time_ago_formatted = f"{hours}h {minutes}m ago"
                    else:
                        time_ago_formatted = f"{hours}h ago"
            else:  # 24+ hours
                days = total_seconds // 86400
                remaining_hours = (total_seconds % 86400) // 3600
                if remaining_hours > 0:
                    time_ago_formatted = f"{days}d {remaining_hours}h ago"
                else:
                    time_ago_formatted = f"{days}d ago"
        
        category_tiles.append({
            'id': category.id,
            'name': category.name,
            'searches_today': searches_today,
            'total_searches': total_searches,
            'items_found': items_found,
            'hours_since_last': hours_since_last,
            'time_ago_formatted': time_ago_formatted,
            'search_interval_formatted': category.search_frequency,
            'view_items_url': f'/admin/searches/item/?searchresult__search__address__category__id__exact={category.id}'
        })
    
    return category_tiles


def get_recent_items(now, yesterday):
    recent_items_queryset = Item.objects.filter(
        created__gte=yesterday
    ).select_related().prefetch_related(
        'searchresult_set__search__address__category'
    ).order_by('-created')[:10]
    
    recent_items = []
    for item in recent_items_queryset:
        search_result = item.searchresult_set.first()
        category_name = "Unknown"
        if search_result and search_result.search.address.category:
            category_name = search_result.search.address.category.name
        
        delta = now - item.created
        if delta.days > 0:
            time_ago = f"{delta.days}d ago"
        elif delta.seconds > 3600:
            time_ago = f"{delta.seconds // 3600}h ago"
        else:
            time_ago = f"{delta.seconds // 60}m ago"
        
        recent_items.append({
            'id': item.id,
            'title': item.title,
            'price': item.price,
            'currency': item.currency,
            'category': category_name,
            'url': item.url,
            'time_ago': time_ago
        })

    return recent_items


def get_chart_data(now):
    chart_labels = []
    chart_values = []
    
    for i in range(13, -1, -1):  # Last 14 days
        day = now - timedelta(days=i)
        day_str = day.strftime('%m/%d')
        chart_labels.append(day_str)
        
        items_count = Item.objects.filter(
            created__date=day.date()
        ).count()
        chart_values.append(items_count)

    return {
        'labels': chart_labels,
        'values': chart_values
    }


def get_top_categories(week_ago):
    top_categories = Category.objects.annotate(
        recent_items=Count(
            'address__search__searchresult__item',
            filter=Q(
                address__search__searchresult__item__created__gte=week_ago,
                address__search__searchresult__was_found=True
            )
        )
    ).filter(recent_items__gt=0).order_by('-recent_items')[:5]

    return [
        {
            'name': cat.name,
            'count': cat.recent_items,
            'url': f'/admin/searches/item/?searchresult__search__address__category__id__exact={cat.id}&created__gte={week_ago.strftime("%Y-%m-%d")}'
        }
        for cat in top_categories
    ]


def get_system_status(now):
    last_search = Search.objects.order_by('-created').first()
    last_search_time = "Never"
    if last_search:
        delta = now - last_search.created
        if delta.days > 0:
            last_search_time = f"{delta.days} days ago"
        elif delta.seconds > 3600:
            last_search_time = f"{delta.seconds // 3600} hours ago"
        else:
            last_search_time = f"{delta.seconds // 60} minutes ago"

    return {
        'last_search_time': last_search_time,
        'status': "Active",
    }


def dashboard_callback(request, context):
    """
    Callback function to add dashboard data to Unfold admin context.
    Provides comprehensive dashboard with category tiles, recent items, and charts.
    """
    now = timezone.now()
    today = now.date()
    yesterday = now - timedelta(days=1)
    week_ago = now - timedelta(days=7)
    
    context.update({
        'dashboard_stats': get_dashboard_stats(today, week_ago),
        'category_tiles': get_category_tiles(now, today),
        'recent_items': get_recent_items(now, yesterday),
        'yesterday': yesterday.strftime('%Y-%m-%d'),
        'chart_data': get_chart_data(now),
        'top_categories': get_top_categories(week_ago),
        'system_status': get_system_status(now),
    })
    
    return context