# Stripe test-mode subscriptions

DeepSight activates paid access only after a signature-verified Stripe webhook maps the recurring Stripe Price ID to an active database plan. Reaching the browser success route is not proof of payment.

Configure the backend-only values in `backend/.env`: `STRIPE_ENABLED=true`, an `sk_test_` secret key, `STRIPE_WEBHOOK_SECRET`, and the Basic/Lite monthly and annual `price_...` identifiers. Never commit those values. The database price columns are synchronized from the approved environment mapping; checkout accepts only a plan code and `monthly` or `annual` billing period.

For local webhook delivery:

```powershell
stripe login
stripe listen --forward-to http://127.0.0.1:8000/api/v1/webhooks/stripe
```

Copy the listener's temporary `whsec_...` value into the local backend environment and restart. Use Stripe's test card `4242 4242 4242 4242`, any future expiry, any three-digit CVC, and any postal code. The success page polls the authoritative subscription endpoint for a bounded period. Customer changes and cancellation use Stripe's hosted billing portal.
