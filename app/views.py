# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import authenticate, login
# from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import *
from swapit_app.models import *
from cart.cart import Cart
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_protect
# Create your views here.


def signup(request):
    if request.user.is_authenticated():
        return render(request, 'index.html', {'cart': Cart(request), 'categories': Category.objects.all()})

    if request.method == 'POST':
        username = request.POST.get('username')
        raw_password = request.POST.get('password')
        email = request.POST.get('email')
        user = authenticate(username=username, password=raw_password)

        if user is None:
            user = User.objects.create_user(username, email, raw_password)
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            if Cart(request):
                return redirect('/checkout/')
            return redirect('/home/')
        else:
            return render(request, 'signup.html', {'status': 'username_taken'})

    return render(request, 'signup.html', {'cart': Cart(request), 'categories': Category.objects.all(),'discount_index':DiscountOnIndex.objects.all()[0]})


@csrf_protect
def SignUpWithFaceBook(request):
    if request.user.is_authenticated():
        return render(request, 'index.html', {'cart': Cart(request), 'categories': Category.objects.all()})

    if request.method == 'POST':
        username = request.POST.get('username')
        raw_password = request.POST.get('password')
        email = request.POST.get('email')
        try:
            user = User.objects.get(username=username)
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            if Cart(request):
                return redirect('/checkout/')
            return redirect('/home/')
        except Exception as e:
            user = User.objects.create(username=username, email=email)
            user.set_password(raw_password)
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name', '')
            user.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            if Cart(request):
                return redirect('/checkout/')
            return redirect('/home/')

    return render(request, 'signup.html', {'cart': Cart(request), 'categories': Category.objects.all(),'discount_index':DiscountOnIndex.objects.all()[0]})



def index(request):
    homepage_products = HomepageProduct.objects.last()

    featured_products = homepage_products.featured_products.all()

    products = Product.objects.filter(sold=False)

    paginator = Paginator(products, 24)

    discount_in_index = DiscountOnIndex.objects.all()[0]
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    params = request.GET.copy()

    if 'page' in params.keys():
        params.pop('page')


    return render(request, 'index.html', {
        'blog': Article.objects.all().order_by('date_created'),
        'products': products,
        'paginator': paginator,
        'featured_products': Product.objects.filter(featured=True, sold=False),
        'deal_products': [product for product in Product.objects.filter(discount_expiry__isnull=False, sold=False) if product.sale_valid()],
        'cart': Cart(request),
        'categories': Category.objects.all(),
        'banners': HomepageBanner.objects.all()[:3],
        'announcements': [HomeAnnouncement1.objects.last(), HomeAnnouncement2.objects.last(),
                          HomeAnnouncement3.objects.last(), HomeAnnouncement4.objects.last()],
        'discount_index':DiscountOnIndex.objects.all()[0],                  
                       
    })


