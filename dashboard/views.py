from django.shortcuts import render
from django.db.models import Q

from products.models import Product
from categories.models import Category

from cart.models import Cart
from wishlist.models import Wishlist

from orders.models import Order
from accounts.models import CustomUser

import re
from difflib import SequenceMatcher


# =========================================================
# SMART SEARCH HELPERS
# =========================================================

def normalize_word(word):
    """
    Convert search words into a simple normalized form.

    Examples:
        pencils  -> pencil
        books    -> book
        pens     -> pen
        notebooks -> notebook
    """

    word = word.lower().strip()

    # Remove common punctuation
    word = re.sub(r'[^a-z0-9]', '', word)

    if not word:
        return ''

    # Simple plural handling
    if len(word) > 4:

        if word.endswith('ies'):
            word = word[:-3] + 'y'

        elif word.endswith('sses'):
            word = word[:-2]

        elif word.endswith('es'):
            word = word[:-2]

        elif word.endswith('s'):
            word = word[:-1]

    return word


def similarity(word1, word2):
    """
    Return similarity between 0 and 1.
    """

    return SequenceMatcher(
        None,
        word1,
        word2
    ).ratio()


def get_text_words(text):
    """
    Convert text into clean searchable words.
    """

    if not text:
        return []

    words = re.findall(
        r'[a-zA-Z0-9]+',
        str(text).lower()
    )

    return [
        normalize_word(word)
        for word in words
        if normalize_word(word)
    ]


def calculate_product_score(product, query):
    """
    Calculate how relevant a product is to the user's search.

    Higher score = more relevant product.
    """

    if not query:
        return 0

    query = query.lower().strip()

    query_words = [
        normalize_word(word)
        for word in query.split()
        if normalize_word(word)
    ]

    if not query_words:
        return 0

    # -----------------------------------------------------
    # PRODUCT DATA
    # -----------------------------------------------------

    name = str(
        product.name or ''
    ).lower()

    description = str(
        product.description or ''
    ).lower()

    category_name = ''

    if product.category:
        category_name = str(
            product.category.name or ''
        ).lower()

    # -----------------------------------------------------
    # WORDS FROM EACH FIELD
    # -----------------------------------------------------

    name_words = get_text_words(
        name
    )

    description_words = get_text_words(
        description
    )

    category_words = get_text_words(
        category_name
    )

    # -----------------------------------------------------
    # NORMALIZED FULL TEXT
    # -----------------------------------------------------

    normalized_name = ' '.join(
        name_words
    )

    normalized_description = ' '.join(
        description_words
    )

    normalized_category = ' '.join(
        category_words
    )

    score = 0

    # =====================================================
    # EXACT FULL QUERY MATCH
    # =====================================================

    if query in name:

        score += 100

    elif query in description:

        score += 45

    elif query in category_name:

        score += 35

    # =====================================================
    # EACH SEARCH WORD
    # =====================================================

    for search_word in query_words:

        if not search_word:
            continue

        best_name_score = 0
        best_description_score = 0
        best_category_score = 0

        # -------------------------------------------------
        # NAME MATCHING
        # -------------------------------------------------

        for product_word in name_words:

            if not product_word:
                continue

            # Exact
            if search_word == product_word:

                best_name_score = max(
                    best_name_score,
                    100
                )

                continue

            # Substring
            if (
                len(search_word) >= 3
                and (
                    search_word in product_word
                    or product_word in search_word
                )
            ):

                best_name_score = max(
                    best_name_score,
                    85
                )

                continue

            # Fuzzy spelling
            if (
                len(search_word) >= 4
                and len(product_word) >= 4
            ):

                ratio = similarity(
                    search_word,
                    product_word
                )

                if ratio >= 0.75:

                    fuzzy_score = int(
                        ratio * 80
                    )

                    best_name_score = max(
                        best_name_score,
                        fuzzy_score
                    )

        # -------------------------------------------------
        # DESCRIPTION MATCHING
        # -------------------------------------------------

        for product_word in description_words:

            if not product_word:
                continue

            if search_word == product_word:

                best_description_score = max(
                    best_description_score,
                    55
                )

                continue

            if (
                len(search_word) >= 4
                and len(product_word) >= 4
            ):

                ratio = similarity(
                    search_word,
                    product_word
                )

                if ratio >= 0.78:

                    fuzzy_score = int(
                        ratio * 45
                    )

                    best_description_score = max(
                        best_description_score,
                        fuzzy_score
                    )

        # -------------------------------------------------
        # CATEGORY MATCHING
        # -------------------------------------------------

        for product_word in category_words:

            if not product_word:
                continue

            if search_word == product_word:

                best_category_score = max(
                    best_category_score,
                    65
                )

                continue

            if (
                len(search_word) >= 4
                and len(product_word) >= 4
            ):

                ratio = similarity(
                    search_word,
                    product_word
                )

                if ratio >= 0.78:

                    fuzzy_score = int(
                        ratio * 55
                    )

                    best_category_score = max(
                        best_category_score,
                        fuzzy_score
                    )

        # -------------------------------------------------
        # ADD BEST MATCH
        # -------------------------------------------------

        score += max(
            best_name_score,
            best_description_score,
            best_category_score
        )

    # =====================================================
    # MULTI-WORD QUERY BONUS
    # =====================================================

    if len(query_words) > 1:

        matched_words = 0

        for search_word in query_words:

            found = False

            for product_word in name_words:

                if (
                    search_word == product_word
                    or (
                        len(search_word) >= 4
                        and len(product_word) >= 4
                        and similarity(
                            search_word,
                            product_word
                        ) >= 0.75
                    )
                ):

                    found = True
                    break

            if found:
                matched_words += 1

        if matched_words == len(query_words):

            score += 50

        elif matched_words > 0:

            score += (
                matched_words * 15
            )

    # =====================================================
    # FINAL FULL NAME BONUS
    # =====================================================

    if normalized_name:

        normalized_query = ' '.join(
            query_words
        )

        if (
            normalized_query
            and normalized_query in normalized_name
        ):

            score += 40

    return score


