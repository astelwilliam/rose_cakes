# WhatsApp Cloud API Setup Guide

## ⚠️ Account Age Restriction
**Your Facebook account is too new to create a business account. Try again in an hour.**

## Alternative Solutions for WhatsApp Notifications

### Option 1: Use WhatsApp Business App (Free)
Instead of Cloud API, you can use the WhatsApp Business App for manual notifications:

1. Download WhatsApp Business App on your phone
2. Use the same business number
3. Manually send status updates to customers
4. The system can still log notifications for tracking

### Option 2: Third-Party WhatsApp Services
Use services like:
- **Twilio** - Paid WhatsApp API service
- **360Dialog** - WhatsApp Business API provider
- **MessageBird** - WhatsApp integration service

### Option 3: Wait and Use Meta's Free Tier
- Wait for your Facebook account to age (usually 24-48 hours)
- Then follow the original setup guide
- Meta provides 1,000 free messages per month

## Current Status
✅ **Email notifications are working** - Customers will receive email updates immediately
⏳ **WhatsApp notifications** - Ready to activate once account age restriction is lifted

## Testing Email Notifications
You can test email notifications right now:
1. Go to Django admin → Orders
2. Change an order status
3. Check the customer's email for notifications

## For Production
Consider these WhatsApp alternatives:
- **Twilio**: $0.005/message, reliable delivery
- **360Dialog**: Direct Meta partnership, good rates
- **WhatsApp Business API**: Free tier available after account verification

The email system provides immediate notification capability while you resolve the WhatsApp setup.

---

## Original Setup Guide (For When Account Ages)

## Step 1: Create a Meta Developer Account
1. Go to [Meta for Developers](https://developers.facebook.com/)
2. Click "Get Started" and create a developer account
3. Verify your account with a phone number

## Step 2: Create a Business App
1. Go to [Meta App Dashboard](https://developers.facebook.com/apps/)
2. Click "Create App"
3. Select "Business" as the app type
4. Choose "WhatsApp" as the business account

## Step 3: Configure WhatsApp Business Account
1. In your app dashboard, go to "WhatsApp" → "Getting Started"
2. Create or connect a WhatsApp Business Account
3. Add your phone number (this will be your business number)
4. Verify the phone number with the code sent to WhatsApp

## Step 4: Get API Credentials
1. In the WhatsApp section, go to "API Setup"
2. Copy the following values:
   - **Access Token** (Temporary token for testing)
   - **Phone Number ID** (Unique ID for your phone number)

## Step 5: Configure Django Settings
Update your `cake_store/settings.py` file:

```python
# WhatsApp Cloud API Settings
WHATSAPP_TOKEN = 'EAAXXXXXXX...'  # Replace with your actual access token
WHATSAPP_PHONE_ID = '123456789012345'  # Replace with your phone number ID
```

## Step 6: Test the Integration
1. Create a test order in your Django admin
2. Change the order status using admin actions
3. Check if WhatsApp messages are sent to customer numbers

## Important Notes:
- **Temporary Access Token**: The token from Step 4 expires. For production, generate a permanent token from the Business Manager.
- **Phone Number Format**: Customer WhatsApp numbers should be in E.164 format (e.g., +1234567890)
- **Rate Limits**: WhatsApp has rate limits - monitor usage in production
- **Business Verification**: For production use, your business needs to be verified by Meta

## Troubleshooting:
- Ensure the access token is valid and not expired
- Check that customer phone numbers are in correct format
- Verify the Phone Number ID matches your configured number
- Check Meta's status page for any API outages

## Production Setup:
1. Generate a permanent access token from Business Manager
2. Set up webhooks for message delivery status (optional)
3. Configure proper error handling and logging
4. Monitor API usage and costs
