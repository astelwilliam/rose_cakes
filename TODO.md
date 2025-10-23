# Rose Cakes Website Re-arrangement Plan

## Information Gathered
- Current website has basic e-commerce functionality with catalog, cart, checkout, user auth
- Images are displayed in catalog cards
- Bootstrap responsive design
- Django admin for basic management
- User wants enhanced homepage with parallax, special offers
- Catalog to be renamed "Menu" with kg-wise pricing and buy now options
- Checkout with delivery restrictions and multiple payment methods
- Enhanced admin capabilities with specific credentials
- Improved search with suggestions
- Shopping cart not displaying added items due to variable mismatches
- Categories need updating to: All Category, Cream Cakes, Plum Cakes, Brownies, Jar Cake, Donuts, etc.

## Plan
### Phase 1: Homepage Enhancements
- [ ] Add parallax scrolling section with cake images
- [ ] Create special offers section for seasonal promotions
- [ ] Enhance hero section with better call-to-actions
- [ ] Add more featured cake images

### Phase 2: Catalog/Menu Re-arrangement
- [x] Rename "Catalog" to "Menu" in templates and navigation
- [x] Add kg-wise pricing options (half kg, 1kg, 2kg, etc.)
- [x] Add "Buy Now" button alongside "Add to Cart"
- [x] Update cake cards with new pricing structure
- [x] Display weight in cart and search pages
- [x] Update category filter to use dynamic categories from database
- [x] Reorganize buttons in catalog for better UX

### Phase 3: Product Details Enhancement
- [x] Add "Buy Now" functionality to cake detail page
- [x] Enhance product display with better image handling

### Phase 4: Checkout Improvements
- [ ] Add delivery pincode restriction (682001 or 5km radius)
- [ ] Implement delivery charge logic (free above ₹1000)
- [ ] Add multiple payment options (UPI, PhonePe, Razorpay)
- [ ] Update checkout form and validation

### Phase 5: Search Enhancements
- [ ] Implement word-by-word search suggestions
- [ ] Improve search results display

### Phase 6: Admin Panel Enhancement
- [ ] Create admin user: username 'astel', password '846343@astel'
- [ ] Add image management capabilities for cakes and offers
- [ ] Enhance admin dashboard with statistics
- [ ] Allow admin to manage special offers

### Phase 7: Database Updates
- [ ] Add weight/portion fields to Cake model
- [ ] Add delivery charge logic
- [ ] Add special offers model
- [ ] Update migrations

### Phase 8: Fix Shopping Cart Display
- [ ] Update cart view to pass correct variables: cart_items, total_items, total_price
- [ ] Update cart.html template to use correct variable names

### Phase 9: Update Categories
- [ ] Add new categories: Cream Cakes, Plum Cakes, Brownies, Jar Cakes, Donuts via Django shell

### Phase 10: Testing and Deployment
- [ ] Test all new features
- [ ] Update responsive design
- [ ] Commit and push changes

## Dependent Files to Edit
- Templates: base.html, homepage.html, catalog.html, cake_detail.html, checkout.html, search.html, cart.html
- Views: views.py (add new functions for buy now, enhanced search, fix cart variables)
- Models: models.py (add weight fields, offers model)
- Admin: admin.py (enhance admin capabilities)
- URLs: urls.py (update routes)
- Settings: settings.py (if needed for new features)
- Static files: Add new images, update CSS for parallax

## Followup Steps
- Install any new dependencies (if needed for parallax)
- Run migrations for new models
- Create admin user
- Add categories via shell
- Test all functionality
- Update documentation
