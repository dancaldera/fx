# API Usage Examples

This document provides practical examples of using the FX Payment Processor API.

## Authentication

Currently, the API uses simple user_id based identification. No authentication headers are required.

## Base URL

When running locally: `http://localhost:5000`
When running with Docker: `http://localhost:5000`

## Examples

### 1. Fund a Wallet

Add money to a user's wallet in a specific currency.

```bash
curl -X POST http://localhost:5000/wallets/user123/fund \
  -H "Content-Type: application/json" \
  -d '{
    "currency": "USD",
    "amount": 1000.50
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Funded 1000.50 USD",
  "balance": 1000.50
}
```

### 2. Convert Currency

Convert money from one currency to another using current FX rates.

```bash
curl -X POST http://localhost:5000/wallets/user123/convert \
  -H "Content-Type: application/json" \
  -d '{
    "from_currency": "USD",
    "to_currency": "MXN",
    "amount": 500
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Converted 500 USD to 9350.00000000 MXN",
  "fx_rate": 18.7,
  "converted_amount": 9350.00000000
}
```

### 3. Withdraw Funds

Withdraw money from a user's wallet.

```bash
curl -X POST http://localhost:5000/wallets/user123/withdraw \
  -H "Content-Type: application/json" \
  -d '{
    "currency": "MXN",
    "amount": 1000
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Withdrew 1000 MXN",
  "balance": 8350.00000000
}
```

### 4. View Balances

Check all balances for a user.

```bash
curl -X GET http://localhost:5000/wallets/user123/balances
```

**Response:**
```json
{
  "USD": 500.50,
  "MXN": 8350.00000000
}
```

### 5. View Transaction History

Get transaction history for a user.

```bash
curl -X GET http://localhost:5000/wallets/user123/transactions?limit=10
```

**Response:**
```json
{
  "transactions": [
    {
      "id": 3,
      "type": "withdraw",
      "currency": "MXN",
      "amount": 1000.0,
      "from_currency": null,
      "to_currency": null,
      "fx_rate": null,
      "timestamp": "2024-01-01T15:30:00.123456"
    },
    {
      "id": 2,
      "type": "convert_in",
      "currency": "MXN",
      "amount": 9350.0,
      "from_currency": "USD",
      "to_currency": "MXN",
      "fx_rate": 18.7,
      "timestamp": "2024-01-01T15:00:00.123456"
    },
    {
      "id": 1,
      "type": "fund",
      "currency": "USD",
      "amount": 1000.5,
      "from_currency": null,
      "to_currency": null,
      "fx_rate": null,
      "timestamp": "2024-01-01T14:00:00.123456"
    }
  ]
}
```

### 6. Reconcile Balances

Check if calculated balances match actual balances.

```bash
curl -X GET http://localhost:5000/wallets/user123/reconcile
```

**Response (when reconciled):**
```json
{
  "reconciled": true,
  "discrepancies": {}
}
```

**Response (when discrepancies exist):**
```json
{
  "reconciled": false,
  "discrepancies": {
    "USD": {
      "calculated": 500.50,
      "actual": 500.49,
      "difference": -0.01
    }
  }
}
```

### 7. View FX Rates

Get current FX rates.

```bash
curl -X GET http://localhost:5000/fx/rates
```

**Response:**
```json
{
  "rates": {
    "USD/MXN": {
      "rate": 18.7,
      "updated_at": "2024-01-01T12:00:00.123456"
    },
    "MXN/USD": {
      "rate": 0.053,
      "updated_at": "2024-01-01T12:00:00.123456"
    }
  }
}
```

### 8. Update FX Rate

Update a specific FX rate (for dynamic rate simulation).

```bash
curl -X PUT http://localhost:5000/fx/rates \
  -H "Content-Type: application/json" \
  -d '{
    "from_currency": "USD",
    "to_currency": "MXN",
    "rate": 19.5
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Updated rate USD/MXN to 19.5"
}
```

## Error Responses

### Validation Errors

```json
{
  "error": "Validation error",
  "details": {
    "currency": ["Must be one of: USD, MXN."],
    "amount": ["Must be greater than 0."]
  }
}
```

### Business Logic Errors

```json
{
  "error": "Insufficient funds"
}
```

```json
{
  "error": "FX rate not found for EUR to USD"
}
```

### Server Errors

```json
{
  "error": "Internal server error"
}
```

## Complete User Journey Example

Here's a complete example of a user's journey through the system:

```bash
# 1. Fund USD wallet
curl -X POST http://localhost:5000/wallets/alice/fund \
  -H "Content-Type: application/json" \
  -d '{"currency": "USD", "amount": 2000}'

# 2. Fund MXN wallet
curl -X POST http://localhost:5000/wallets/alice/fund \
  -H "Content-Type: application/json" \
  -d '{"currency": "MXN", "amount": 10000}'

# 3. Check balances
curl -X GET http://localhost:5000/wallets/alice/balances

# 4. Convert USD to MXN
curl -X POST http://localhost:5000/wallets/alice/convert \
  -H "Content-Type: application/json" \
  -d '{"from_currency": "USD", "to_currency": "MXN", "amount": 500}'

# 5. Withdraw MXN
curl -X POST http://localhost:5000/wallets/alice/withdraw \
  -H "Content-Type: application/json" \
  -d '{"currency": "MXN", "amount": 5000}'

# 6. View transaction history
curl -X GET http://localhost:5000/wallets/alice/transactions

# 7. Reconcile balances
curl -X GET http://localhost:5000/wallets/alice/reconcile
```

## Rate Limits and Constraints

- Maximum 8 decimal places for all amounts
- Supported currencies: USD, MXN
- Negative balances are not allowed
- All operations are atomic and consistent
- Transaction history is unlimited but paginated via limit parameter
