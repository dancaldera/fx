from __future__ import annotations
from app import db
from app.models import Wallet, Transaction, FxRate, TransactionType
from decimal import Decimal, ROUND_DOWN
from typing import Dict, List, Any

class WalletService:

    @staticmethod
    def get_or_create_wallet(user_id: str, currency: str) -> Wallet:
        wallet = Wallet.query.filter_by(user_id=user_id, currency=currency).first()
        if not wallet:
            wallet = Wallet(user_id=user_id, currency=currency, balance=Decimal('0'))
            db.session.add(wallet)
            db.session.commit()
        return wallet

    @staticmethod
    def fund_wallet(user_id: str, currency: str, amount: Decimal) -> Dict[str, Any]:
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")

        wallet = WalletService.get_or_create_wallet(user_id, currency)
        wallet.balance += amount

        transaction = Transaction(
            user_id=user_id,
            transaction_type=TransactionType.FUND,
            currency=currency,
            amount=amount
        )

        db.session.add(transaction)
        db.session.commit()

        return {
            "success": True,
            "message": f"Funded {amount} {currency}",
            "balance": wallet.balance
        }

    @staticmethod
    def withdraw_funds(user_id: str, currency: str, amount: Decimal) -> Dict[str, Any]:
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")

        wallet = WalletService.get_or_create_wallet(user_id, currency)

        if wallet.balance < amount:
            raise ValueError("Insufficient funds")

        wallet.balance -= amount

        transaction = Transaction(
            user_id=user_id,
            transaction_type=TransactionType.WITHDRAW,
            currency=currency,
            amount=amount
        )

        db.session.add(transaction)
        db.session.commit()

        return {
            "success": True,
            "message": f"Withdrew {amount} {currency}",
            "balance": wallet.balance
        }

    @staticmethod
    def convert_currency(user_id: str, from_currency: str, to_currency: str, amount: Decimal) -> Dict[str, Any]:
        if amount <= 0:
            raise ValueError("Amount must be greater than 0")

        if from_currency == to_currency:
            raise ValueError("Cannot convert to the same currency")

        from_wallet = WalletService.get_or_create_wallet(user_id, from_currency)
        to_wallet = WalletService.get_or_create_wallet(user_id, to_currency)

        if from_wallet.balance < amount:
            raise ValueError("Insufficient funds")

        fx_rate = FxService.get_rate(from_currency, to_currency)
        converted_amount = (amount * fx_rate).quantize(Decimal('0.00000001'), rounding=ROUND_DOWN)

        from_wallet.balance -= amount
        to_wallet.balance += converted_amount

        out_transaction = Transaction(
            user_id=user_id,
            transaction_type=TransactionType.CONVERT_OUT,
            currency=from_currency,
            amount=amount,
            from_currency=from_currency,
            to_currency=to_currency,
            fx_rate=fx_rate
        )

        in_transaction = Transaction(
            user_id=user_id,
            transaction_type=TransactionType.CONVERT_IN,
            currency=to_currency,
            amount=converted_amount,
            from_currency=from_currency,
            to_currency=to_currency,
            fx_rate=fx_rate
        )

        db.session.add(out_transaction)
        db.session.add(in_transaction)
        db.session.commit()

        return {
            "success": True,
            "message": f"Converted {amount} {from_currency} to {converted_amount} {to_currency}",
            "fx_rate": fx_rate,
            "converted_amount": converted_amount
        }

    @staticmethod
    def get_balances(user_id: str) -> Dict[str, float]:
        wallets = Wallet.query.filter_by(user_id=user_id).all()
        balances: Dict[str, float] = {}

        for wallet in wallets:
            if wallet.balance > 0:
                balances[wallet.currency] = float(wallet.balance)

        return balances

    @staticmethod
    def get_transactions(user_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        transactions = Transaction.query.filter_by(user_id=user_id)\
            .order_by(Transaction.created_at.desc())\
            .limit(limit)\
            .all()

        result: List[Dict[str, Any]] = []
        for txn in transactions:
            result.append({
                "id": txn.id,
                "type": txn.transaction_type.value,
                "currency": txn.currency,
                "amount": float(txn.amount),
                "from_currency": txn.from_currency,
                "to_currency": txn.to_currency,
                "fx_rate": float(txn.fx_rate) if txn.fx_rate else None,
                "timestamp": txn.created_at.isoformat()
            })

        return result

    @staticmethod
    def reconcile_balances(user_id: str) -> Dict[str, Any]:
        transactions = Transaction.query.filter_by(user_id=user_id).all()
        calculated_balances: Dict[str, Decimal] = {}

        for txn in transactions:
            currency = txn.currency
            if currency not in calculated_balances:
                calculated_balances[currency] = Decimal('0')

            if txn.transaction_type == TransactionType.FUND:
                calculated_balances[currency] += txn.amount
            elif txn.transaction_type == TransactionType.WITHDRAW:
                calculated_balances[currency] -= txn.amount
            elif txn.transaction_type == TransactionType.CONVERT_IN:
                calculated_balances[currency] += txn.amount
            elif txn.transaction_type == TransactionType.CONVERT_OUT:
                calculated_balances[currency] -= txn.amount

        actual_balances: Dict[str, Decimal] = {}
        wallets = Wallet.query.filter_by(user_id=user_id).all()
        for wallet in wallets:
            actual_balances[wallet.currency] = wallet.balance

        discrepancies: Dict[str, Dict[str, float]] = {}
        all_currencies = set(calculated_balances.keys()) | set(actual_balances.keys())

        for currency in all_currencies:
            calculated = calculated_balances.get(currency, Decimal('0'))
            actual = actual_balances.get(currency, Decimal('0'))
            if calculated != actual:
                discrepancies[currency] = {
                    "calculated": float(calculated),
                    "actual": float(actual),
                    "difference": float(actual - calculated)
                }

        return {
            "reconciled": len(discrepancies) == 0,
            "discrepancies": discrepancies
        }

class FxService:

    @staticmethod
    def initialize_rates() -> None:
        rates = [
            ("USD", "MXN", Decimal('18.70')),
            ("MXN", "USD", Decimal('0.053')),
        ]

        for from_curr, to_curr, rate in rates:
            existing = FxRate.query.filter_by(from_currency=from_curr, to_currency=to_curr).first()
            if not existing:
                fx_rate = FxRate(from_currency=from_curr, to_currency=to_curr, rate=rate)
                db.session.add(fx_rate)

        db.session.commit()

    @staticmethod
    def get_rate(from_currency: str, to_currency: str) -> Decimal:
        if from_currency == to_currency:
            return Decimal('1')

        fx_rate = FxRate.query.filter_by(from_currency=from_currency, to_currency=to_currency).first()
        if not fx_rate:
            raise ValueError(f"FX rate not found for {from_currency} to {to_currency}")

        return fx_rate.rate

    @staticmethod
    def update_rate(from_currency: str, to_currency: str, rate: Decimal) -> FxRate:
        fx_rate = FxRate.query.filter_by(from_currency=from_currency, to_currency=to_currency).first()
        if fx_rate:
            fx_rate.rate = rate
        else:
            fx_rate = FxRate(from_currency=from_currency, to_currency=to_currency, rate=rate)
            db.session.add(fx_rate)

        db.session.commit()
        return fx_rate

    @staticmethod
    def get_all_rates() -> Dict[str, Dict[str, Any]]:
        rates = FxRate.query.all()
        result: Dict[str, Dict[str, Any]] = {}
        for rate in rates:
            pair = f"{rate.from_currency}/{rate.to_currency}"
            result[pair] = {
                "rate": float(rate.rate),
                "updated_at": rate.created_at.isoformat()
            }
        return result