# =========================================================
# HOME
# =========================================================

def home(request):

    query = request.GET.get(
        'q',
        ''
    ).strip()

    category_id = request.GET.get(
        'category'
    )

    # =====================================================
    # PRODUCTS
    # =====================================================

    products = Product.objects.select_related(
        'category'
    ).all()

    # =====================================================
    # CATEGORY FILTER
    # =====================================================

    if category_id:

        products = products.filter(
            category_id=category_id
        )

    # =====================================================
    # SMART SEARCH
    # =====================================================

    if query:

        # -------------------------------------------------
        # First get all products
        # -------------------------------------------------

        all_products = list(
            products
        )

        scored_products = []

        # -------------------------------------------------
        # Calculate relevance score
        # -------------------------------------------------

        for product in all_products:

            score = calculate_product_score(
                product,
                query
            )

            # -------------------------------------------------
            # Only keep genuinely relevant results
            # -------------------------------------------------

            if score >= 45:

                scored_products.append(
                    (
                        score,
                        product
                    )
                )

        # -------------------------------------------------
        # Sort highest relevance first
        # -------------------------------------------------

        scored_products.sort(
            key=lambda item: item[0],
            reverse=True
        )

        # -------------------------------------------------
        # Convert back to products
        # -------------------------------------------------

        products = [
            product
            for score, product
            in scored_products
        ]

    # =====================================================
    # CATEGORIES
    # =====================================================

    categories = Category.objects.all()

    # =====================================================
    # DEFAULT COUNTERS / LISTS
    # =====================================================

    cart_count = 0

    wishlist_count = 0

    my_orders_count = 0

    wishlisted_products = []

    # =====================================================
    # IMPORTANT:
    # CART PRODUCTS
    #
    # This list tells home.html which products are already
    # inside the user's cart.
    # =====================================================

    cart_products = []

    # =====================================================
    # USER DATA
    # =====================================================

    if request.user.is_authenticated:

        # -------------------------------------------------
        # CART
        # -------------------------------------------------

        cart, created = Cart.objects.get_or_create(
            user=request.user
        )

        cart_items = cart.items.select_related(
            'product'
        ).all()

        # -------------------------------------------------
        # CART TOTAL QUANTITY
        # -------------------------------------------------

        cart_count = sum(
            item.quantity
            for item in cart_items
        )

        # -------------------------------------------------
        # CART PRODUCT IDS
        #
        # THIS FIXES THE REFRESH PROBLEM.
        # -------------------------------------------------

        cart_products = [
            item.product.id
            for item in cart_items
        ]

        # -------------------------------------------------
        # WISHLIST
        # -------------------------------------------------

        wishlist_items = Wishlist.objects.filter(
            user=request.user
        )

        wishlist_count = wishlist_items.count()

        # -------------------------------------------------
        # ORDERS
        # -------------------------------------------------

        my_orders_count = Order.objects.filter(
            user=request.user
        ).count()

        # -------------------------------------------------
        # WISHLISTED PRODUCT IDS
        # -------------------------------------------------

        wishlisted_products = [
            item.product.id
            for item in wishlist_items
        ]

    # =====================================================
    # DASHBOARD STATS
    # =====================================================

    total_products = Product.objects.count()

    total_orders = Order.objects.count()

    total_customers = CustomUser.objects.count()

    revenue = sum(
        order.total_amount
        for order in Order.objects.all()
    )

    # =====================================================
    # RENDER
    # =====================================================

    return render(
        request,
        'home.html',
        {

            'products': products,

            'categories': categories,

            'cart_count': cart_count,

            # IMPORTANT FIX
            'cart_products': cart_products,

            'wishlist_count': wishlist_count,

            'my_orders_count': my_orders_count,

            'wishlisted_products':
                wishlisted_products,

            'total_products':
                total_products,

            'total_orders':
                total_orders,

            'total_customers':
                total_customers,

            'revenue':
                revenue,

            'query':
                query,

        }
    )