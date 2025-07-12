import json
from .models import *

def cookieCart(request):
    # Create an empty cart for now for non-logged-in user
    try:
        cart = json.loads(request.COOKIES['cart'])
        print("updated cart...", cart)
                        
    except:
        cart = {}    
    
    items = []
    order = {'get_cart_total': 0, 'get_cart_items': 0}
    cartItems = 0  # order['get_cart_items']

    for i in cart:
        # We use try block to prevent items in cart that may have been removed from causing error
        
        try:
            cartItems += cart[i]['quantity']
            
            cake = BirthdayCake.objects.get(id=i)
            
            total = (cake.price * cart[i]['quantity'])
                                    
            order['get_cart_total'] += total
            order['get_cart_items'] += cart[i]['quantity']
            
            # cart = {8 : {'quantity':1,
            #              'size':'10-inches(approx. 20 -24 serving)',
            #              'sponge':'vanilla',
            #              'message':'Happy Birthday Alex',
            #              'price':50.00
            #             }
            #        }
            
            item = {
                'id': cake.id,
                'name': cake.name,  # Store name here (instead of inside 'cake')
                'description': cake.description,
                'ingredients': cake.ingredients,
                'price': cart[i].get('price'),  # Already storing price at top level
                'imageURL': cake.imageURL,  # Store imageURL here
                'quantity': cart[i]['quantity'],
                'size': cart[i].get('size'),
                'sponge': cart[i].get('sponge'),
                'message': cart[i].get('message'),
                'get_total': total,
            }
                        
            items.append(item)
            
        except:
            pass

    return {'cartItems': cartItems, 'order': order, 'items': items}

def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items  # Get the number of items in the cart
        print("Number of items in cart:", cartItems)

    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']
        
    return {'cartItems': cartItems, 'order': order, 'items': items}
	
def guestOrder(request, data):
    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    # Check if customer already exists, if not, create a new customer
    customer, created = Customer.objects.get_or_create(email=email)
    customer.name = name
    customer.save()

    # Create a new order for the guest customer
    order = Order.objects.create(customer=customer, complete=False)

    # Log to confirm order creation
    print(f"Created order {order.id} for guest customer {customer.name}.")

    # Loop through the items and create order items
    for item in items:
        try:
            cake = BirthdayCake.objects.get(id=item['id'])
            orderItem = OrderItem.objects.create(
                cake=cake,
                order=order,
                quantity=item['quantity'],
                size=item['size'],
                sponge=item['sponge'],
                message=item['message'],
                price=item['price']
            )
            print(f"Created order item for cake: {cake.name} with quantity: {item['quantity']}")
        except Cake.DoesNotExist:
            print(f"Cake with ID {item['id']} not found.")
    
    return customer, order

def send_password_reset_email(user_email, reset_link):
    sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
    from_email = Email(settings.SENDGRID_FROM_EMAIL)
    to_email = To(user_email)
    subject = "Password Reset Request"
    content = Content("text/plain", f"Click the link to reset your password: {reset_link}")

    mail = Mail(from_email, to_email, subject, content)
    
    try:
        response = sg.send(mail)
        return response
    except Exception as e:
        print(f"Error sending email: {e}")
        return None