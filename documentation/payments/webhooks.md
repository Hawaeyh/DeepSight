# Stripe webhooks

`POST /api/v1/webhooks/stripe` verifies `Stripe-Signature`. Event IDs are unique and duplicates are ignored. Verified subscription events update local entitlements; deletion returns an account to Starter, and paid/failed invoices update status and notifications. Keep the webhook secret outside Git.