def shop(request):
    colors = request.GET.getlist('colors[]')
    colors = map(int, colors)

    brands = request.GET.getlist('brands[]')
    brands = map(int, brands)

    sizes = request.GET.getlist('sizes[]')
    sizes = map(int, sizes)

    subcategories = request.GET.getlist('subcategories[]')
    subcategories = map(int, subcategories)

    conditions = request.GET.getlist('conditions[]')

    shop_products = Product.objects.filter(sold=False)

    if 'keyword' in request.GET:
        q = request.GET['keyword']
        if q.lower() == 'medium':
            q = 'm'
            shop_products = shop_products.filter(Q(size__name__iexact=q))    
        elif q.lower() == 'large':
            q = 'l'
            shop_products = shop_products.filter(Q(size__name__iexact=q)) 
        elif q.lower().replace(' ', '') == 'xlarge':
            q = 'xl'
            shop_products = shop_products.filter(Q(size__name__iexact=q)) 
        elif q.lower() == '2xl':
            q = 'xxl'
            shop_products = shop_products.filter(Q(size__name__iexact=q)) 
        elif q.lower() == '2x':
            q = 'xxl'
            shop_products = shop_products.filter(Q(size__name__iexact=q))     
        elif q.lower() == 'xxxl':
            q = '3xl' 
            shop_products = shop_products.filter(Q(size__name__iexact=q)) 
        elif q.lower() == '3x':
            q = '3xl'  
            shop_products = shop_products.filter(Q(size__name__iexact=q))   
        elif q.lower().replace(' ', '') == 'xsmall':
            q = 'xs'
            shop_products = shop_products.filter(Q(size__name__iexact=q)) 
        elif q.lower() == 'small':
            q = 's'
            shop_products = shop_products.filter(Q(size__name__iexact=q)) 
        else:                       

            shop_products = shop_products.filter(Q(name__icontains=q) | Q(color__name__icontains=q) |
                                             Q(brand__name__icontains=q) | Q(size__name__icontains=q) |
                                             Q(status__icontains=q) | Q(category__name__icontains=q)| Q(subcategory__name__icontains=q))

    if 'category' in request.GET:
        shop_products = shop_products.filter(category=Category.objects.get(id=request.GET['category']))

    if 'subcategory' in request.GET:
        shop_products = shop_products.filter(subcategory=SubCategory.objects.get(id=request.GET['subcategory']))

    if colors:
        shop_products = shop_products.filter(color_id__in=colors)
    if brands:
        shop_products = shop_products.filter(brand_id__in=brands)
    if sizes:
        shop_products = shop_products.filter(size_id__in=sizes)
    if subcategories:
        shop_products = shop_products.filter(subcategory_id__in=subcategories)

    if 'min_price' in request.GET:
        min_price = int(request.GET['min_price'])
        shop_products = shop_products.filter(Q(price__gte=min_price) | Q(discounted_price__gte=min_price))

    if 'max_price' in request.GET:
        max_price = int(request.GET['max_price'])
        shop_products = shop_products.filter(Q(price__lte=max_price) | Q(discounted_price__lte=max_price))


    if 'new' in conditions and 'used' not in conditions:
        shop_products = shop_products.filter(status='New')

    if 'used' in conditions and 'new' not in conditions:
        shop_products = shop_products.filter(status='Used')

    if 'sort' in request.GET:
        if request.GET['sort'] == 'price-ascending':
            shop_products = shop_products.order_by('price')

        if request.GET['sort'] == 'price-descending':
            shop_products = shop_products.order_by('-price')

        if request.GET['sort'] == 'subcategory-ascending':
            shop_products = shop_products.order_by('subcategory')

        if request.GET['sort'] == 'subcategory-descending':
            shop_products = shop_products.order_by('-subcategory')

    paginator = Paginator(shop_products, 24)
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    params = request.GET.copy()

    if 'page' in params.keys():
        params.pop('page')

    return render(request, 'shop.html', {
        'products': products,
        'paginator': paginator,
        'cart': Cart(request),
        'categories': Category.objects.all(),
        'brands': Brand.objects.all().order_by('name'),
        'colors': Color.objects.all(),
        'sizes': Size.objects.all(),
        'params': params,

        'selected_colors': colors,
        'selected_brands': brands,
        'selected_sizes': sizes,
        'selected_subcategories': subcategories,
        'selected_conditions': conditions,
        'selected_sort': request.GET['sort'] if 'sort' in request.GET else 'default',
        'discount_index':DiscountOnIndex.objects.all()[0],
    })


#depricated
def filter(request):
    colors = request.GET.getlist('colors[]')
    brands = request.GET.getlist('brands[]')
    sizes = request.GET.getlist('sizes[]')
    conditions = request.GET.getlist('conditions[]')

    min_price = request.GET['min_price'][:-3]
    max_price = request.GET['max_price'][:-3]

    url_string = '/shop/?'

    for color in colors:
        url_string += 'colors%5B%5D=' + str(color) + '&'

    for brand in brands:
        url_string += 'brands%5B%5D=' + str(brand) + '&'

    for size in sizes:
        url_string += 'sizes%5B%5D=' + str(size) + '&'

    for condition in conditions:
        url_string += 'conditions%5B%5D=' + condition + '&'

    url_string += 'min_price=' + min_price + '&'
    url_string += 'max_price=' + max_price + '&'

    url_string += 'sort=' + request.GET['sort_by'] + '&'

    return HttpResponse(url_string)


