import os
os.environ.setdefault('JWT_SECRET_KEY', 'test-secret')
os.environ['DATABASE_URL'] = 'sqlite://'  # in-memory database

import pytest
from backend.app import create_app
from backend.database.db import db
from backend.database.models import User


@pytest.fixture()
def app(monkeypatch):
    def fake_analyze(text):
        negative = 'bad' in text or 'disappoint' in text
        return {'sentiment': 'negative' if negative else 'positive',
                'emotion': 'sadness' if negative else 'joy', 'confidence': 0.9}
    monkeypatch.setattr('backend.services.review_service.analyze_text', fake_analyze)
    app = create_app()
    with app.app_context():
        user = User(username='admin')
        user.set_password('test-password-123')
        db.session.add(user)
        db.session.commit()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def auth(client):
    res = client.post('/api/auth/login', json={'username': 'admin', 'password': 'test-password-123'})
    return {'Authorization': 'Bearer ' + res.get_json()['access_token']}
