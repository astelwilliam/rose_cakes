## Checkout Page Changes: Delivery to Pickup

### Phase 1: Model Updates
- [ ] Update Order model: remove customer_address, add pickup_date = models.DateField()
- [ ] Run makemigrations and migrate

### Phase 2: View Updates
- [ ] Update checkout view: remove customer_address, customer_pincode, add pickup_date, change phone to whatsapp_number, remove delivery charge logic, remove pincode validation

### Phase 3: Template Updates
- [ ] Update checkout.html: remove address, pincode, delivery charge from summary, change phone label to WhatsApp, add pickup_date field, rename section to "Pickup Information", update secure checkout text to mention pickup

### Phase 4: Testing
- [ ] Test the checkout process with new fields
- [ ] Verify order creation and confirmation