def product(request):
    prod_id = int(request.GET['id'])
    sorted_products = Product.objects.filter(sold=False).order_by('id')

    from_blog = Article.objects.all()

    prev_prod = sorted_products.first()
    next_prod = sorted_products.last()

    for i, prod in enumerate(sorted_products):
        if prod.id == prod_id:
            if i - 1 in xrange(0, len(sorted_products)):
                prev_prod = sorted_products[i-1]

            if i + 1 in xrange(0, len(sorted_products)):
                next_prod = sorted_products[i+1]

    prod = Product.objects.get(id=int(request.GET['id']))
    related_products = Product.objects.filter(category=prod.category, sold=False)

    return render(request, 'product.html', {
        'product': prod,
        'cart': Cart(request),
        'next_prod': next_prod,
        'prev_prod': prev_prod,
        'related_products': related_products,
        'categories': Category.objects.all(),
        'from_blog': from_blog,
        'discount_index':DiscountOnIndex.objects.all()[0],
    })


def wishlist_add(request):
    user = request.user
    prod = Product.objects.get(id=int(request.GET['id']))
    if not prod.sold:
        user.profile.wish_list.add(prod)
    return redirect(request.GET['redirect'])


def wishlist_remove(request):
    user = request.user
    user.profile.wish_list.remove(Product.objects.get(id=int(request.GET['id'])))
    return redirect(request.GET['redirect'])


def wishlist_get(request):
    user = request.user
    return render(request, 'wishlist.html', {
        'wishlist': user.profile.wish_list.all(),
        'cart': Cart(request),
        'categories': Category.objects.all(),
        'discount_index':DiscountOnIndex.objects.all()[0]
    })


def add_to_cart(request):
    prod = Product.objects.get(id=int(request.GET['id']))
    cart = Cart(request)

    if not prod.sold:
        if prod.discounted_price:
            price = prod.discounted_price
        else:
            price = prod.price

        cart.add(prod, price, 1)
        return redirect('/cart/')
    return redirect(request.GET['redirect'])


def remove_from_cart(request):
    try:
        prod = Product.objects.get(id=int(request.GET['id']))
        cart = Cart(request)
        cart.remove(prod)
    except:
        Cart(request).clear()

    return redirect(request.GET['redirect'])


def get_cart(request):
    cart = Cart(request)
    for item in cart:
        if item.product.sold:
            cart.remove(item.product)
            return redirect(request.path)
    if cart.count() != 0:
        return render(request, 'cart.html', {'total': Cart(request).summary() + 60, 'cart': cart, 'categories': Category.objects.all()})
    else:
        return render(request, 'cart-empty.html', {'cart': cart, 'categories': Category.objects.all(),'discount_index':DiscountOnIndex.objects.all()[0]})


def exchange(request):
    url = str(HomepageProduct.objects.last().exchange_video_link)
    width_substring = url[url.index('width') : url.index('"', url.index('width')+7)+1]
    url = url.replace(width_substring, 'width="100%"')
    width_substring = url[url.index('height') : url.index('"', url.index('height')+8)+1]
    url = url.replace(width_substring, 'height="100%"')
    # return HttpResponse(url)
    video_tutorial = ExchangePageVideo.objects.last().link
    return render(request, 'exchange.html', {
        'cart': Cart(request),
        'categories': Category.objects.all(),
        'url': url,
        'discount_index':DiscountOnIndex.objects.all()[0],
        'video_tutorial':video_tutorial
    })


def sell(request):
    return render(request, 'sell.html', {
        'cart': Cart(request),
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
        'products': Product.objects.filter(sold=False).order_by('?')[:16],
        'discount_index':DiscountOnIndex.objects.all()[0],
    })


def save_seller(request):
    print request.GET['payment']
    seller = Seller(
        name=request.GET['name'],
        payment_type=request.GET['payment'],
        email=request.GET['email'],
        phone=request.GET['phone'],
        address=request.GET['address'],
        preferred_picking_time=request.GET['picking-time'],
        comment=request.GET['comment']
    )

    seller.save()


    body = 'A new seller has been added: '
    body += '<br>name: ' + seller.name
    body += '<br>email: ' + seller.email
    body += '<br>payment: ' + seller.payment_type
    body += '<br>phone: ' + seller.phone
    body += '<br>address: ' + seller.address
    body += '<br>picking-time: ' + seller.preferred_picking_time
    body += '<br>comment: ' + seller.comment
    send_email(body, 'New Seller Notification', 'info@swapitclothing.com')


    return redirect('/sell/')


