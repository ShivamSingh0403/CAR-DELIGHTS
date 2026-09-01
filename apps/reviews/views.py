from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review
from apps.products.models import Product
from apps.services.models import Service
from apps.orders.models import OrderItem
from apps.services.models import ServiceBooking

@login_required
def add_product_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    # Check if user purchased this product
    has_purchased = OrderItem.objects.filter(order__user=request.user, product=product).exists()
    
    if request.method == 'POST':
        rating = request.POST.get('rating', 5)
        title = request.POST.get('title', '').strip()
        comment = request.POST.get('comment', '').strip()
        image = request.FILES.get('image')

        if not (title and comment):
            messages.error(request, "Please enter both a title and review comment.")
            return render(request, 'reviews/add_review.html', {'item': product, 'item_type': 'product'})

        Review.objects.create(
            user=request.user,
            product=product,
            rating=int(rating),
            title=title,
            comment=comment,
            image=image,
            is_verified_purchase=has_purchased,
            is_approved=True
        )

        # Update product average rating
        all_revs = product.reviews.filter(is_approved=True)
        if all_revs.exists():
            avg_rating = sum(r.rating for r in all_revs) / all_revs.count()
            product.rating = round(avg_rating, 1)
            product.review_count = all_revs.count()
            product.save(update_fields=['rating', 'review_count'])

        messages.success(request, "Thank you! Your verified review has been published.")
        return redirect('products:product_detail', slug=product.slug)

    return render(request, 'reviews/add_review.html', {
        'item': product,
        'item_type': 'product',
        'has_purchased': has_purchased
    })
