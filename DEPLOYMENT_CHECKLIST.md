# Pre-Deployment Checklist

## Environment Variables (Required)
- [ ] `SESSION_SECRET` - Session security key
- [ ] `DATABASE_URL` - PostgreSQL connection (auto-provided in Replit)
- [ ] `OPENAI_API_KEY` - For AI sentiment analysis

## Email Integration (Recommended)
- [ ] `GMAIL_EMAIL` - Sender email address
- [ ] `GMAIL_APP_PASSWORD` - Gmail app password (not regular password)

## Optional Integrations
- [ ] Twilio SMS: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`
- [ ] WhatsApp: `WHATSAPP_API_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID`
- [ ] Claude AI: `ANTHROPIC_API_KEY`
- [ ] JAIS Arabic AI: `JAIS_API_KEY`

## Testing Checklist
- [ ] Visit `/integrations` page
- [ ] Test Gmail SMTP connection (should show "successful")
- [ ] Create a test survey at `/surveys`
- [ ] Verify Arabic text renders correctly (RTL)
- [ ] Check analytics dashboard at `/analytics`
- [ ] Test feedback widget functionality

## Performance Verification
- [ ] Application starts within 30 seconds
- [ ] Database connection established
- [ ] All API blueprints register successfully
- [ ] No critical errors in console logs

## Security Check
- [ ] All secrets properly configured (not hardcoded)
- [ ] Database queries use parameterized statements
- [ ] OAuth authentication working
- [ ] HTTPS enabled in production

## Documentation Update
- [ ] Update `replit.md` with any environment-specific notes
- [ ] Verify all links in documentation work
- [ ] Update contact information if changed

## Ready for Production ✅
Once all items are checked, the platform is ready for live deployment.