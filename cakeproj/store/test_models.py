# Create your tests here.
import os
import django
import pytest
import math

# Manually set the DJANGO_SETTINGS_MODULE before importing any Django models
os.environ['DJANGO_SETTINGS_MODULE'] = 'cakeproj.settings'
django.setup()

# Now you can import Django models
from store.models import Customer, User, Cake

        
@pytest.mark.django_db
def test_create_customer():
    # First, create a user instance
    user = User.objects.create_user(username='ellenap', password='testpassword')

    # Now create a Customer instance and assign the user instance
    customer = Customer.objects.create(user=user, name='Ellena', email='ellenap@gmail.com')

    # Assert that the customer is created correctly
    assert customer.name == 'Ellena'
    assert customer.email == 'ellenap@gmail.com'
    assert customer.user.username == 'ellenap'  # Check that the user is properly assigned
    assert str(customer)  == 'Ellena'
    
#class Cake(models.Model):
    #name = models.CharField(max_length=200)
    #from_price = models.FloatField()  # Base price for the cake - usually set at small size 
    #description = models.CharField(max_length=500, null=True, blank=True)
    #ingredients = models.CharField(max_length=500, null=True, blank=True)
    #image = models.ImageField(null=True, blank=True)
    
    #def __str__(self):
        #return self.name
    
    
def test_create_cake():
    
    cake = Cake.objects.create(name='Carrot Cake', from_price=30.0, description='Carrot flavour', ingredients='Carrot')
    
    assert cake.name == 'Carrot Cake' 
    assert math.isclose(cake.from_price, 30.0, abs_tol=1e-9)
    assert cake.description == 'Carrot flavour'
    assert cake.ingredients == 'Carrot'

    assert str(cake) == 'Carrot Cake'
        