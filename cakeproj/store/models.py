from django.db import models
from django.contrib.auth.models import User
# Create your models here.
    
class Customer(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, null=True)
    email = models.CharField(max_length=200)
    
    def __str__(self):
        return self.name   
        
# Base Cake class
class Cake(models.Model):
    name = models.CharField(max_length=200)
    from_price = models.DecimalField(max_digits=10, decimal_places=2)  # Base price for the cake - usually set at small size 
    description = models.CharField(max_length=500, null=True, blank=True)
    ingredients = models.CharField(max_length=500, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)
    
    def __str__(self):
        return self.name
    
    @property
    def imageURL(self):
        try:
            url = self.image.url
        except AttributeError:
            url = ''
        return url

# BirthdayCake class inherits from Cake
class BirthdayCake(Cake):
    # Define choices for sponge type
    SPONGE_CHOICES = [
        ('vanilla', 'Vanilla'),
        ('chocolate', 'Chocolate'),
        ('red_velvet', 'Red Velvet'),
        ('carrot', 'Carrot'),
    ]

    SIZE_CHOICES = [
        ('6-inches', 'Small'),
        ('8-inches', 'Medium'),
        ('10-inches', 'Large'),
    ]
    
    size = models.CharField(
        max_length=20,
        choices=SIZE_CHOICES,
        default='8-inches',  # Default size is medium
    )
    
    sponge = models.CharField(
        max_length=20,
        choices=SPONGE_CHOICES,
        default='vanilla',  # Default sponge type
    )

    small_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)  # Price for small (6-inches)
    medium_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)  # Price for medium (8-inches)
    large_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)  # Price for large (10-inches)

    def save(self, *args, **kwargs):
        # Dynamically set the from_price based on the manually entered small price
        if not self.from_price:
            self.from_price = self.small_price  # Default the from_price to the small price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Birthday Cake: {self.name} ({self.get_size_display()} - {self.get_sponge_display()})"

    @property
    def price(self):
        # Map the size to the corresponding price, using 'in' to match sizes with additional info
        if '6-inches' in self.size:
            return self.small_price  # Price for Small
        elif '8-inches' in self.size:
            return self.medium_price  # Price for Medium
        elif '10-inches' in self.size:
            return self.large_price  # Price for Large
        return self.from_price  # Default to from_price if no match
    
# WeddingCake is a subclass of Cake
class WeddingCake(Cake):
    tiers = models.IntegerField()  # Example field for wedding cakes
    decoration_style = models.CharField(max_length=100)
    
    def __str__(self):
        return f"Wedding Cake: {self.name}"
    
# Cupcake is a subclass of Cake
class Cupcake(Cake):  # Inherits from Cake
    flavor = models.CharField(max_length=100)  # Flavor of the cupcake (e.g., vanilla, chocolate)
    decoration_style = models.CharField(max_length=100)  # Decoration style (e.g., frosting, sprinkles)
    price = models.DecimalField(max_digits=5, decimal_places=2)  # Price per cupcake
    special_request = models.TextField(blank=True, null=True)  # Any special requests or customizations (optional)

    def __str__(self):
        return f"{self.flavor} Cupcake"
    
class PartyDecorating(models.Model):
    name = models.CharField(max_length=200)  # Name of the decoration item (e.g., Balloons, Banners)
    decoration_type = models.CharField(max_length=100, choices=[('balloon', 'Balloon'), ('banner', 'Banner'), ('table_setting', 'Table Setting'), ('lighting', 'Lighting'), ('other', 'Other')])  # Type of decoration
    description = models.CharField(max_length=500, null=True, blank=True)  # Description of the decoration
    theme = models.CharField(max_length=100, null=True, blank=True)  # The theme it suits (e.g., Birthday, Wedding, Christmas)
    color = models.CharField(max_length=100, null=True, blank=True)  # Color of the decoration (e.g., Red, Blue, Gold)
    quantity = models.IntegerField()  # Quantity of decorations available
    price = models.DecimalField(max_digits=6, decimal_places=2)  # Price per decoration item or set
    image = models.ImageField(null=True, blank=True)  # Optional image of the decoration
    special_instructions = models.TextField(null=True, blank=True)  # Special instructions or requests

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except AttributeError:
            url = ''
        return url

# class DeliveryAddress(models.Model):
#     customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
#     #order = models.OneToOneField(Order, on_delete=models.SET_NULL, null=True)
#     house_number = models.CharField(max_length=200, null=False)  # house_number field
#     building_name = models.CharField(max_length=200, null=False)
#     street = models.CharField(max_length=200, null=False)    
#     postcode = models.CharField(max_length=200, null=False)
    
#     def __str__(self):
#         return self.postcode
    
    
# class Order(models.Model):
#     customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
#     delivery_address = models.ForeignKey(DeliveryAddress, null=True, on_delete=models.CASCADE)
#     date_ordered = models.DateField(auto_now_add=True, db_index=True)  # Adding an index
#     complete = models.BooleanField(default=False)
#     deliver = models.BooleanField(default=False)
#     transaction_id = models.CharField(max_length=100, null=True, blank=True, unique=True)
#     status = models.CharField(max_length=100, default='Paid')
    
#     def __str__(self):
#         return str(self.id)
    
    
#     @property
#     def get_cart_total(self):
#         orderitems = self.orderitem_set.all()
#         total = sum([item.get_total for item in orderitems])
#         return total
    
class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateField(auto_now_add=True, db_index=True)  # Adding an index
    complete = models.BooleanField(default=False)
    deliver = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True, blank=True, unique=True)
    status = models.CharField(max_length=100, default='Paid')
    
    def __str__(self):
        return str(self.id)
    
    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total
    
    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total
    
    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total
        
class OrderItem(models.Model):
    cake = models.ForeignKey(Cake, on_delete=models.SET_NULL, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.IntegerField(default=1, null=True, blank=True)
    date_added = models.DateField(auto_now_add=True)
    
    # Fields for size and sponge type
    size = models.CharField(max_length=40, blank=True, null=True)  # For BirthdayCake size
    sponge = models.CharField(max_length=20, blank=True, null=True)  # For BirthdayCake sponge type
    message = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)  # Added price field
    
    @property
    def get_total(self):
        # Ensure dynamic price calculation
        return self.price * self.quantity

    class Meta:
        unique_together = ('order', 'cake', 'size', 'sponge', 'message')  # To prevent duplicate cakes in the same order


class DeliveryAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True)
    #order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    order = models.OneToOneField(Order, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=200, null=False)
    city = models.CharField(max_length=200, null=False)
    postcode = models.CharField(max_length=200, null=False)
    
    def __str__(self):
        return self.address

#In this case, the related_name="wedding_cake_enquiry" in the order field means that 
# the reverse relationship from Order to WeddingCakeOrder will be accessed via 
# wedding_cake_orders instead of the default name, which avoids the clash.
class WeddingCakeBooking(models.Model):
    wedding_cake = models.ForeignKey(WeddingCake, null=False, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, null=True, on_delete=models.CASCADE)
    delivery_address = models.ForeignKey(DeliveryAddress, null=True, on_delete=models.CASCADE)
    date_added = models.DateField(auto_now_add=True)
    transaction_id = models.CharField(max_length=100, null=True, blank=True, unique=True)
    phone_number = models.CharField(max_length=20, null=False)   
    date_wanted = models.DateField()
    message = models.CharField(max_length=500, null=True)
    complete = models.BooleanField(default=False)
    
    
class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return self.name
    
