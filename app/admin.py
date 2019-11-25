# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from swapit_app.models import *
from django.contrib import admin
from swapit_app.forms import *
import xlwt
from django.http import HttpResponse
from django.utils.safestring import mark_safe
admin.site.site_header = 'SWAPIT administration'
# Register your models here.


def get_excel_sellers(modeladmin, request, queryset):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Sellers.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('Sheet')

    style = xlwt.XFStyle()

    font = xlwt.Font()
    font.bold = True
    style.font = font
    style.borders.bottom = True
    style.borders.DOUBLE = True

    row = sheet.row(0)
    row.write(0, 'Name', style)
    row.write(1, 'Email', style)

    row.write(2, 'Phone', style)
    row.write(3, 'Address', style)

    row.write(4, 'Payment Type', style)
    row.write(5, 'Preferred Picking Time', style)

    row.write(6, 'Comment', style)

    for index, seller in enumerate(queryset):
        row = sheet.row(index + 1)

        row.write(0, seller.name)
        row.write(1, seller.email)

        row.write(2, seller.phone)
        row.write(3, seller.address)

        row.write(4, seller.payment_type)
        row.write(5, seller.preferred_picking_time)

        row.write(6, seller.comment)


    wb.save(response)
    return response


get_excel_sellers.short_description = "Generate excel sheet for selected sellers."


def get_excel_orders(modeladmin, request, queryset):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Orders.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    sheet = wb.add_sheet('Sheet')

    style = xlwt.XFStyle()

    font = xlwt.Font()
    font.bold = True
    style.font = font
    style.borders.bottom = True
    style.borders.DOUBLE = True

    row = sheet.row(0)
    row.write(0, 'User Name', style)
    row.write(1, 'Email', style)
    row.write(2, 'Phone', style)

    row.write(3, 'country', style)
    row.write(4, 'city', style)
    row.write(5, 'province', style)
    row.write(6, 'Address', style)

    row.write(7, 'total', style)

    row.write(8, 'date_placed', style)
    row.write(9, 'date_shipped', style)
    row.write(10, 'status', style)
    row.write(11, 'note', style)

    row.write(12, 'No. of items', style)

    for index, order in enumerate(queryset):
        row = sheet.row(index + 1)

        row.write(0, order.name)
        row.write(1, order.email)
        row.write(2, order.phone)

        row.write(3, order.country)
        row.write(4, order.city)
        row.write(5, order.province)
        row.write(6, order.address)

        row.write(7, order.total)
        row.write(8, order.date_placed.strftime('%d %b %Y, %I:%M %p'))

        row.write(9, order.date_shipped.strftime('%d %b %Y, %I:%M %p') if order.date_shipped else 'NA')
        row.write(10, order.status)
        row.write(11, order.note)
        
        row.write(12, str(order.product_set.count()))


    wb.save(response)
    return response


get_excel_orders.short_description = "Generate excel sheet for selected orders."


class ImageInline(admin.TabularInline):
    model = Image


class LowResImageInline(admin.TabularInline):
    model = LowResImage


class ProductSpecInline(admin.TabularInline):
    model = ProductSpec


class ProductAdmin(admin.ModelAdmin):
    inlines = [
        ImageInline,
        LowResImageInline,
        ProductSpecInline,
    ]
    list_display = ('name', 'get_image', 'featured')
    search_fields = ['brand__name', 'category__name', 'subcategory__name']
    list_filter = ['brand', 'category', 'subcategory']

    


class SectionInline(admin.TabularInline):
    model = Section


class ArticleAdmin(admin.ModelAdmin):
    inlines = [
        SectionInline
    ]


class HomepageBannerAdmin(admin.ModelAdmin):
    form = HomepageBannerForm
    fields = ('image', 'title', 'title_color', 'subtitle', 'subtitle_color', 'button_text', 'button_text_color',
              'button_color', 'button_url','font_size','button_font_size')


class SellerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'address', 'payment_type', 'preferred_picking_time', 'comment')
    actions = [get_excel_sellers]


class HomepageProductAdmin(admin.ModelAdmin):
    exclude = ('featured_products', )
    filter_horizontal = ('deal_of_the_day_products', )


class ProductInline(admin.StackedInline):
    model = Product
    readonly_fields = ['get_image',]



class OrderAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'city', 'date_placed', 'date_shipped', 'status')
    actions = [get_excel_orders]
    inlines = [ProductInline,]


admin.site.register(Product, ProductAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Profile)
admin.site.register(Color)
admin.site.register(Size)
admin.site.register(Image)
admin.site.register(Tag)
admin.site.register(Review)
admin.site.register(Brand)
admin.site.register(Category)
admin.site.register(SubCategory)
admin.site.register(Seller, SellerAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(HomepageBanner, HomepageBannerAdmin)
admin.site.register(HomeAnnouncement2)
admin.site.register(HomeAnnouncement3)
admin.site.register(PromoCode)
admin.site.register(HomepageProduct, HomepageProductAdmin)
admin.site.register(DiscountOnIndex)
admin.site.register(ExchangePageVideo)
