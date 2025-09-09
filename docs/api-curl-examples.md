# FX Payment Processor API - cURL Examples

This document provides comprehensive cURL examples for all API endpoints in the FX Payment Processor.

## Base URL
```bash
BASE_URL="http://localhost:5001"
```

## API Endpoints Overview

### 1. Get API Information
Get basic information about the API and available endpoints.

```bash
curl -X GET "${BASE_URL}/" \
  -H "Content-Type: application/json" \
  | jq '.'
```

**Expected Response:**
```json
{
  "message": "FX Payment Processor API",
  "version": "1.0.0",
  "endpoints": {
    "fund": "POST /wallets/<user_id>/fund",
    "convert": "POST /wallets/<user_id>/convert",
    "withdraw": "POST /wallets/<user_id>/withdraw",
    "balances": "GET /wallets/<user_id>/balances",
    "transactions": "GET /wallets/<user_id>/transactions",
    "reconcile": "GET /wallets/<user_id>/reconcile",
    "fx_rates": "GET /fx/rates"
  }
}
```

## Wallet Operations

### 2. Fund Wallet
Add money to a user's wallet in a specific currency.

**Fund USD Wallet:**
```bash
curl -X POST "${BASE_URL}/wallets/user123/fund" \
  -H "Content-Type: application/json" \
  -d '{
    "currency": "USD",
    "amount": 1500.75
  }' \
  | jq '.'
```

**Fund MXN Wallet:**
```bash
curl -X POST "${BASE_URL}/wallets/user123/fund" \
  -H "Content-Type: application/json" \
  -d '{
    "currency": "MXN",
    "amount": 25000.50
  }' \
  | jq '.'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Wallet funded successfully",
  "user_id": "user123",
  "currency": "USD",
  "amount": 1500.75,
  "new_balance": 1500.75,
  "transaction_id": 1
}
```

### 3. Get Wallet Balances
Retrieve all wallet balances for a user.

```bash
curl -X GET "${BASE_URL}/wallets/user123/balances" \
  -H "Content-Type: application/json" \
  | jq '.'
```

**Expected Response:**
```json
{
  "USD": 1500.75,
  "MXN": 25000.50
}
```

**Empty balances response:**
```json
{}
```

### 4. Withdraw Funds
Withdraw money from a user's wallet.

**Withdraw from USD:**
```bash
curl -X POST "${BASE_URL}/wallets/user123/withdraw" \
  -H "Content-Type: application/json" \
  -d '{
    "currency": "USD",
    "amount": 200.25
  }' \
  | jq '.'
```

**Withdraw from MXN:**
```bash
curl -X POST "${BASE_URL}/wallets/user123/withdraw" \
  -H "Content-Type: application/json" \
  -d '{
    "currency": "MXN",
    "amount": 5000.00
  }' \
  | jq '.'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Funds withdrawn successfully",
  "user_id": "user123",
  "currency": "USD",
  "amount": 200.25,
  "new_balance": 1300.50,
  "transaction_id": 2
}
```

## Currency Conversion

### 5. Convert Currency
Convert money between USD and MXN.

**Convert USD to MXN:**
```bash
curl -X POST "${BASE_URL}/wallets/user123/convert" \
  -H "Content-Type: application/json" \
  -d '{
    "from_currency": "USD",
    "to_currency": "MXN",
    "amount": 500.00
  }' \
  | jq '.'
```

**Convert MXN to USD:**
```bash
curl -X POST "${BASE_URL}/wallets/user123/convert" \
  -H "Content-Type: application/json" \
  -d '{
    "from_currency": "MXN",
    "to_currency": "USD",
    "amount": 10000.00
  }' \
  | jq '.'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Currency conversion completed",
  "user_id": "user123",
  "from_currency": "USD",
  "to_currency": "MXN",
  "amount": 500.00,
  "converted_amount": 10000.00,
  "fx_rate": 20.00,
  "from_balance": 800.50,
  "to_balance": 35000.50
}
```

## Transaction History

### 6. Get Transaction History
Retrieve transaction history for a user.

**Get all transactions:**
```bash
curl -X GET "${BASE_URL}/wallets/user123/transactions" \
  -H "Content-Type: application/json" \
  | jq '.'
```

