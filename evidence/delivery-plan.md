# Webhook delivery plan

The service sends signed webhook requests. Each request has an HMAC-SHA256
signature header that the receiver can verify with its shared secret.

When delivery fails, the service retries up to three times with exponential
backoff. After the final failure, it records the failure for operator review.

Delivery attempts, outcomes, and error messages are retained in logs for 30
days. The plan does not make claims about legal compliance in any jurisdiction.
