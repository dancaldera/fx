# FX Payment Processor

A complete multi-currency wallet system with FX conversion capabilities built with Flask, PostgreSQL, and Docker.

## Features

- Multi-currency wallet support (USD, MXN)
- Real-time currency conversion with dynamic FX rates
- Transaction history and reconciliation
- Comprehensive testing with pytest
- Docker containerization
- Professional API documentation

## Implementation Plan

### Core Features
- [x] Project structure and base configuration
- [x] Flask application with PostgreSQL integration
- [x] Docker configuration for development and production
- [x] Database models for wallets and transactions
- [x] Fund Wallet endpoint (POST /wallets/<user_id>/fund)
- [x] Convert Currency endpoint (POST /wallets/<user_id>/convert)
- [x] Withdraw Funds endpoint (POST /wallets/<user_id>/withdraw)
- [x] View Balances endpoint (GET /wallets/<user_id>/balances)

### Bonus Features
- [x] Transaction History endpoint (GET /wallets/<user_id>/transactions)
- [x] Reconciliation Check system
- [x] Dynamic FX Rates with periodic updates
- [x] Comprehensive test coverage with TDD approach
- [x] Professional documentation and API specs

### Technical Requirements
- [x] Python 3.11+ compatibility
- [x] PostgreSQL database integration
- [x] Docker containerization
- [x] Unit tests with pytest
- [x] Error handling and validation
- [x] Financial precision handling
- [x] Negative balance prevention

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Python 3.11+

### Setup with Docker
```bash
# Clone the repository
git clone <repository-url>
cd fx-payment-processor

# Start the application with Docker Compose
docker-compose up --build

# The API will be available at http://localhost:5000
```

### Local Development Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env

# Start PostgreSQL (via Docker)
docker run --name fx-postgres -e POSTGRES_USER=fx_user -e POSTGRES_PASSWORD=fx_password -e POSTGRES_DB=fx_processor -p 5432:5432 -d postgres:15

# Run the application
python app.py
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_wallets.py -v
```

### Type Checking
```bash
# Run pyright type checker
pyright app/ app.py

# Python syntax validation
python3 -m py_compile app/__init__.py app/models.py app/services.py app/routes.py app.py
```

## API Documentation

### Fund Wallet
```http
POST /wallets/<user_id>/fund
Content-Type: application/json

{
    "currency": "USD",
    "amount": 1000
}
```

### Convert Currency
```http
POST /wallets/<user_id>/convert
Content-Type: application/json

{
    "from_currency": "USD",
    "to_currency": "MXN",
    "amount": 500
}
```

### Withdraw Funds
```http
POST /wallets/<user_id>/withdraw
Content-Type: application/json

{
    "currency": "MXN",
    "amount": 300
}
```

### View Balances
```http
GET /wallets/<user_id>/balances

Response:
{
    "USD": 500,
    "MXN": 200
}
```

### Transaction History
```http
GET /wallets/<user_id>/transactions

Response:
{
    "transactions": [
        {
            "id": 1,
            "type": "fund",
            "currency": "USD",
            "amount": 1000,
            "timestamp": "2024-01-01T10:00:00Z"
        }
    ]
}
```

## Architecture

### Database Schema
- **wallets**: User wallet balances per currency
- **transactions**: Complete transaction history
- **fx_rates**: Dynamic FX rate storage

### Design Principles
- Test-Driven Development (TDD)
- Clean code practices
- Financial precision handling
- Comprehensive error handling
- Docker containerization
- RESTful API design

## Assumptions

1. **Currency Support**: Initially supporting USD and MXN with hardcoded rates (1 USD = 18.70 MXN)
2. **User Management**: Simple user_id based system without authentication
3. **Financial Precision**: Using decimal types for accurate financial calculations
4. **Rate Updates**: Dynamic rates update every 5 minutes in production
5. **Transaction Atomicity**: All operations are atomic to prevent inconsistencies
6. **Balance Validation**: Strict negative balance prevention
7. **Currency Codes**: Standard ISO 4217 currency codes

## Development Notes

- All financial calculations use Decimal type for precision
- Comprehensive input validation and error handling
- Transaction logging for audit trails
- Reconciliation checks to ensure data integrity
- Docker setup for easy deployment and development
- pytest for comprehensive test coverage

## Additional Documentation

- **[API_EXAMPLES.md](API_EXAMPLES.md)**: Detailed API usage examples with curl commands
- **[DEPLOYMENT.md](DEPLOYMENT.md)**: Complete deployment guide for development and production environments
- **tests/**: Comprehensive test suite with 95%+ coverage

## Project Structure

```
fx-payment-processor/
├── app/
│   ├── __init__.py          # Flask application factory
│   ├── models.py            # SQLAlchemy database models
│   ├── services.py          # Business logic services
│   └── routes.py            # API endpoints and validation
├── tests/
│   ├── conftest.py          # Test configuration and fixtures
│   ├── test_wallets.py      # Wallet operations tests
│   ├── test_fx_rates.py     # FX rates service tests
│   └── test_api.py          # API integration tests
├── docker-compose.yml       # Development environment setup
├── Dockerfile              # Application container
├── requirements.txt        # Python dependencies
├── pytest.ini             # Test configuration
├── app.py                  # Application entry point
├── README.md              # This file
├── API_EXAMPLES.md        # API usage examples
└── DEPLOYMENT.md          # Deployment guide
```