**Get limited transactions:**
```bash
curl -X GET "${BASE_URL}/wallets/user123/transactions?limit=10" \
  -H "Content-Type: application/json" \
  | jq '.'
```

**Expected Response:**
```json
{
  "transactions": [
    {
      "id": 4,
      "user_id": "user123",
      "transaction_type": "convert_out",
      "currency": "USD",
      "amount": 500.00,
      "from_currency": "USD",
      "to_currency": "MXN",
      "fx_rate": 20.00,
      "created_at": "2025-01-15T10:30:45Z"
    },
    {
      "id": 3,
      "user_id": "user123",
      "transaction_type": "convert_in",
      "currency": "MXN",
      "amount": 10000.00,
      "from_currency": "USD",
      "to_currency": "MXN",
      "fx_rate": 20.00,
      "created_at": "2025-01-15T10:30:45Z"
    }
  ]
}
```

## Account Reconciliation

### 7. Reconcile Balances
Verify that wallet balances match transaction history.

```bash
curl -X GET "${BASE_URL}/wallets/user123/reconcile" \
  -H "Content-Type: application/json" \
  | jq '.'
```

**Expected Response (Reconciled):**
```json
{
  "reconciled": true,
  "message": "All balances are correctly reconciled",
  "balances": {
    "USD": {
      "wallet_balance": 800.50,
      "calculated_balance": 800.50,
      "difference": 0.00
    },
    "MXN": {
      "wallet_balance": 35000.50,
      "calculated_balance": 35000.50,
      "difference": 0.00
    }
  }
}
```

**Expected Response (Not Reconciled):**
```json
{
  "reconciled": false,
  "message": "Balance discrepancies found",
  "balances": {
    "USD": {
      "wallet_balance": 800.50,
      "calculated_balance": 850.50,
      "difference": -50.00
    }
  }
}
```

## FX Rate Management

### 8. Get FX Rates
Retrieve current exchange rates.

```bash
curl -X GET "${BASE_URL}/fx/rates" \
  -H "Content-Type: application/json" \
  | jq '.'
```

**Expected Response:**
```json
{
  "rates": {
    "USD/MXN": 20.00,
    "MXN/USD": 0.05
  }
}
```

### 9. Update FX Rate
Update exchange rate between currency pairs.

**Update USD to MXN rate:**
```bash
curl -X PUT "${BASE_URL}/fx/rates" \
  -H "Content-Type: application/json" \
  -d '{
    "from_currency": "USD",
    "to_currency": "MXN",
    "rate": 20.25
  }' \
  | jq '.'
```

**Update MXN to USD rate:**
```bash
curl -X PUT "${BASE_URL}/fx/rates" \
  -H "Content-Type: application/json" \
  -d '{
    "from_currency": "MXN",
    "to_currency": "USD",
    "rate": 0.0494
  }' \
  | jq '.'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Updated rate USD/MXN to 20.25"
}
```

## Error Examples

### Validation Errors

**Invalid currency:**
```bash
curl -X POST "${BASE_URL}/wallets/user123/fund" \
  -H "Content-Type: application/json" \
  -d '{
    "currency": "EUR",
    "amount": 100.00
  }' \
  | jq '.'
```

**Response:**
```json
{
  "error": "Validation error",
  "details": {
    "currency": ["Not a valid choice."]
  }
}
```

**Negative amount:**
```bash
curl -X POST "${BASE_URL}/wallets/user123/fund" \
  -H "Content-Type: application/json" \
  -d '{
    "currency": "USD",
    "amount": -100.00
  }' \
  | jq '.'
```

**Response:**
```json
{
  "error": "Amount must be greater than 0"
}
```

**Missing required fields:**
```bash
curl -X POST "${BASE_URL}/wallets/user123/fund" \
  -H "Content-Type: application/json" \
  -d '{
    "currency": "USD"
  }' \
  | jq '.'
```

**Response:**
```json
{
  "error": "Validation error",
  "details": {
    "amount": ["Missing data for required field."]
  }
}
```

**Insufficient funds:**
```bash
curl -X POST "${BASE_URL}/wallets/user123/withdraw" \
  -H "Content-Type: application/json" \
  -d '{
    "currency": "USD",
    "amount": 999999.00
  }' \
  | jq '.'
```

**Response:**
```json
{
  "error": "Insufficient funds"
}
```

