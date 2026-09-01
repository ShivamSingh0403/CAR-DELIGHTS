from django.shortcuts import render
from django.http import JsonResponse
from .models import Offer

def offer_list(request):
    active_offers = Offer.objects.filter(is_active=True).order_by('section')
    
    sections = {
        'daily': active_offers.filter(section='daily'),
        'weekend': active_offers.filter(section='weekend'),
        'festival': active_offers.filter(section='festival'),
        'tata': active_offers.filter(section='tata'),
        'tyres': active_offers.filter(section='tyres'),
        'services': active_offers.filter(section='services'),
        'accessories': active_offers.filter(section='accessories'),
    }

    return render(request, 'offers/offer_list.html', {
        'sections': sections,
        'all_offers': active_offers,
    })


def api_active_offers(request):
    offers = Offer.objects.filter(is_active=True)
    data = [{
        'id': o.id,
        'title': o.title,
        'subtitle': o.subtitle,
        'code': o.coupon_code,
        'discount_label': o.get_discount_label(),
        'badge': o.badge_text,
        'min_order': float(o.minimum_order),
    } for o in offers if o.is_valid_now()]
    return JsonResponse({'status': 'success', 'offers': data})
