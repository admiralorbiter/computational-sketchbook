# Oura OAuth Integration Setup Guide

## Prerequisites

1. **Oura Developer Account**: Sign up at [Oura Cloud](https://cloud.ouraring.com/)
2. **Python Dependencies**: Install required packages from `requirements.txt`

## Configuration Steps

### 1. Create Oura Application

1. Go to [Oura Cloud → My Applications](https://cloud.ouraring.com/oauth/applications)
2. Click **"Create app"**
3. Fill in the application details:
   - **Contact Email**: Your email address
   - **Website**: `http://127.0.0.1:5000` (for local development)
   - **Privacy Policy URL**: `http://127.0.0.1:5000/privacy`
   - **Terms of Service URL**: `http://127.0.0.1:5000/terms`
   - **Redirect URIs**: `http://127.0.0.1:5000/callback`
4. **Authentication Options**: Check both:
   - ✅ Allow server-side authentication (grant-type code)
   - ✅ Allow client-side authentication (grant-type token)
5. **Agree to Oura API Agreement**: ✅ Check this box
6. Click **"Save"**

### 2. Environment Configuration

Create a `.env` file in your project root with:

```bash
# BonziBuddy Configuration
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///var/bonzibuddy.db

# Oura OAuth Configuration
OURA_CLIENT_ID=your-oura-client-id-from-step-1
OURA_CLIENT_SECRET=your-oura-client-secret-from-step-1
OURA_REDIRECT_URI=http://127.0.0.1:5000/callback
OURA_SCOPE=daily email personal
```

### 3. Database Migration

Apply the new migration to create Oura tables:

```bash
python scripts/db_apply.py migrations/0012_oura_oauth.sql
```

### 4. Start the Application

```bash
python app.py
```

## Usage

### Connecting Oura Ring

1. Go to your health dashboard
2. In the "Oura Ring" card, click **"Connect"**
3. You'll be redirected to Oura's authorization page
4. Authorize the application
5. You'll be redirected back to your dashboard

### Available Data

Once connected, you can access:
- **Sleep Data**: `/health/oura/sleep`
- **Activity Data**: `/health/oura/activity`
- **Readiness Data**: `/health/oura/readiness`

### API Endpoints

- `GET /health/oura/connect` - Start OAuth flow
- `GET /health/oura/callback` - OAuth callback handler
- `GET /health/oura/status` - Connection status
- `GET /health/oura/sleep` - Sleep data
- `GET /health/oura/activity` - Activity data
- `GET /health/oura/readiness` - Readiness data
- `GET /health/oura/disconnect` - Disconnect account

## Troubleshooting

### Common Issues

1. **"Oura OAuth not initialized"**
   - Check that your `.env` file has all required Oura variables
   - Ensure the app was restarted after adding environment variables

2. **"Invalid redirect URI"**
   - Verify the redirect URI in your Oura app matches exactly
   - Check for trailing slashes or protocol mismatches

3. **"Client ID not found"**
   - Double-check your `OURA_CLIENT_ID` in the `.env` file
   - Ensure the Oura application was created successfully

4. **Database errors**
   - Run the migration: `python scripts/db_apply.py migrations/0012_oura_oauth.sql`
   - Check that the database file is writable

### Security Notes

- Never commit your `.env` file to version control
- Keep your Oura client secret secure
- Use HTTPS in production
- Regularly rotate your Oura client credentials

## Production Deployment

For production use:

1. Update redirect URIs to use your production domain
2. Use HTTPS for all URLs
3. Set appropriate scopes for your use case
4. Implement proper session management
5. Add rate limiting for API calls
6. Set up monitoring and logging

## Support

If you encounter issues:
1. Check the application logs
2. Verify your Oura app configuration
3. Test with the Oura API directly using your credentials
4. Check the Oura API documentation for endpoint changes
