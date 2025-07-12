import datetime
import traceback
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.db import transaction
from django.contrib.auth.forms import PasswordResetForm
from django.core.mail import send_mail
from .models import *
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
import json
from .utils import cartData, guestOrder
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

from .forms import ContactForm

# import json
# from django.http import JsonResponse
# from .models import Order, OrderItem, Cake

# Create your views here.
def home(request):
    return render(request, 'store/home.html')

def cake_categories(request):        
    return render(request, 'store/cake-categories.html')

def wedding_cakes(request):
    wedding_cakes = WeddingCake.objects.all()
    context = {'wedding_cakes': wedding_cakes}
    return render(request, 'store/cake_decorations/wedding_cakes.html',context)

def birthday_cakes(request):
    birthday_cakes = BirthdayCake.objects.all()
    context = {'birthday_cakes': birthday_cakes}
    return render(request, 'store/cake_decorations/birthday_cakes.html',context)

def cupcakes(request):
    cupcakes = Cupcake.objects.all()
    context = {'cupcakes': cupcakes}
    return render(request, 'store/cake_decorations/cupcakes.html',context)

def party_decorating(request):
    party_decoratings = PartyDecorating.objects.all()
    context = {'party_decoratings': party_decoratings}    
    return render(request, 'store/cake_decorations/party-decorating.html',context)

def store(request):        
    cakes = Cake.objects.all()
    context = {'cakes': cakes}
    return render(request, 'store/store.html',context)

def cake_description(request,pk):
    cake_desc = Cake.objects.get(id=pk)
    
    context = {
        'cake_desc':cake_desc,
    }
    return render(request, 'store/cake_description.html', context)

def gallery(request):
    return render(request, 'store/gallery.html')

def update_cart_with_cookie(cart, cake_id, selected_size, selected_sponge, message, price):
    """Helper function to update cart with default values or increment quantity"""
    # Ensure all necessary fields exist in the cart
    cart[cake_id].setdefault('size', selected_size)
    cart[cake_id].setdefault('sponge', selected_sponge)
    cart[cake_id].setdefault('message', message)
    cart[cake_id].setdefault('quantity', 0)
    cart[cake_id].setdefault('price', str(price))

    # Increment quantity if size, sponge, and message are set
    if (cart[cake_id]['size'] != '' and cart[cake_id]['sponge'] and cart[cake_id]['message']):
        cart[cake_id]['quantity'] += 1  # Increment quantity
    else:
        # If not set, keep the initial values (size, sponge, message)
        cart[cake_id]['size'] = selected_size
        cart[cake_id]['sponge'] = selected_sponge
        cart[cake_id]['message'] = message
        cart[cake_id]['quantity'] = 1
        cart[cake_id]['price'] = str(price)
        
    return cart


def update_cart_cookie(cart, response, max_age=3600):
    """Helper function to update the cart cookie"""
    response.set_cookie('cart', json.dumps(cart), max_age=max_age)  # Set the cart cookie for 1 hour
    return response


def handle_non_authenticated_user(cart, cake_id, selected_size, selected_sponge, message, price):
    """Helper function to handle cart update for non-authenticated users"""
    # If the cake_id doesn't exist in the cart, add it with default values
    if cake_id in cart:
        cart = update_cart_with_cookie(cart, cake_id, selected_size, selected_sponge, message, price)
        print("Cart updated?", cart)
    else:
        print("cake_id not in cart:",cake_id, selected_size, selected_sponge, message, price)
        cart[cake_id] = {
            'quantity': 1,
            'size': selected_size,
            'sponge': selected_sponge,
            'message': message,
            'price': str(price),
        }
    return cart


