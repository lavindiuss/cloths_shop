# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models import *
from django.utils import timezone
from unique_upload import unique_upload
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe


def validate_only_one_instance(obj):
    model = obj.__class__
    if (model.objects.count() > 0 and
            obj.id != model.objects.get().id):
        raise ValidationError("Can only create 1 %s instance" % model.__name__)


def file_upload(instance, filename):
    return 'images/' + unique_upload(instance, filename)


def validate_image(image):
    file_size = image.file.size
    limit_kb = 900
    if file_size > limit_kb * 1024:
        raise ValidationError('Please keep image size under %s KB. Current size %s KB' % (limit_kb, file_size/1024))


# Create your models here.


class Size(Model):
    name = CharField(max_length=20)

    def __unicode__(self):
        return self.name


class Tag(Model):
    name = CharField(max_length=20)

    def __unicode__(self):
        return self.name


class Color(Model):
    name = CharField(max_length=20)
    color_code = CharField(max_length=50, null=True, blank=True)
    thumbnail = ImageField(upload_to=file_upload, null=True, blank=True, validators=[validate_image])

    def __unicode__(self):
        return self.name


class Brand(Model):
    name = CharField(max_length=20)
    logo = ImageField(upload_to=file_upload, null=True, blank=True, validators=[validate_image])

    def __unicode__(self):
        return self.name


class Category(Model):
    name = CharField(max_length=20)
    css_name = CharField(max_length=20, null=True, blank=True)
    image = ImageField(upload_to=file_upload, null=True, blank=True, validators=[validate_image])
    color = ForeignKey('Color', null=True, blank=True)

    def __unicode__(self):
        return self.name

    @property
    def sorted_subcategories(self):
        return self.subcategory_set.order_by('priority')

    class Meta:
        verbose_name_plural = 'categories'



class SubCategory(Model):
    name = CharField(max_length=100)
    category = ForeignKey(Category, on_delete=CASCADE)
    priority = IntegerField(default=0)

    def __unicode__(self):
        return self.name


    class Meta:
        verbose_name_plural = 'subcategories'


class Profile(Model):
    user = OneToOneField(User, on_delete=CASCADE)
    address = TextField(blank=True, null=True)
    balance = FloatField(default=0.0)
    wish_list = ManyToManyField('Product', blank=True)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    def __unicode__(self):
        return self.user.first_name + ' ' + self.user.last_name


class Seller(Model):
    name = CharField(max_length=100, null=True, blank=True)
    payment_type = CharField(max_length=20)
    email = CharField(max_length=100)
    phone = CharField(max_length=100)
    address = TextField()
    preferred_picking_time = CharField(max_length=50)
    comment = TextField(blank=True, null=True)

    def __unicode__(self):
        return self.name


class Product(Model):
    name = CharField(max_length=30)
    availability = CharField(max_length=30, choices=(('In Stock', 'In Stock'), ('Out of Stock', 'Out of Stock')))
    featured = BooleanField()
    description = TextField(null=True, blank=True)
    status = CharField(max_length=30, choices=(('New', 'New'), ('Pre-owned', 'Pre-owned')))
    price = FloatField()
    brand = ForeignKey(Brand, null=True, blank=True)
    category = ForeignKey(Category, null=True, blank=True)
    subcategory = ForeignKey(SubCategory, null=True, blank=True)

    discounted_price = FloatField(null=True, blank=True)
    discount_percentage = IntegerField(blank=True, null=True)
    discount_expiry = DateTimeField(blank=True, null=True)
    # quantity = IntegerField()
    sku = CharField(max_length=128, blank=True, null=True)
    date_created = DateTimeField(auto_now_add=True)

    size = ForeignKey('Size', null=True, blank=True)
    color = ForeignKey('Color', null=True, blank=True, related_name='c1')
    color2 = ForeignKey('Color', null=True, blank=True, related_name='c2')
    color3 = ForeignKey('Color', null=True, blank=True, related_name='c3')
    tags = ManyToManyField('Tag', blank=True)

    sold = BooleanField(default=False)
    order = ForeignKey('Order', null=True, blank=True, on_delete=SET_NULL)


    def __unicode__(self):
        return self.name

    def sale_valid(self):
        if not self.discount_expiry or not self.discounted_price or not self.discount_percentage:
            return False
        return self.discount_expiry > timezone.now()

    def low_res_image(self):
        try:
            return LowResImage.objects.filter(product=self)[0].image.url
        except:
            return 'No Image'

    def get_image(self):
        try:
            image = Image.objects.filter(product=self)[0]

            return mark_safe('<img src="{url}"  height={height} />'.format(
                url = image.image.url,
                height=200,
                )
            )
        except:
            return 'No Image'


class Image(Model):
    image = ImageField(upload_to=file_upload, verbose_name='high res image', validators=[validate_image])
    product = ForeignKey(Product, on_delete=CASCADE)

    def __unicode__(self):
        return str(self.id)

    class Meta:
        verbose_name = 'high res image'
        verbose_name_plural = 'high res images'


class LowResImage(Model):
    image = ImageField(upload_to=file_upload, verbose_name='low res image', validators=[validate_image])
    product = ForeignKey(Product, on_delete=CASCADE)

    def __unicode__(self):
        return str(self.id)


class ProductSpec(Model):
    name = CharField(max_length=100, null=True, blank=True)
    value = CharField(max_length=100, null=True, blank=True)
    product = ForeignKey(Product, on_delete=CASCADE)

    def __unicode__(self):
        return self.name


class Review(Model):
    user = ForeignKey(User, on_delete=CASCADE)
    product = ForeignKey(Product, on_delete=CASCADE)

    price = IntegerField()
    value = IntegerField()
    quality = IntegerField()

    text = TextField()

    def __unicode__(self):
        return str(self.id)


