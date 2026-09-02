# ARIA Platform - API Keys Setup Guide

This guide walks you through obtaining all required API keys for the ARIA emergency response platform.

## Table of Contents

1. [Required Services](#required-services)
2. [OpenAI (GPT-4, Whisper, Vision)](#openai)
3. [Google Maps API](#google-maps-api)
4. [Twilio SMS](#twilio-sms)
5. [SendGrid Email](#sendgrid-email)
6. [OpenWeatherMap](#openweathermap)
7. [Environment Configuration](#environment-configuration)
8. [Testing Your Setup](#testing-your-setup)

---

## Required Services

The ARIA platform integrates with the following external services:

| Service | Purpose | Required | Cost |
|---------|---------|----------|------|
| **OpenAI** | LLM, Speech-to-Text, Image Analysis | Yes | Paid (usage-based) |
| **Google Maps** | Geocoding, Routing, Places | Yes | Free tier available |
| **Twilio** | SMS Notifications | Optional | Paid (usage-based) |
| **SendGrid** | Email Notifications | Optional | Free tier available |
| **OpenWeatherMap** | Weather Data & Alerts | Optional | Free tier available |

---

## OpenAI

OpenAI provides GPT-4 for natural language understanding, Whisper for speech-to-text, and GPT-4 Vision for image analysis.

### 1. Create an OpenAI Account

- Go to [https://platform.openai.com/signup](https://platform.openai.com/signup)
- Sign up for a new account
- Complete email verification

### 2. Add Payment Method

- Navigate to [Billing Settings](https://platform.openai.com/account/billing/overview)
- Add a credit card
- Set up usage limits to control costs

### 3. Generate API Key

- Go to [API Keys](https://platform.openai.com/api-keys)
- Click "Create new secret key"
- Name it "ARIA Platform"
- Copy the key (starts with `sk-...`)
- **Important:** Save it immediately - you won't see it again

### 4. Configure in ARIA

```bash
# In backend/.env
OPENAI_API_KEY=sk-your-actual-key-here
OPENAI_MODEL=gpt-4-turbo-preview
```

### Cost Estimates

- **GPT-4 Turbo:** ~$0.01 per incident analysis
- **Whisper:** ~$0.006 per minute of audio
- **GPT-4 Vision:** ~$0.01 per image analysis

**Monthly estimate for 1000 incidents:** $15-30

---

## Google Maps API

Google Maps provides geocoding, routing, distance calculations, and places search.

### 1. Create a Google Cloud Account

- Go to [Google Cloud Console](https://console.cloud.google.com/)
- Sign in with your Google account
- Accept terms and create a project

### 2. Create a Project

- Click "Select a project" → "New Project"
- Name: "ARIA Emergency Response"
- Click "Create"

### 3. Enable Required APIs

Navigate to [APIs & Services](https://console.cloud.google.com/apis/library) and enable:

- ✅ **Geocoding API** (address to coordinates)
- ✅ **Directions API** (route calculation)
- ✅ **Distance Matrix API** (travel time estimates)
- ✅ **Places API** (find nearby hospitals)

### 4. Create API Key

- Go to [Credentials](https://console.cloud.google.com/apis/credentials)
- Click "Create Credentials" → "API Key"
- Copy the key (starts with `AIza...`)

### 5. Restrict API Key (Recommended)

- Click on your API key
- Under "Application restrictions":
  - Select "IP addresses"
  - Add your server IP
- Under "API restrictions":
  - Select "Restrict key"
  - Choose the 4 APIs listed above
- Click "Save"

### 6. Configure in ARIA

```bash
# In backend/.env
GOOGLE_MAPS_API_KEY=AIza-your-actual-key-here
```

### Free Tier

- **$200 free credit per month**
- Typically covers 10,000-40,000 API calls
- More than enough for development and small-scale production

---

## Twilio SMS

Twilio enables SMS notifications to ambulance drivers, hospital staff, and reporters.

### 1. Create a Twilio Account

- Go to [https://www.twilio.com/try-twilio](https://www.twilio.com/try-twilio)
- Sign up for a free trial
- Verify your email and phone number

### 2. Get Your Credentials

From the [Twilio Console](https://console.twilio.com/):

- **Account SID:** Found on the dashboard (starts with `AC...`)
- **Auth Token:** Click "View" to reveal (alphanumeric string)

### 3. Get a Phone Number

- Go to [Phone Numbers](https://console.twilio.com/us1/develop/phone-numbers/manage/incoming)
- Click "Buy a number"
- Choose a number with SMS capability
- Complete purchase (free with trial credits)

### 4. Configure in ARIA

```bash
# In backend/.env
TWILIO_ACCOUNT_SID=AC-your-account-sid-here
TWILIO_AUTH_TOKEN=your-auth-token-here
TWILIO_PHONE_NUMBER=+1234567890
```

### Notes

- **Trial account:** Can only send to verified phone numbers
- **Production:** Upgrade account to send to any number
- **Cost:** ~$0.0075 per SMS in the US

---

## SendGrid Email

SendGrid provides reliable email delivery for notifications and reports.

### 1. Create a SendGrid Account

- Go to [https://signup.sendgrid.com/](https://signup.sendgrid.com/)
- Sign up for a free account
- Complete email verification

### 2. Create an API Key

- Go to [API Keys](https://app.sendgrid.com/settings/api_keys)
- Click "Create API Key"
- Name: "ARIA Platform"
- Choose "Full Access"
- Click "Create & View"
- Copy the key (starts with `SG.`)

### 3. Verify Sender Identity

- Go to [Sender Authentication](https://app.sendgrid.com/settings/sender_auth)
- Click "Verify a Single Sender"
- Fill in your details
- Verify your email address

### 4. Configure in ARIA

```bash
# In backend/.env
SENDGRID_API_KEY=SG.your-actual-key-here
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
SENDGRID_FROM_NAME=ARIA Emergency Response
```

### Free Tier

- **100 emails per day** forever free
- Sufficient for development and testing

---

## OpenWeatherMap

OpenWeatherMap provides current weather, forecasts, and severe weather alerts.

### 1. Create an Account

- Go to [https://home.openweathermap.org/users/sign_up](https://home.openweathermap.org/users/sign_up)
- Sign up for a free account
- Verify your email

### 2. Get Your API Key

- Go to [API Keys](https://home.openweathermap.org/api_keys)
- Your default key is already generated
- Copy the key (alphanumeric string)
- **Note:** Keys may take 10-15 minutes to activate

### 3. Configure in ARIA

```bash
# In backend/.env
OPENWEATHER_API_KEY=your-api-key-here
```

### Free Tier

- **60 calls per minute**
- **1,000,000 calls per month**
- More than sufficient for most use cases

---

## Environment Configuration

### Backend Configuration

1. Copy the example file:
```bash
cd backend
cp .env.example .env
```

2. Edit `.env` and add all your API keys:
```bash
nano .env  # or use your preferred editor
```

3. Ensure all keys are properly formatted (no quotes, no spaces)

### Frontend Configuration

1. Copy the example file:
```bash
cd frontend
cp .env.example .env
```

2. Update API URLs if needed (defaults work for local development)

---

## Testing Your Setup

### Quick Test Script

Run the integration test to verify all services:

```bash
# From project root
chmod +x test_integration.sh
./test_integration.sh
```

### Manual Service Tests

#### Test OpenAI

```python
from openai import OpenAI
client = OpenAI(api_key="your-key")
response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[{"role": "user", "content": "Hello"}]
)
print(response.choices[0].message.content)
```

#### Test Google Maps

```bash
curl "https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=YOUR_KEY"
```

#### Test Twilio

```python
from twilio.rest import Client
client = Client("YOUR_SID", "YOUR_TOKEN")
message = client.messages.create(
    body="Test from ARIA",
    from_="+1234567890",
    to="+1987654321"
)
print(message.sid)
```

#### Test SendGrid

```python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

message = Mail(
    from_email='test@example.com',
    to_emails='test@example.com',
    subject='Test',
    html_content='<strong>Test email</strong>')

sg = SendGridAPIClient('YOUR_KEY')
response = sg.send(message)
print(response.status_code)
```

#### Test OpenWeatherMap

```bash
curl "https://api.openweathermap.org/data/2.5/weather?q=London&appid=YOUR_KEY"
```

---

## Cost Management Tips

### OpenAI
- Set usage limits in billing settings
- Use GPT-3.5-turbo for non-critical tasks
- Cache frequent queries
- Implement rate limiting

### Google Maps
- Enable billing alerts
- Set daily quotas per API
- Cache geocoding results
- Use batch requests when possible

### Twilio
- Use email fallback for non-critical notifications
- Implement SMS templates to reduce length
- Group notifications when possible

### General
- Monitor usage dashboards weekly
- Set up billing alerts at 50%, 80%, and 100% of budget
- Review logs for inefficient API calls
- Implement request caching where appropriate

---

## Troubleshooting

### "Invalid API Key" Errors

1. Check for typos in `.env` file
2. Ensure no quotes around keys
3. Verify key is active in provider dashboard
4. Check for trailing spaces
5. Restart backend server after changes

### Google Maps "API Key Not Found"

- API keys can take 5-10 minutes to propagate
- Ensure required APIs are enabled
- Check API key restrictions aren't too strict

### OpenAI "Rate Limit Exceeded"

- You've hit free tier limits
- Add payment method to increase limits
- Implement request queuing and retry logic

### Twilio "Unverified Number"

- With trial accounts, both from and to numbers must be verified
- Upgrade to paid account for unrestricted sending

### SendGrid Emails Not Arriving

- Check spam folder
- Verify sender identity is confirmed
- Check SendGrid activity logs for delivery status

---

## Security Best Practices

1. **Never commit `.env` files** to version control
2. **Rotate keys regularly** (every 90 days recommended)
3. **Use separate keys** for development and production
4. **Implement IP restrictions** where possible
5. **Monitor usage** for unusual patterns
6. **Limit key permissions** to only what's needed
7. **Use environment-specific keys** (dev/staging/prod)
8. **Enable 2FA** on all service accounts

---

## Need Help?

- **ARIA Documentation:** See `INTEGRATION-GUIDE.md`
- **OpenAI Support:** https://help.openai.com/
- **Google Cloud Support:** https://cloud.google.com/support
- **Twilio Support:** https://support.twilio.com/
- **SendGrid Support:** https://support.sendgrid.com/
- **OpenWeatherMap Support:** https://openweathermap.org/faq

---

**Last Updated:** 2024
**ARIA Version:** 1.0.0
