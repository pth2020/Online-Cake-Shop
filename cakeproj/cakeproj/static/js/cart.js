document.addEventListener('DOMContentLoaded', function() {
    // Find all "Buy Now" buttons
    const buyNowBtns = document.querySelectorAll('.buy-now');

    // Loop through the buttons and add click event listeners
    buyNowBtns.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();  // Prevent the default form submission behavior
            
            console.log("Update button clicked");  // Debug log to track button click
            const cakeId = this.dataset.cake;
            const action = this.dataset.action;
            const redirectUrl = this.dataset.url;  // URL to redirect after the action is completed

            console.log("Cake ID from button:", cakeId);
            console.log("Action:", action);
            console.log("Redirect URL from button:", redirectUrl);

            // Check if the cakeId and action are valid
            if (!cakeId) {
                console.log("Missing cakeId or action, cannot proceed.");
                return; // Stop execution if cakeId or action is missing
            }

            // Check if the user is authenticated
            if (user === 'AnonymousUser') {
                console.log("User is not authenticated, adding to cart with cookies");
                addCookieItem(cakeId, action, redirectUrl);
            } else {
                console.log("User is authenticated, updating user order");
                updateUserOrder(cakeId, action, redirectUrl);
            }
        });
    });

    const updateQtyBtns = document.querySelectorAll('.qty-btn');
    updateQtyBtns.forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault();                
            
            const cakeId = this.getAttribute('data-cartCake');  // Get the value directly
            const action = this.getAttribute('data-cartAction'); // Get the value directly
            const redirectUrl = "";
            
            if (!action) {
                console.log("Missing cakeId or action for quantity change");
                return;
            }

            if (user === 'AnonymousUser') {
                console.log("User is not authenticated, adding to cart with cookies");
                addCookieItem(cakeId, action, redirectUrl);
            } else {
                console.log("User is authenticated, updating user order");
                
                updateUserOrder(cakeId, action, "");
                
            }
        });

    });

    // Function to create the order for logged-in users
    function updateUserOrder(cakeId, action, redirectUrl) {
        const url = '/update_item/';  // The URL to create the order and birthday cake order

        console.log("Sending request to create order for cake ID:", cakeId);  // Debug log

        // Send a POST request to the server to create the order
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,  // CSRF token for security
            },
            body: JSON.stringify({
                'cakeId': cakeId,
                'action': action,
                
            }),
        })
        .then(response => response.json())
        .then(data => {
            console.log('Order created:', data);
            if (redirectUrl !== "") {
                // Redirect to the build_your_cake page after the order creation
                window.location.href = '/build_your_cake/?cakeId=' + cakeId;  // Redirect to build_your_cake with the cakeId
            } else {
                location.reload();
            }
        });
    }

    // Function to update the cart for non-logged-in users (using cookies)
    function addCookieItem(cakeId, action, redirectUrl) {
        
        if (!cakeId) {
            console.log("Missing cakeId or action for cookie item update");
            return; // Stop if cakeId or action is missing
        }

        if(action == 'add'){            
            if (cart[cakeId] == undefined) {                
                // Initialize with placeholders for non-authenticated users
                cart[cakeId] = { 
                    'quantity': 1, 
                    'size': '',  // Placeholder for size
                    'sponge': '',  // Placeholder for sponge
                    'message': '',  // Placeholder for message
                    'price': '0.0'  // Default price
                };
            }else {
                // If cakeId exists, check if any properties are empty
                let json_cart = JSON.parse(cart)
                if (!( cakeId in json_cart)) {
                    alert(json_cart[cakeId])
                    // Reset size, sponge, and message to their default values
                    cart[cakeId].size = '';
                    cart[cakeId].sponge = '';
                    cart[cakeId].message = '';
                } else {
                    // If all properties are filled, increment the quantity
                    cart[cakeId].quantity += 1;
                    // Perform any other actions, such as updating non-authenticated users
                    update_non_authenticated(cakeId, action);
                }
                
            }   
        }

        if (action == 'remove') {
            // Update the quantity in cart before sending the request
            if (cart[cakeId] && cart[cakeId].quantity > 0) {
                cart[cakeId].quantity -= 1;
            }

            if (cart[cakeId].quantity <= 0) {
                delete cart[cakeId];  // Remove item if quantity is 0 or less
            }

            // Send the updated cart information
            update_non_authenticated(cakeId, action);
        }

        // Update the cart cookie
        console.log('Updated Cart:', cart);
        document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/";

        if (redirectUrl !== "") {
            // Redirect to the build_your_cake page after the order creation
            window.location.href = '/build_your_cake/?cakeId=' + cakeId;  // Redirect to build_your_cake with the cakeId
        } else {
            location.reload();
        }
    }  

    function update_non_authenticated(cakeId, action){
        const url = '/update_item/';
        
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken,  // CSRF token for security
            },
            body: JSON.stringify({
                'cakeId': cakeId,
                'action': action,
                'quantity': cart[cakeId].quantity,
                'size': cart[cakeId].size,
                'sponge': cart[cakeId].sponge,
                'message': cart[cakeId].message,
                'price': cart[cakeId].price,
            }),
        })
        .then(response => response.json())
        .then(data => {
            console.log('Order created:', data);
            location.reload();
        });
    }
});