def build_your_cake(request):
    if request.method == 'POST':
        selected_size = request.POST.get('size')
        selected_sponge = request.POST.get('sponge')
        message = request.POST.get('message', "")
        quantity = request.POST.get('quantity')
        cake_id = request.POST.get('cake_id')
        
    
        try:
            cake = BirthdayCake.objects.get(id=cake_id)
        except BirthdayCake.DoesNotExist:
            return redirect('error_page')

        price = cake.price

        if not request.user.is_authenticated:
            # Non-authenticated user flow
            try:
                cart = json.loads(request.COOKIES.get('cart', '{}'))
                print(selected_size,selected_sponge,message,quantity,cake_id)
                cart = handle_non_authenticated_user(cart, cake_id, selected_size, selected_sponge, message, price)
                response = redirect('cart')
                return update_cart_cookie(cart, response)

            except json.JSONDecodeError:
                # Handle malformed or missing cart cookie
                cart = {cake_id: {'quantity': 1, 'size': selected_size, 'sponge': selected_sponge, 'message': message, 'price': str(price)}}
                response = redirect('cart')
                return update_cart_cookie(cart, response)

        else:
            # Authenticated user flow
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False, transaction_id=None)

            # Get or create the order item
            order_item, created = OrderItem.objects.get_or_create(order=order, cake=cake)
            order_item.size = selected_size
            order_item.sponge = selected_sponge
            order_item.message = message
            order_item.quantity = quantity
            order_item.price = float(price)

            order_item.save()

            return redirect('cart')

    # Handle GET request for displaying cake details
    cake_id = request.GET.get('cakeId')
    try:
        cake = BirthdayCake.objects.get(id=cake_id)
    except BirthdayCake.DoesNotExist:
        return redirect('error_page')

    return render(request, 'store/build_your_cake.html', {'cake': cake})

def wedding_cake_enquiry(request):
    cake_id = request.GET.get('cake_id')  # Get the 'cake_id' from the query parameters
    
    if cake_id:
        try:
            cake = WeddingCake.objects.get(id=cake_id)  # Retrieve the cake by ID
        
            if request.user.is_authenticated:
                authenticated = True
            else: 
                authenticated = False
                
        except Cake.DoesNotExist:
            return HttpResponseNotFound("Cake not found")
            
        # Now you have the `cake` object and can pass it to the template
        return render(request, 'store/wedding_cake_enquiry.html', {'cake': cake, 'authenticated': authenticated})
    else:
        return HttpResponse("Invalid cake_id", status=400)
            

#@login_required(login_url="/signin/")
def wedding_cake_booking(request):
    if request.method == 'POST':
        cake_id = request.POST.get('cake_id')
        date = request.POST.get('date')
        phone = request.POST.get('phone')
        house_number = request.POST.get('house-number')
        building_name = request.POST.get('building-name')
        street = request.POST.get('street')
        postcode = request.POST.get('postcode')
        message = request.POST.get('message')
        
        #For authenticated users
        if request.user.is_authenticated:
            customer = request.user.customer  # Use the existing customer linked to the user
        else:
            # Handle non-authenticated users (create new user and customer)
            name = request.POST.get('name')
            email = request.POST.get('email')
            password = request.POST.get('password')
            
            # Validation: Check if user with the same email already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, "A user with this email already exists.")
                return redirect('wedding_cake_booking')  # Stay on the current page

            try:
                # Create the user and customer object
                user = User.objects.create_user(username=email, email=email, password=password)
                customer = Customer.objects.create(user=user, name=name, email=email)
                
                login(request, user)  # Automatically log the user in after creation

            except Exception as e:
                messages.error(request, f"Error creating user: {str(e)}")
                return redirect('wedding_cake_booking')

        # Fetch the selected wedding cake based on the cake_id
        try:
            wedding_cake = WeddingCake.objects.get(id=cake_id)
        except WeddingCake.DoesNotExist:
            return HttpResponse("Wedding cake not found", status=404)

        # Convert date to a datetime object (if needed)
        try:
            date_wanted = datetime.datetime.strptime(date, "%Y-%m-%d")  # Change the format as per your date input format
        except ValueError:
            return HttpResponse("Invalid date format", status=400)

        # Create a WeddingCakeBooking entry associated with the selected wedding cake
        transaction_id = datetime.datetime.now().timestamp()
        
        #delivery address
        delivery = DeliveryAddress.objects.create(customer=customer,house_number=house_number, building_name=building_name,street=street, postcode=postcode  )

        WeddingCakeBooking.objects.create(
            wedding_cake=wedding_cake,
            customer=customer, 
            delivery_address = delivery,
            transaction_id=transaction_id,  
            phone_number=phone,                       
            date_wanted=date_wanted,                      
            message=message,
            complete=False
        )

        # Redirect to a thank-you page after successful form submission
        return redirect('thank_you')  # Ensure this URL exists in your `urls.py`

    return render(request, 'store/cake-categories.html')  # Render the form again if the request is not POST

