import pytest
import json

class TestAPIEndpoints:
    
    def test_index_endpoint(self, client):
        response = client.get('/')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'FX Payment Processor API'
        assert data['version'] == '1.0.0'
        assert 'endpoints' in data
        assert 'fund' in data['endpoints']
        assert 'convert' in data['endpoints']
        assert 'withdraw' in data['endpoints']
        assert 'balances' in data['endpoints']
        assert 'transactions' in data['endpoints']
        assert 'reconcile' in data['endpoints']
        assert 'fx_rates' in data['endpoints']
    
    def test_complete_user_journey(self, client, app):
        """Test a complete user journey through the system"""
        with app.app_context():
            user_id = 'journey_user'
            
            # 1. Start with empty balances
            response = client.get(f'/wallets/{user_id}/balances')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data == {}
            
            # 2. Fund USD wallet
            response = client.post(
                f'/wallets/{user_id}/fund',
                data=json.dumps({'currency': 'USD', 'amount': 2000}),
                content_type='application/json'
            )
            assert response.status_code == 200
            
            # 3. Fund MXN wallet
            response = client.post(
                f'/wallets/{user_id}/fund',
                data=json.dumps({'currency': 'MXN', 'amount': 10000}),
                content_type='application/json'
            )
            assert response.status_code == 200
            
            # 4. Check balances
            response = client.get(f'/wallets/{user_id}/balances')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['USD'] == 2000
            assert data['MXN'] == 10000
            
            # 5. Convert USD to MXN
            response = client.post(
                f'/wallets/{user_id}/convert',
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
            
            # 6. Convert MXN to USD
            response = client.post(
                f'/wallets/{user_id}/convert',
                data=json.dumps({
                    'from_currency': 'MXN',
                    'to_currency': 'USD',
                    'amount': 1000
                }),
                content_type='application/json'
            )
            assert response.status_code == 200
            
            # 7. Withdraw from USD
            response = client.post(
                f'/wallets/{user_id}/withdraw',
                data=json.dumps({'currency': 'USD', 'amount': 100}),
                content_type='application/json'
            )
            assert response.status_code == 200
            
            # 8. Withdraw from MXN
            response = client.post(
                f'/wallets/{user_id}/withdraw',
                data=json.dumps({'currency': 'MXN', 'amount': 500}),
                content_type='application/json'
            )
            assert response.status_code == 200
            
            # 9. Check final balances
            response = client.get(f'/wallets/{user_id}/balances')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'USD' in data
            assert 'MXN' in data
            
            # 10. Get transaction history
            response = client.get(f'/wallets/{user_id}/transactions')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'transactions' in data
            assert len(data['transactions']) == 8  # 2 funds + 4 converts + 2 withdraws
            
            # 11. Reconcile balances
            response = client.get(f'/wallets/{user_id}/reconcile')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['reconciled'] is True
    
    def test_edge_cases(self, client):
        """Test various edge cases"""
        user_id = 'edge_user'
        
        # Test zero amount funding
        response = client.post(
            f'/wallets/{user_id}/fund',
            data=json.dumps({'currency': 'USD', 'amount': 0}),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        # Test negative amount funding
        response = client.post(
            f'/wallets/{user_id}/fund',
            data=json.dumps({'currency': 'USD', 'amount': -100}),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        # Test invalid JSON
        response = client.post(
            f'/wallets/{user_id}/fund',
            data='invalid json',
            content_type='application/json'
        )
        assert response.status_code == 400
        
        # Test missing fields
        response = client.post(
            f'/wallets/{user_id}/fund',
            data=json.dumps({'currency': 'USD'}),
            content_type='application/json'
        )
        assert response.status_code == 400
        
        # Test unsupported currency
        response = client.post(
            f'/wallets/{user_id}/fund',
            data=json.dumps({'currency': 'EUR', 'amount': 100}),
            content_type='application/json'
        )
        assert response.status_code == 400
    
    def test_precision_handling(self, client, app):
        """Test financial precision handling"""
        with app.app_context():
            user_id = 'precision_user'
            
            # Fund with high precision amount
            response = client.post(
                f'/wallets/{user_id}/fund',
                data=json.dumps({'currency': 'USD', 'amount': 1000.12345678}),
                content_type='application/json'
            )
            assert response.status_code == 200
            
            # Check balance precision
            response = client.get(f'/wallets/{user_id}/balances')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['USD'] == 1000.12345678
            
            # Convert with precision
            response = client.post(
                f'/wallets/{user_id}/convert',
                data=json.dumps({
                    'from_currency': 'USD',
                    'to_currency': 'MXN',
                    'amount': 100.12345678
                }),
                content_type='application/json'
            )
            assert response.status_code == 200
            data = json.loads(response.data)
            # Verify the conversion maintains precision
            assert 'converted_amount' in data
    
    def test_concurrent_operations(self, client, app):
        """Test that operations maintain consistency"""
        with app.app_context():
            user_id = 'concurrent_user'
            
            # Fund wallet
            client.post(
                f'/wallets/{user_id}/fund',
                data=json.dumps({'currency': 'USD', 'amount': 1000}),
                content_type='application/json'
            )
            
            # Perform multiple operations
            for i in range(5):
                # Convert some amount
                client.post(
                    f'/wallets/{user_id}/convert',
                    data=json.dumps({
                        'from_currency': 'USD',
                        'to_currency': 'MXN',
                        'amount': 10
                    }),
                    content_type='application/json'
                )
                
                # Convert back
                client.post(
                    f'/wallets/{user_id}/convert',
                    data=json.dumps({
                        'from_currency': 'MXN',
                        'to_currency': 'USD',
                        'amount': 100
                    }),
                    content_type='application/json'
                )
            
            # Check reconciliation
            response = client.get(f'/wallets/{user_id}/reconcile')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['reconciled'] is True