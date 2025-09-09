import pytest
import json
from decimal import Decimal
from app.services import FxService
from app.models import FxRate

class TestFxRatesEndpoints:
    
    def test_get_fx_rates(self, client):
        response = client.get('/fx/rates')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'rates' in data
        assert 'USD/MXN' in data['rates']
        assert 'MXN/USD' in data['rates']
        assert data['rates']['USD/MXN']['rate'] == 18.7
        assert data['rates']['MXN/USD']['rate'] == 0.053
    
    def test_update_fx_rate(self, client, app):
        with app.app_context():
            response = client.put(
                '/fx/rates',
                data=json.dumps({
                    'from_currency': 'USD',
                    'to_currency': 'MXN',
                    'rate': 19.5
                }),
                content_type='application/json'
            )
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            
            fx_rate = FxRate.query.filter_by(from_currency='USD', to_currency='MXN').first()
            assert fx_rate.rate == Decimal('19.5')
    
    def test_update_fx_rate_missing_fields(self, client):
        response = client.put(
            '/fx/rates',
            data=json.dumps({
                'from_currency': 'USD',
                'rate': 19.5
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_update_fx_rate_invalid_rate(self, client):
        response = client.put(
            '/fx/rates',
            data=json.dumps({
                'from_currency': 'USD',
                'to_currency': 'MXN',
                'rate': 'invalid'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

class TestFxService:
    
    def test_initialize_rates(self, app):
        with app.app_context():
            FxService.initialize_rates()
            
            usd_to_mxn = FxRate.query.filter_by(from_currency='USD', to_currency='MXN').first()
            mxn_to_usd = FxRate.query.filter_by(from_currency='MXN', to_currency='USD').first()
            
            assert usd_to_mxn is not None
            assert usd_to_mxn.rate == Decimal('18.70')
            assert mxn_to_usd is not None
            assert mxn_to_usd.rate == Decimal('0.053')
    
    def test_get_rate_same_currency(self, app):
        with app.app_context():
            rate = FxService.get_rate('USD', 'USD')
            assert rate == Decimal('1')
    
    def test_get_rate_existing(self, app):
        with app.app_context():
            rate = FxService.get_rate('USD', 'MXN')
            assert rate == Decimal('18.70')
    
    def test_get_rate_not_found(self, app):
        with app.app_context():
            with pytest.raises(ValueError, match="FX rate not found"):
                FxService.get_rate('USD', 'EUR')
    
    def test_update_rate_existing(self, app):
        with app.app_context():
            FxService.update_rate('USD', 'MXN', Decimal('20.0'))
            
            rate = FxService.get_rate('USD', 'MXN')
            assert rate == Decimal('20.0')
    
    def test_update_rate_new(self, app):
        with app.app_context():
            FxService.update_rate('USD', 'EUR', Decimal('0.85'))
            
            rate = FxService.get_rate('USD', 'EUR')
            assert rate == Decimal('0.85')
    
    def test_get_all_rates(self, app):
        with app.app_context():
            rates = FxService.get_all_rates()
            
            assert 'USD/MXN' in rates
            assert 'MXN/USD' in rates
            assert rates['USD/MXN']['rate'] == 18.7
            assert rates['MXN/USD']['rate'] == 0.053