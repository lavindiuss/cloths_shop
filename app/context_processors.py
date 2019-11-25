

from swapit_app.models import DiscountOnIndex


def header_processor(request):
    return {
        'discount_on_index': DiscountOnIndex.objects.all()[0],
    }
