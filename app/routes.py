from flask import Blueprint, request, jsonify
from app.services import WalletService, FxService
from decimal import Decimal, InvalidOperation
from marshmallow import Schema, fields, ValidationError

bp = Blueprint('main', __name__)

class FundWalletSchema(Schema):
    currency = fields.Str(required=True, validate=lambda x: x in ['USD', 'MXN'])
    amount = fields.Decimal(required=True, places=8)

class ConvertCurrencySchema(Schema):
    from_currency = fields.Str(required=True, validate=lambda x: x in ['USD', 'MXN'])
    to_currency = fields.Str(required=True, validate=lambda x: x in ['USD', 'MXN'])
    amount = fields.Decimal(required=True, places=8)

class WithdrawFundsSchema(Schema):
    currency = fields.Str(required=True, validate=lambda x: x in ['USD', 'MXN'])
    amount = fields.Decimal(required=True, places=8)

@bp.route('/')
def index():
    return jsonify({
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
    })

@bp.route('/wallets/<user_id>/fund', methods=['POST'])
def fund_wallet(user_id):
    try:
        schema = FundWalletSchema()
        data = schema.load(request.json)
        
        result = WalletService.fund_wallet(
            user_id=user_id,
            currency=data['currency'],
            amount=data['amount']
        )
        
        return jsonify(result), 200
        
    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.messages}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/wallets/<user_id>/convert', methods=['POST'])
def convert_currency(user_id):
    try:
        schema = ConvertCurrencySchema()
        data = schema.load(request.json)
        
        result = WalletService.convert_currency(
            user_id=user_id,
            from_currency=data['from_currency'],
            to_currency=data['to_currency'],
            amount=data['amount']
        )
        
        return jsonify(result), 200
        
    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.messages}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/wallets/<user_id>/withdraw', methods=['POST'])
def withdraw_funds(user_id):
    try:
        schema = WithdrawFundsSchema()
        data = schema.load(request.json)
        
        result = WalletService.withdraw_funds(
            user_id=user_id,
            currency=data['currency'],
            amount=data['amount']
        )
        
        return jsonify(result), 200
        
    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.messages}), 400
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/wallets/<user_id>/balances', methods=['GET'])
def get_balances(user_id):
    try:
        balances = WalletService.get_balances(user_id)
        return jsonify(balances), 200
        
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/wallets/<user_id>/transactions', methods=['GET'])
def get_transactions(user_id):
    try:
        limit = request.args.get('limit', 100, type=int)
        transactions = WalletService.get_transactions(user_id, limit)
        return jsonify({"transactions": transactions}), 200
        
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/wallets/<user_id>/reconcile', methods=['GET'])
def reconcile_balances(user_id):
    try:
        result = WalletService.reconcile_balances(user_id)
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/fx/rates', methods=['GET'])
def get_fx_rates():
    try:
        rates = FxService.get_all_rates()
        return jsonify({"rates": rates}), 200
        
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500

@bp.route('/fx/rates', methods=['PUT'])
def update_fx_rate():
    try:
        data = request.json
        from_currency = data.get('from_currency')
        to_currency = data.get('to_currency')
        rate = data.get('rate')
        
        if not all([from_currency, to_currency, rate]):
            return jsonify({"error": "Missing required fields"}), 400
        
        rate = Decimal(str(rate))
        FxService.update_rate(from_currency, to_currency, rate)
        
        return jsonify({
            "success": True,
            "message": f"Updated rate {from_currency}/{to_currency} to {rate}"
        }), 200
        
    except (ValueError, InvalidOperation) as e:
        return jsonify({"error": "Invalid rate value"}), 400
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500