**Invalid JSON:**
```bash
curl -X POST "${BASE_URL}/wallets/user123/fund" \
  -H "Content-Type: application/json" \
  -d 'invalid json' \
  | jq '.'
```

**Response:**
```json
{
  "error": "Validation error",
  "details": "Invalid JSON payload"
}
```

## Complete User Journey Example

Here's a complete example showing a typical user journey:

```bash
#!/bin/bash

BASE_URL="http://localhost:5000"
USER_ID="demo_user"

echo "=== FX Payment Processor Demo ==="

echo "1. Check initial balances"
curl -s -X GET "${BASE_URL}/wallets/${USER_ID}/balances" | jq '.'

echo -e "\n2. Fund USD wallet with $2000"
curl -s -X POST "${BASE_URL}/wallets/${USER_ID}/fund" \
  -H "Content-Type: application/json" \
  -d '{"currency": "USD", "amount": 2000.00}' | jq '.'

echo -e "\n3. Fund MXN wallet with $40000 pesos"
curl -s -X POST "${BASE_URL}/wallets/${USER_ID}/fund" \
  -H "Content-Type: application/json" \
  -d '{"currency": "MXN", "amount": 40000.00}' | jq '.'

echo -e "\n4. Check balances after funding"
curl -s -X GET "${BASE_URL}/wallets/${USER_ID}/balances" | jq '.'

echo -e "\n5. Convert $500 USD to MXN"
curl -s -X POST "${BASE_URL}/wallets/${USER_ID}/convert" \
  -H "Content-Type: application/json" \
  -d '{"from_currency": "USD", "to_currency": "MXN", "amount": 500.00}' | jq '.'

echo -e "\n6. Withdraw $200 USD"
curl -s -X POST "${BASE_URL}/wallets/${USER_ID}/withdraw" \
  -H "Content-Type: application/json" \
  -d '{"currency": "USD", "amount": 200.00}' | jq '.'

echo -e "\n7. Check final balances"
curl -s -X GET "${BASE_URL}/wallets/${USER_ID}/balances" | jq '.'

echo -e "\n8. Get transaction history"
curl -s -X GET "${BASE_URL}/wallets/${USER_ID}/transactions" | jq '.'

echo -e "\n9. Reconcile balances"
curl -s -X GET "${BASE_URL}/wallets/${USER_ID}/reconcile" | jq '.'

echo -e "\n10. Check current FX rates"
curl -s -X GET "${BASE_URL}/fx/rates" | jq '.'

echo -e "\n=== Demo Complete ==="
```

## Testing with Different Precision

### High Precision Amounts
```bash
# Test with 8 decimal places
curl -X POST "${BASE_URL}/wallets/precision_test/fund" \
  -H "Content-Type: application/json" \
  -d '{
    "currency": "USD",
    "amount": 1234.12345678
  }' \
  | jq '.'
```

### Bulk Operations Script

```bash
#!/bin/bash
BASE_URL="http://localhost:5000"

# Create multiple users and perform operations
for i in {1..5}; do
  USER_ID="bulk_user_${i}"
  echo "Processing user: ${USER_ID}"

  # Fund each user
  curl -s -X POST "${BASE_URL}/wallets/${USER_ID}/fund" \
    -H "Content-Type: application/json" \
    -d "{\"currency\": \"USD\", \"amount\": $((1000 + i * 100))}" > /dev/null

  # Convert some amount
  curl -s -X POST "${BASE_URL}/wallets/${USER_ID}/convert" \
    -H "Content-Type: application/json" \
    -d "{\"from_currency\": \"USD\", \"to_currency\": \"MXN\", \"amount\": $((100 + i * 10))}" > /dev/null
done

echo "Bulk operations completed"
```

## Notes

1. **jq**: All examples use `jq` for pretty-printing JSON. Install with `brew install jq` on macOS or `apt-get install jq` on Ubuntu.

2. **Error Handling**: Always check the HTTP status code. Successful operations return 200, validation errors return 400, and server errors return 500.

3. **Precision**: The API handles up to 8 decimal places for financial amounts.

4. **Concurrency**: Multiple requests can be made concurrently, and the system maintains data consistency.

5. **Rate Limits**: Consider implementing rate limiting in production environments.

For more information about the API architecture and testing considerations, see `testing-and-improvements.md`.