def checkout(request):
    promocode = False
    new_total = float(Cart(request).summary())
    old_total = float(Cart(request).summary())
    discount = 0
    if 'promocode' in request.session:
        try:
            promocode = PromoCode.objects.get(code=request.session['promocode'])
            if promocode.valid():
                new_total = float(new_total) - (float(new_total) * promocode.factor())
                discount = old_total - new_total
        except:
            pass

    return render(request, 'checkout.html', {'new_total':new_total + 60, 'discount':discount, 'promocode':promocode, 'total': Cart(request).summary() + 60, 'cart': Cart(request), 'categories': Category.objects.all(),'discount_index':DiscountOnIndex.objects.all()[0]})




def blog(request):
    blog_posts = Article.objects.all().order_by('date_created')

    paginator = Paginator(blog_posts, 3)
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:

        posts = paginator.page(1)
    except EmptyPage:

        posts = paginator.page(paginator.num_pages)

    return render(request, 'blog.html', {
        'products': Product.objects.filter(featured=True, sold=False),
        'cart': Cart(request),
        'categories': Category.objects.all(),
        'paginator': paginator,
        'blog': posts,
        'discount_index':DiscountOnIndex.objects.all()[0],
    })


def article(request):
    return render(request, 'blog-single.html', {
        'products': Product.objects.filter(featured=True, sold=False),
        'cart': Cart(request),
        'categories': Category.objects.all(),
        'article': Article.objects.get(id=int(request.GET['id'])),
        'discount_index':DiscountOnIndex.objects.all()[0]
    })


def about(request):
    return render(request, 'about.html', {
        'blog': Article.objects.all().order_by('date_created'),
        'cart': Cart(request),
        'brands': Brand.objects.all(),
        'deals': Product.objects.filter(featured=True, sold=False),
        'categories': Category.objects.all(),
        'discount_index':DiscountOnIndex.objects.all()[0],
    })


def contact(request):
    return render(request, 'contact.html', {'cart': Cart(request), 'categories': Category.objects.all(),'discount_index':DiscountOnIndex.objects.all()[0]})

def privacy_policy(request):
    return render(request, 'privacy-policy.html',)

@login_required
def account_details(request):
    return render(request, 'account_details.html', {
        'cart': Cart(request),
        'categories': Category.objects.all(),
        'discount_index':DiscountOnIndex.objects.all()[0]
    })

@login_required
def account_wishlist(request):
    user = request.user
    return render(request, 'account_wishlist.html', {
        'wishlist': user.profile.wish_list.all(),
        'cart': Cart(request),
        'categories': Category.objects.all(),
        'discount_index':DiscountOnIndex.objects.all()[0]
    })

@login_required
def account_history(request):
    user = request.user
    return render(request, 'account_history.html', {
        'orders': user.order_set.all(),
        'cart': Cart(request),
        'categories': Category.objects.all(),
        'discount_index':DiscountOnIndex.objects.all()[0],
    })


def test(request):
    return render(request, 'new_order_email.html', {'discount_index':DiscountOnIndex.objects.all()[0]})    


