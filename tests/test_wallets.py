import pytest
import json
from decimal import Decimal
from app import db
from app.models import Wallet, Transaction, TransactionType
from app.services import WalletService

class TestWalletEndpoints:
    
    def test_fund_wallet_success(self, client, app):
        with app.app_context():
            response = client.post(
                '/wallets/user1/fund',
                data=json.dumps({'currency': 'USD', 'amount': 1000}),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['balance'] == 1000
            
            wallet = Wallet.query.filter_by(user_id='user1', currency='USD').first()
            assert wallet is not None
            assert wallet.balance == Decimal('1000')
    
    def test_fund_wallet_invalid_amount(self, client):
        response = client.post(
            '/wallets/user1/fund',
            data=json.dumps({'currency': 'USD', 'amount': -100}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_fund_wallet_invalid_currency(self, client):
        response = client.post(
            '/wallets/user1/fund',
            data=json.dumps({'currency': 'EUR', 'amount': 100}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_withdraw_funds_success(self, client, app):
        with app.app_context():
            client.post(
                '/wallets/user1/fund',
                data=json.dumps({'currency': 'USD', 'amount': 1000}),
                content_type='application/json'
            )
            
            response = client.post(
                '/wallets/user1/withdraw',
                data=json.dumps({'currency': 'USD', 'amount': 300}),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['balance'] == 700
    
    def test_withdraw_insufficient_funds(self, client, app):
        with app.app_context():
            response = client.post(
                '/wallets/user1/withdraw',
                data=json.dumps({'currency': 'USD', 'amount': 1000}),
                content_type='application/json'
            )
            
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
            assert 'Insufficient funds' in data['error']
    
    def test_convert_currency_success(self, client, app):
        with app.app_context():
            client.post(
                '/wallets/user1/fund',
                data=json.dumps({'currency': 'USD', 'amount': 1000}),
                content_type='application/json'
            )
            
            response = client.post(
                '/wallets/user1/convert',
                data=json.dumps({
                    'from_currency': 'USD',
                    'to_currency': 'MXN',
                    'amount': 500
                }),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['fx_rate'] == 18.7
            assert data['converted_amount'] == 9350
    
    def test_convert_insufficient_funds(self, client):
        response = client.post(
            '/wallets/user1/convert',
            data=json.dumps({
                'from_currency': 'USD',
                'to_currency': 'MXN',
                'amount': 1000
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_get_balances_empty(self, client):
        response = client.get('/wallets/user1/balances')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == {}
    
    def test_get_balances_with_funds(self, client, app):
        with app.app_context():
            client.post(
                '/wallets/user1/fund',
                data=json.dumps({'currency': 'USD', 'amount': 1000}),
                content_type='application/json'
            )
            client.post(
                '/wallets/user1/fund',
                data=json.dumps({'currency': 'MXN', 'amount': 5000}),
                content_type='application/json'
            )
            
            response = client.get('/wallets/user1/balances')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['USD'] == 1000
            assert data['MXN'] == 5000
    
    def test_get_transactions(self, client, app):
        with app.app_context():
            client.post(
                '/wallets/user1/fund',
                data=json.dumps({'currency': 'USD', 'amount': 1000}),
                content_type='application/json'
            )
            
            response = client.get('/wallets/user1/transactions')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'transactions' in data
            assert len(data['transactions']) == 1
            assert data['transactions'][0]['type'] == 'fund'
            assert data['transactions'][0]['currency'] == 'USD'
            assert data['transactions'][0]['amount'] == 1000
    
    def test_reconciliation_success(self, client, app):
        with app.app_context():
            client.post(
                '/wallets/user1/fund',
                data=json.dumps({'currency': 'USD', 'amount': 1000}),
                content_type='application/json'
            )
            
            response = client.get('/wallets/user1/reconcile')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['reconciled'] is True
            assert data['discrepancies'] == {}

class TestWalletServices:
    
    def test_get_or_create_wallet(self, app):
        with app.app_context():
            wallet = WalletService.get_or_create_wallet('user1', 'USD')
            assert wallet.user_id == 'user1'
            assert wallet.currency == 'USD'
            assert wallet.balance == Decimal('0')
            
            same_wallet = WalletService.get_or_create_wallet('user1', 'USD')
            assert wallet.id == same_wallet.id
    
    def test_fund_wallet_service(self, app):
        with app.app_context():
            result = WalletService.fund_wallet('user1', 'USD', Decimal('1000'))
            assert result['success'] is True
            assert result['balance'] == Decimal('1000')
            
            transaction = Transaction.query.filter_by(
                user_id='user1',
                transaction_type=TransactionType.FUND
            ).first()
            assert transaction is not None
            assert transaction.amount == Decimal('1000')
    
    def test_fund_wallet_invalid_amount(self, app):
        with app.app_context():
            with pytest.raises(ValueError, match="Amount must be greater than 0"):
                WalletService.fund_wallet('user1', 'USD', Decimal('-100'))
    
    def test_withdraw_funds_service(self, app):
        with app.app_context():
            WalletService.fund_wallet('user1', 'USD', Decimal('1000'))
            
            result = WalletService.withdraw_funds('user1', 'USD', Decimal('300'))
            assert result['success'] is True
            assert result['balance'] == Decimal('700')
    
    def test_withdraw_insufficient_funds(self, app):
        with app.app_context():
            with pytest.raises(ValueError, match="Insufficient funds"):
                WalletService.withdraw_funds('user1', 'USD', Decimal('1000'))
    
    def test_convert_currency_service(self, app):
        with app.app_context():
            WalletService.fund_wallet('user1', 'USD', Decimal('1000'))
            
            result = WalletService.convert_currency(
                'user1', 'USD', 'MXN', Decimal('500')
            )
            
            assert result['success'] is True
            assert result['fx_rate'] == Decimal('18.70')
            assert result['converted_amount'] == Decimal('9350.00000000')
            
            usd_wallet = Wallet.query.filter_by(user_id='user1', currency='USD').first()
            mxn_wallet = Wallet.query.filter_by(user_id='user1', currency='MXN').first()
            
            assert usd_wallet.balance == Decimal('500')
            assert mxn_wallet.balance == Decimal('9350.00000000')
    
    def test_convert_same_currency(self, app):
        with app.app_context():
            with pytest.raises(ValueError, match="Cannot convert to the same currency"):
                WalletService.convert_currency('user1', 'USD', 'USD', Decimal('100'))
    
    def test_get_balances_service(self, app):
        with app.app_context():
            balances = WalletService.get_balances('user1')
            assert balances == {}
            
            WalletService.fund_wallet('user1', 'USD', Decimal('1000'))
            WalletService.fund_wallet('user1', 'MXN', Decimal('5000'))
            
            balances = WalletService.get_balances('user1')
            assert balances['USD'] == 1000
            assert balances['MXN'] == 5000
    
    def test_complex_transaction_flow(self, app):
        with app.app_context():
            WalletService.fund_wallet('user1', 'USD', Decimal('2000'))
            
            WalletService.convert_currency('user1', 'USD', 'MXN', Decimal('1000'))
            
            WalletService.withdraw_funds('user1', 'MXN', Decimal('1000'))
            
            reconciliation = WalletService.reconcile_balances('user1')
            assert reconciliation['reconciled'] is True
            
            balances = WalletService.get_balances('user1')
            assert balances['USD'] == 1000
            assert balances['MXN'] == 17700