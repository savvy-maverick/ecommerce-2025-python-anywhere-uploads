from .cart import Cart

# create context processors so cart can work on all pages
def cart(request):
    # return default data from our Cart
    return {'cart': Cart(request)}