class Article(Model):
    image = ImageField(upload_to=file_upload, validators=[validate_image])
    title = CharField(max_length=50)
    author = CharField(max_length=30, null=True, blank=True)
    date_created = DateTimeField(auto_now_add=True)
    tags = ManyToManyField('Tag', related_name='articles')

    def __unicode__(self):
        return self.title


class HomepageBanner(Model):
    image = ImageField(upload_to=file_upload, validators=[validate_image])
    title = CharField(max_length=300, null=True, blank=True)
    font_size = CharField(max_length=300,choices=[(str(i)+'%',str(i)+'%') for i in range(300)],null=True, blank=True)
    title_color = CharField(max_length=300, null=True, blank=True)
    subtitle = CharField(max_length=300, null=True, blank=True)
    subtitle_color = CharField(max_length=300, null=True, blank=True)

    button_text = CharField(max_length=300, null=True, blank=True)
    button_text_color = CharField(max_length=300, null=True, blank=True)
    button_color = CharField(max_length=300, null=True, blank=True)
    button_font_size = CharField(max_length=300,choices=[(str(i)+'%',str(i)+'%') for i in range(300)],null=True, blank=True)
    button_url = TextField(null=True, blank=True)

    def __unicode__(self):
        return self.title


class Section(Model):
    article = ForeignKey(Article, on_delete=CASCADE)
    type = CharField(max_length=30, choices=(('paragraph', 'paragraph'), ('quote', 'quote')))
    text = TextField()


class Order(Model):
    user = ForeignKey(User,blank=True, null=True)
    phone = CharField(max_length=128)
    name = CharField(max_length=128)
    email = CharField(max_length=128)

    country = CharField(max_length=128, blank=True, null=True)
    city = CharField(max_length=128, blank=True, null=True)
    province = CharField(max_length=128, blank=True, null=True)
    address = TextField(null=True, blank=True)
    postcode = CharField(max_length=128, blank=True, null=True)

    total = FloatField(null=True, blank=True)
    date_placed = DateTimeField(auto_now_add=True)
    date_shipped = DateTimeField(blank=True, null=True)
    status = CharField(max_length=128, default='Processing', choices=(
        ('Processing', 'Processing'), ('Confirmed', 'Confirmed'), ('Out for shipping', 'Out for shipping'),
        ('Delivered', 'Delivered')))
    note = TextField(blank=True, null=True)

    promocode = ForeignKey('PromoCode', blank=True, null=True)
    # discount = FloatField(default=0)


    def __unicode__(self):
        return self.name


class HomeAnnouncement1(Model):
    image = ImageField(upload_to=file_upload, validators=[validate_image])
    title = TextField(null=True, blank=True)
    sub_title = TextField(null=True, blank=True)
    text = TextField(null=True, blank=True)
    url = URLField(null=True, blank=True)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = 'Announcement 1 (Top Left)'
        verbose_name_plural = 'Announcement 1 (Top Left)'



class HomeAnnouncement2(Model):
    image = ImageField(upload_to=file_upload, validators=[validate_image])
    title = TextField(null=True, blank=True)
    sub_title = TextField(null=True, blank=True)
    url = URLField(null=True, blank=True)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = 'Announcement 2 (Top Right)'
        verbose_name_plural = 'Announcement 2 (Top Right)'



class HomeAnnouncement3(Model):
    image = ImageField(upload_to=file_upload, validators=[validate_image])
    title = TextField(null=True, blank=True)
    sub_title = TextField(null=True, blank=True)
    button_text = TextField(null=True, blank=True)
    url = URLField(null=True, blank=True)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = 'Announcement 3 (Bottom Left)'
        verbose_name_plural = 'Announcement 3 (Bottom Left)'



class HomeAnnouncement4(Model):
    image = ImageField(upload_to=file_upload, validators=[validate_image])
    title = TextField(null=True, blank=True)
    sub_title = TextField(null=True, blank=True)
    url = URLField(null=True, blank=True)

    def __unicode__(self):
        return self.title

    class Meta:
        verbose_name = 'Announcement 4 (Bottom Right)'
        verbose_name_plural = 'Announcement 4 (Bottom Right)'


class HomepageProduct(Model):
    featured_products = ManyToManyField('Product', blank=True, related_name='featured_products')
    deal_of_the_day_products = ManyToManyField('Product', blank=True, related_name='deal_of_the_day_products')
    exchange_video_link = TextField(null=True, blank=True, help_text='Use youtube embed code.')

    def __unicode__(self):
        return 'Deal Of The Day Products / Exchange Video URL'

    def clean(self):
        validate_only_one_instance(self)

    class Meta:
        verbose_name = 'Deal Of The Day Products / Exchange Video URL'
        verbose_name_plural = 'Deal Of The Day Products / Exchange Video URL'

class PromoCode(Model):
    code = CharField(unique=True, max_length=12)
    percent_discount = IntegerField(default=10)
    multiple_use = BooleanField(default=True)
    active = BooleanField(default=True)

    def __unicode__(self):
        return self.code

    def factor(self):
        return float(self.percent_discount)/100.0

    def number_of_uses(self):
        return Order.objects.filter(promocode=self).count()

    def valid(self):
        if not self.active:
            return False
        if self.multiple_use:
            return True
        uses = self.number_of_uses
        if uses < 1:
            return True
        return False



""" for percentage tag on index """ 

class DiscountOnIndex(Model):

    slug = CharField(max_length=100)


class ExchangePageVideo(Model):

    link = CharField(max_length=300,blank=True,null=True)