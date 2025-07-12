from django.test import TestCase
from django.urls import reverse
from .models import *
from django.core.files.uploadedfile import SimpleUploadedFile

class CakeCategoriesViewTest(TestCase):
    
    def test_cake_categories_view_status_code(self):
        # Use reverse() to get the URL for the view, 
        # it will dynamically resolve to the correct URL.
        
        # Use the correct URL name if you have a named URL.
        url = reverse('cake_categories') 

        # Send a GET request to the view.
        response = self.client.get(url)
        
        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
        
    def test_cake_categories_view_template(self):
        url = reverse('cake_categories')  # Again, use the correct URL name.
        
        # Send a GET request to the view.
        response = self.client.get(url)
        
        # Ensure the correct template is used.
        self.assertTemplateUsed(response, 'store/cake-categories.html')
        
class CakeDescriptionViewTest(TestCase):
    
    def setUp(self):
        # Create a mock image file to associate with the Cake instance
        image = SimpleUploadedFile(
            name="test_image.jpg",
            content=b"file_content",  # Binary content of the file
            content_type="image/jpeg"  # Specify the content type (MIME type)
        )

        # Create a Cake instance with the image and from_price
        self.cake = Cake.objects.create(
            name="Chocolate Cake",
            description="A delicious chocolate cake",
            from_price=15.99,
            image=image  # Associating the image
        )
    
    def test_cake_description_view_status_code(self):
        # path('cake_description/<int:pk>/', views.cake_description, name='cake_description'),
        # Generate the URL with a valid pk value from the Cake instance
        url = reverse('cake_description', kwargs={'pk': self.cake.pk})  # Pass pk as part of the URL
        
        response = self.client.get(url)
        
        # Check if the response status code is 200 (OK)
        self.assertEqual(response.status_code, 200)
        
    def test_cake_description_view_template(self):
        # Generate the URL with a valid pk value
        url = reverse('cake_description', kwargs={'pk': self.cake.pk})  # Pass pk as part of the URL
        
        response = self.client.get(url)
        
        # Ensure the correct template is used.
        self.assertTemplateUsed(response, 'store/cake_description.html')