def cart(request):
    data = cartData(request)
    
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
                
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'store/cart.html', context)

def checkout(request):
    data = cartData(request)
    
    cart_items = data['cartItems']
    order = data['order']
    items = data['items']
            
    context = {'items':items, 'order': order, 'cartItems':cart_items}
    return render(request, 'store/checkout.html', context)

def accessories(request):
    return render(request, 'store/accessories.html')

def update_item(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        cake_id = data.get('cakeId')
        action = data.get('action')

        # Check if cakeId and action are provided in the data
        if not cake_id or not action:
            return JsonResponse({"error": "Missing cakeId or action"}, status=400)

        # Handle authenticated user flow
        if request.user.is_authenticated:
            customer = request.user.customer
            cake = Cake.objects.filter(id=cake_id).first()  # Use filter().first() instead of get()
            if not cake:
                return JsonResponse({"error": "Cake not found"}, status=404)

            # Get or create the order for the customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False, transaction_id=None)
            order_item, created = OrderItem.objects.get_or_create(order=order, cake=cake)

            # Update quantity based on action
            if created:
                order_item.quantity = 1
            else:
                if action == 'add':
                    order_item.quantity += 1
                elif action == 'remove':
                    order_item.quantity -= 1

            # Handle quantity less than or equal to 0
            if order_item.quantity <= 0:
                order_item.delete()
            else:
                order_item.save()

            return JsonResponse({"message": "Item updated successfully", "quantity": order_item.quantity}, status=200)

        # Handle non-authenticated user flow using cookies
        else:
            cart = json.loads(request.COOKIES.get('cart', '{}'))  # Default to empty cart if no cookie

            # Ensure cake_id is in the cart and initialize with default quantity 0
            if cake_id not in cart:
                cart[cake_id] = {'quantity': 0}

            # Update cart based on action
            if action == 'add':
                cart[cake_id]['quantity'] += 1
            elif action == 'remove':
                cart[cake_id]['quantity'] -= 1

            # Remove cake if quantity is less than or equal to 0
            if cart[cake_id]['quantity'] <= 0:
                del cart[cake_id]

            response = JsonResponse({'message': 'Cart updated successfully'})
            # Update cart cookie with the modified cart data
            response.set_cookie('cart', json.dumps(cart), max_age=60*60*24*30)  # Store for 30 days

            return response
        

def process_order(request):
    try:
        transaction_id = datetime.datetime.now().timestamp()
        data = json.loads(request.body)

        if request.user.is_authenticated:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
        else:
            customer, order = guestOrder(request, data)

        total = float(data['form']['total'])
        deliver = data['form']['deliverorder']
        order.deliver = deliver
        order.transaction_id = transaction_id

        #if total == order.get_cart_total():
        if total == float(order.get_cart_total):    
            order.complete = True

        order.save()

        if deliver == 'True':
            DeliveryAddress.objects.create(
                customer=customer,
                order=order,
                address=data['deliveryInfo']['address'],
                city=data['deliveryInfo']['city'],
                postcode=data['deliveryInfo']['postcode'],
            )

        response = JsonResponse('Payment submitted..', safe=False)
        if not request.user.is_authenticated:
            response.delete_cookie('cart', path='/')
            if 'cart' in request.session:
                del request.session['cart']
        return response

    except Exception as e:
        print(traceback.format_exc())  # log error to server console
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt  # Make sure CSRF exemption is removed when you have CSRF token protection
def update_transaction_view(request):
    if request.method == 'POST':
        try:
            # Load data from the request
            data = json.loads(request.body)
            order_id = data.get('orderId')  # Get orderId from the request body

            if not order_id:
                return JsonResponse({'error': 'No order ID provided'}, status=400)

            # Try to retrieve the order from the database
            order = Order.objects.get(id=order_id)
            order.status = 'Ready for collection'  # Update the status
            order.save()  # Save the updated order

            return JsonResponse({'status': 'success'}, status=200)  # Return success response

        except Order.DoesNotExist:
            return JsonResponse({'error': 'Order not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

def error_page(request):
    return render(request, 'store/error_page.html')
    
def signin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Authenticate the user with the provided username and password
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # If the user is authenticated, log them in
            login(request, user)
            # Redirect based on user privileges (admin or regular user)
            if user.is_superuser:  
                login(request,user)
                return redirect('secure-admin-area')              
            else:
                login(request,user)
                return redirect('store')  # Redirect to the store page for regular users           
            
        else:
            # If authentication fails (incorrect username or password), show an error
            messages.error(request, 'Incorrect username or password. Try again.')
            return redirect('signin')  # Redirect back to the signin page

    # If the request method is GET, render the signin page
    return render(request, 'store/signin.html')  # Render the login page template


def signout(request):
    logout(request)
    return redirect('home')

    
#users can sign up by themselves by providing their details
def signup(request):
    
    if request.method == 'POST':
        
        name = request.POST.get('fullname')
        email = request.POST.get('email')
        username = request.POST.get('username')          
        password = request.POST.get('password')   
        
        #Create the User instance
        user = User.objects.create_user(
            username = username,
            email = email,
            password = password
        )
        
        #Create the user instance linked to the User
        customer = Customer(
            user = user,
            name = name,
            email = email            
        )
        
        customer.save()
        
        #converts user password into a hash algorithm for security reasons
        #Random example -  password=johnsmith2  
        # (hash - pbkdf2_sha256$789047$qtS4Yssquerr7ncufMyH3z$SheYWFjnsU3vrOYsWy5nsPfIoFUeGY4/6U=)
        #customer.set_password(customer.password)
        
        return render(request,'store/signin.html')   
                
    else: 
        return HttpResponse("Invalid request method!")
    
def testimonials(request):
    return render(request, 'store/testimonials.html')

def contact(request):
    return render(request, 'store/contact.html')

def search_view(request):
    query = request.GET.get('query', '')  # Capture search query from the URL
    cakes = []
    
    data = cartData(request)    
    cartItems = data['cartItems']

    if query:
        # Filter products by name (case-insensitive match)
        cakes = Cake.objects.filter(name__icontains=query)  # Filtering by name (case insensitive)

    return render(request, 'store/search_results.html', {'cakes': cakes, 'cartItems': cartItems})

def password_reset_request(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            # This checks if the email exists and sends a password reset email
            form.save(request=request)
            return redirect('password_reset_done')  # Redirect to a success page after email is sent
    else:
        form = PasswordResetForm()
    
    return render(request, "store/password_reset_form.html", {"form": form})

# Helper function to send reset email
def send_password_reset_email(to_email, reset_link):
    subject = "Password Reset Request"
    message = f"Click the following link to reset your password: {reset_link}"
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [to_email])
    
def password_reset_done(request):
    return render(request, 'password_reset_done.html')

def contact_view(request):
    submitted = False
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('thank_you')  # Redirect to success page
    else:
        form = ContactForm()

    return render(request, 'store/contact.html', {'form': form})

def thank_you(request):
    name = request.session.get('name')  # Store name in session or pass as context
    return render(request, 'store/thank_you.html', {'name': name})

def secure_admin_area(request):
    order_items = OrderItem.objects.filter(order__transaction_id__isnull=False).exclude(order__transaction_id="")
    
    wedding_cake_booking = WeddingCakeBooking.objects.all()
    
    birthday_cakes = BirthdayCake.objects.all()
        
    paginator_items = Paginator(order_items, 10)  # Show 10 orders per page
    paginator_wedding = Paginator(wedding_cake_booking, 10)  # Show 10 orders per page
    
    page_number = request.GET.get('page')
    
    page_obj_item = paginator_items.get_page(page_number)
    page_obj_wedding = paginator_wedding.get_page(page_number)

    return render(request, 'store/secure-admin-area.html', {'page_obj_item': page_obj_item,'birthday_cakes':birthday_cakes,'page_obj_wedding': page_obj_wedding })



    

