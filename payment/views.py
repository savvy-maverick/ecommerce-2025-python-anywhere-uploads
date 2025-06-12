from django.shortcuts import render, redirect
from cart.cart import Cart
from .forms import ShippingForm, PaymentForm
from .models import ShippingAddress
from django.contrib import messages
from .models import Order, OrderItem
from django.contrib.auth.models import User
from store.models import Product
import datetime


# Create your views here.

def orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        # get order
        order= Order.objects.get(id=pk)
        # get the order items
        items = OrderItem.objects.filter(order=pk)

        if request.POST:
            status = request.POST['shipping_status']
            

            
            if status == 'true':
                # get the order
                order = Order.objects.filter(id=pk)
                # get time
                now = datetime.datetime.now()
                # update the status
                order.update(shipped=True, date_shipped=now)

            else:
                # get order
                order = Order.objects.filter(id=pk)
                # update the status
                order.update(shipped=False)
            messages.success(request, "shipping status updated")
            return redirect('home')
            

        return render(request, 'payment/orders.html', {'order': order, 'items':items})


    else:
        messages.success(request, "Acess denied")
        return redirect('home')

def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)

        if request.POST:
            status = request.POST['shipping_status']
            number = request.POST['number']
            order = Order.objects.filter(id=number)
            order.update(shipped=False)

            messages.success(request, "shipping status updated")
            return redirect('home')
        



        return render(request, 'payment/shipped_dash.html', {'orders': orders})
    else:
        messages.success(request, "Acess denied")
        return redirect('home')

def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False )

        if request.POST:
            status = request.POST['shipping_status']
            number = request.POST['number']
            order = Order.objects.filter(id=number)
            now = datetime.datetime.now()
            order.update(shipped=True, date_shipped=now)

            messages.success(request, "shipping status updated")
            return redirect('home')

        return render(request, 'payment/not_shipped_dash.html', {'orders':orders})
    else:
        messages.success(request, "Acess denied")
        return redirect('home')

def process_orders(request):
    # get the cart
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_totals()

    if request.POST:
        # get billing info from the last page
        payment_form = PaymentForm(request.POST or None)
        # get shipping session data
        my_shipping = request.session.get('my_shipping')
        
        # gather order info
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        amount_paid = totals

        # create shipping address from session info
        shipping_address = f"{my_shipping['shipping_address1']}\n {my_shipping['shipping_address1']}\n {my_shipping['shipping_address2']}\n {my_shipping['shipping_city']}\n {my_shipping['shipping_zipcode']}\n {my_shipping['shipping_state']}\n {my_shipping['shipping_country']}\n"
        
        # create an order
        if request.user.is_authenticated:
            # logged in
            user = request.user
            # create order
            create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

            # get order
            order_id = create_order.pk
            
            # get product id
            for product in cart_products:
                product_id = product.id

                if product.is_sale:
                    price = product.sale_price
                else:
                    price= product.price

                for key, value in quantities.items():
                    if int(key) == product.id:
                        quantity = value
                        #create order item 
                        create_order_item = OrderItem(order_id=order_id, product_id= product_id, user=user, price=price, quantity=quantity)
                        create_order_item.save()

            # delete cart
            for key in list(request.session.keys()):
                if key == 'session_key':
                    # delete key
                    del request.session[key]


            messages.success(request, "Order placed")
            return redirect('home')

        else:
            # not logged in
            # create order
            create_order = Order(user=user, full_name=full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

            # get order
            order_id = create_order.pk
            
            # get product id
            for product in cart_products:
                product_id = product.id

                if product.is_sale:
                    price = product.sale_price
                else:
                    price= product.price

                for key, value in quantities().items():
                    if int(key) == product.id:
                        quantity = value
                        #create order item 
                        create_order_item = OrderItem(order_id=order_id, product_id= product_id, price=price, quantity=quantity)
                        create_order_item.save()
            
            # delete cart
            for key in list(request.session.keys()):
                if key == 'session_key':
                    # delete key
                    del request.session[key]

            

            messages.success(request, "Order placed")
            return redirect('home')
    else:
        messages.success(request, "Access Denied")
        return redirect('home')


def billing_info(request):
    if request.POST:
        # get the cart
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants()
        totals = cart.cart_totals()

        # create a session with shipping info
        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping

        

        # check if user is logged in
        if request.user.is_authenticated:
            # get billing form
            billing_form = PaymentForm()
            return render(request, 'payment/billing_info.html', {"cart_products": cart_products, 'quantities':quantities, 'totals': totals, 'shipping_info': request.POST, 'billing_form': billing_form} )
        else:
             # get billing form
            billing_form = PaymentForm()
            return render(request, 'payment/billing_info.html', {"cart_products": cart_products, 'quantities':quantities, 'totals': totals, 'shipping_info': request.POST, 'billing_form': billing_form} )

        shipping_form = request.POST
        return render(request, 'payment/billing_info.html', {"cart_products": cart_products, 'quantities':quantities, 'totals': totals, 'shipping_info': shipping_form} )
    else:
        messages.success(request, 'Access denied')
        return redirect('home')

def checkout(request):
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants()
    totals = cart.cart_totals()

    if request.user.is_authenticated:
        # checkout as logged in 
        shipping_user = ShippingAddress.objects.get(user__id = request.user.id)
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        return render(request, 'payment/checkout.html', {"cart_products": cart_products, 'quantities':quantities, 'totals': totals, 'shipping_form': shipping_form})
    else:
        # checkout as guest
        shipping_form = ShippingForm(request.POST or None)
        return render(request, 'payment/checkout.html', {"cart_products": cart_products, 'quantities':quantities, 'totals': totals, 'shipping_form': shipping_form})

def payment_success(request):
    return render(request, 'payment/payment_success')