def place_order(request):
    arr = []
      

    if Cart(request).count() == 0:
       return redirect('/checkout/')

    total = 0
    prods = []
    cart = Cart(request)
    for item in cart:
        if item.product.sold:
            cart.remove(item.product)
            return redirect('/checkout/')
        else:
            if item.product.sale_valid():
                total += item.product.discounted_price
                prods.append((item.product, item.product.discounted_price))
            else:
                total += item.product.price
                prods.append((item.product, item.product.price))

    promocode = False
    new_total = total
    old_total = new_total
    discount = 0
    if 'promocode' in request.session:
        try:
            promocode = PromoCode.objects.get(code=request.session['promocode'])
            if promocode.valid():
                new_total = float(new_total) - (float(new_total) * promocode.factor())
                discount = old_total - new_total
        except:
            pass

    order = Order(
        phone=request.GET['phone'],
        name=request.GET['first_name'] + ' ' + request.GET['last_name'],
        email=request.GET['email'],

        country=request.GET.get('country',''),
        province=request.GET.get('province',''),
        city=request.GET.get('city',''),
        address=request.GET.get('address',''),
        postcode=request.GET.get('postcode',''),
        note=request.GET.get('note','')
    )
    try:
        order.user=request.user
    except Exception as e:
        pass    


    order.save()
    if promocode:
        order.promocode = promocode
        order.save()

    for prod in prods:
        prod[0].order = order
        prod[0].sold = True
        prod[0].save()       




    order.total = new_total
    order.save()
    Cart(request).clear()

    if 'promocode' in request.session:
        del request.session['promocode']
        request.session.modified = True

    x = render_to_string(
        'new_order_email.html',
        {'prods': prods, 'total': order.total},
        RequestContext(request)
    )
    try:
        send_email(x, 'Thank you for your order', str(order.email))
    except:
        # raise
        pass

    #mail to project owner

    x = render_to_string(
        'owner_order_email.html',
        {'prods': prods, 'total': order.total,'order':order},
        RequestContext(request)
    )
    try:
        send_email(x, 'New Order Notification - SwapIt', 'shadyk@aucegypt.edu')
    except:
        # raise
        pass    
    
    if request.user.is_authenticated():

        return redirect('/account_history/')
    else :
        return redirect('/')

def order_details(request):
    id = phone=request.GET['id']
    order = Order.objects.get(id=id)
    order_products = Product.objects.filter(order=order)
    return render(request, 'order-details.html', {
        'order': order,
        'order_products': order_products,
        'total': order.total + 60,
        'discount_index':DiscountOnIndex.objects.all()[0],
        })

def send_email(body, subject, recipient):
    import smtplib
    from smtplib import SMTP
    from email.MIMEText import MIMEText
    from email.Header import Header
    from email.Utils import parseaddr, formataddr
    """Send an email.

    All arguments should be Unicode strings (plain ASCII works as well).

    Only the real name part of sender and recipient addresses may contain
    non-ASCII characters.

    The email will be properly MIME encoded and delivered though SMTP to
    localhost port 25.  This is easy to change if you want something different.

    The charset of the email will be the first one out of US-ASCII, ISO-8859-1
    and UTF-8 that can represent all the characters occurring in the email.
    """

    sender = 'info@swapitclothing.com'
    # Header class is smart enough to try US-ASCII, then the charset we
    # provide, then fall back to UTF-8.
    header_charset = 'ISO-8859-1'

    # We must choose the body charset manually
    for body_charset in 'US-ASCII', 'ISO-8859-1', 'UTF-8':
        try:
            body.encode(body_charset)
        except UnicodeError:
            pass
        else:
            break

    # Split real name (which is optional) and email address parts
    sender_name, sender_addr = parseaddr(sender)
    recipient_name, recipient_addr = parseaddr(recipient)

    # We must always pass Unicode strings to Header, otherwise it will
    # use RFC 2047 encoding even on plain ASCII strings.
    sender_name = str(Header(unicode(sender_name), header_charset))
    recipient_name = str(Header(unicode(recipient_name), header_charset))

    # Make sure email addresses do not contain non-ASCII characters
    sender_addr = sender_addr.encode('ascii')
    recipient_addr = recipient_addr.encode('ascii')

    # Create the message ('plain' stands for Content-Type: text/plain)
    msg = MIMEText(body.encode(body_charset), 'html', body_charset)
    msg['From'] = formataddr((sender_name, sender_addr))
    msg['To'] = formataddr((recipient_name, recipient_addr))
    msg['Subject'] = Header(unicode(subject), header_charset)

    # Create server object with SSL option
    server = smtplib.SMTP_SSL('smtp.{{service provider}}.com', 465)

    # Perform operations via server
    server.login(sender, '{pass}')
    server.sendmail(sender, [recipient], msg.as_string())
    server.quit()

def sslVerify(request):
    return render_to_response('ssl.txt')

def apply_promo_code(request):
    request.session['promocode'] = request.GET['code']
    return HttpResponseRedirect('/checkout/')


def thankyou(request):

    return render(request, 'thankyou.html', {'discount_index':DiscountOnIndex.objects.all()[0]})

