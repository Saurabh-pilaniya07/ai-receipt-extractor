import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.main import app
from backend.api import routes
from backend.models.database import Base, get_db


TEST_DATABASE_URL = "sqlite://"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
)


@pytest.fixture(autouse=True)
def test_database():
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_upload_receipt(monkeypatch):
    def mock_extract_receipt(file_path):
        from backend.schemas.receipt import LineItem, ReceiptExtraction

        return ReceiptExtraction(
            merchant_name="TEST STORE",
            date="2026-09-14",
            line_items=[
                LineItem(item_name="Coffee", price=5.00),
                LineItem(item_name="Sandwich", price=10.00),
            ],
            total_amount=15.00,
            tax=1.00,
            tip=None,
        )

    monkeypatch.setattr(
        routes,
        "extract_receipt",
        mock_extract_receipt,
    )

    response = client.post(
        "/upload",
        files={
            "file": (
                "test_receipt.jpg",
                b"fake image content",
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["filename"] == "test_receipt.jpg"
    assert data["merchant_name"] == "TEST STORE"
    assert data["date"] == "2026-09-14"
    assert data["total_amount"] == 15.00
    assert data["category"] == "Food"
    assert len(data["line_items"]) == 2
    assert data["tax"] == 1.00
    assert data["tip"] is None


def test_reject_unsupported_file_type():
    response = client.post(
        "/upload",
        files={
            "file": (
                "test.txt",
                b"unsupported content",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400


def test_get_receipts():
    response = client.get("/receipts")

    assert response.status_code == 200
    assert isinstance(response.json(), list)