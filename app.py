from __future__ import annotations
from app import create_app
from app.services import FxService

app = create_app()

with app.app_context():
    # Database tables are now managed by migrations
    # Run: flask db upgrade
    # Initialize default FX rates if they don't exist
    FxService.initialize_rates()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
