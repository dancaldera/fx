from __future__ import annotations
from app import create_app, db
from app.services import FxService

app = create_app()

with app.app_context():
    db.create_all()
    FxService.initialize_rates()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
