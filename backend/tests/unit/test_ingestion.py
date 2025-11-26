"""Unit tests for data ingestion service."""

from decimal import Decimal

import pytest

from app.services.ingestion import DataAnonymizer, DataIngestionService


class TestDataIngestionService:
    """Tests for DataIngestionService."""

    @pytest.fixture
    def service(self) -> DataIngestionService:
        """Create ingestion service instance."""
        return DataIngestionService()

    def test_parse_csv_valid(self, service: DataIngestionService) -> None:
        """Test parsing valid CSV data."""
        csv_content = """date,kwh
2024-01-01,950
2024-02-01,875
2024-03-01,920
"""
        records, result = service.parse_csv(csv_content)

        assert result.success is True
        assert result.records_processed == 3
        assert result.records_failed == 0
        assert len(records) == 3
        assert records[0].kwh_usage == Decimal("950")

    def test_parse_csv_alternative_columns(self, service: DataIngestionService) -> None:
        """Test parsing CSV with alternative column names."""
        csv_content = """month,consumption
2024-01-01,950
2024-02-01,875
"""
        records, result = service.parse_csv(csv_content)

        assert result.success is True
        assert len(records) == 2

    def test_parse_csv_with_errors(self, service: DataIngestionService) -> None:
        """Test parsing CSV with some invalid rows."""
        csv_content = """date,kwh
2024-01-01,950
invalid-date,875
2024-03-01,not-a-number
2024-04-01,920
"""
        records, result = service.parse_csv(csv_content)

        assert result.success is True
        assert result.records_processed == 2
        assert result.records_failed == 2
        assert len(result.errors) == 2

    def test_parse_csv_missing_columns(self, service: DataIngestionService) -> None:
        """Test parsing CSV with missing required columns."""
        csv_content = """name,value
test,100
"""
        records, result = service.parse_csv(csv_content)

        assert result.success is False
        assert "Could not find date column" in result.errors[0]

    def test_parse_json_valid(self, service: DataIngestionService) -> None:
        """Test parsing valid JSON data."""
        data = [
            {"date": "2024-01-01", "kwh": 950},
            {"usage_date": "2024-02-01", "kwh_usage": 875},
            {"month": "2024-03-01", "consumption": 920},
        ]
        records, result = service.parse_json(data)

        assert result.success is True
        assert result.records_processed == 3
        assert len(records) == 3

    def test_parse_json_with_numbers(self, service: DataIngestionService) -> None:
        """Test parsing JSON with numeric usage values."""
        data = [
            {"date": "2024-01-01", "kwh": 950.5},
            {"date": "2024-02-01", "kwh": 875},
        ]
        records, result = service.parse_json(data)

        assert result.success is True
        assert records[0].kwh_usage == Decimal("950.5")
        assert records[1].kwh_usage == Decimal("875")

    def test_data_quality_warnings_few_months(
        self, service: DataIngestionService
    ) -> None:
        """Test that warnings are generated for insufficient data."""
        csv_content = """date,kwh
2024-01-01,950
2024-02-01,875
"""
        records, result = service.parse_csv(csv_content)

        assert result.success is True
        assert len(result.warnings) > 0
        assert "months of data" in result.warnings[0].lower()


class TestDataAnonymizer:
    """Tests for DataAnonymizer."""

    def test_anonymize_customer_id_consistent(self) -> None:
        """Test that anonymization produces consistent results."""
        id1 = DataAnonymizer.anonymize_customer_id("customer-123")
        id2 = DataAnonymizer.anonymize_customer_id("customer-123")

        assert id1 == id2
        assert id1 != "customer-123"
        assert len(id1) == 16

    def test_anonymize_customer_id_different_inputs(self) -> None:
        """Test that different inputs produce different outputs."""
        id1 = DataAnonymizer.anonymize_customer_id("customer-123")
        id2 = DataAnonymizer.anonymize_customer_id("customer-456")

        assert id1 != id2

    def test_generate_synthetic_id(self) -> None:
        """Test synthetic ID generation."""
        id1 = DataAnonymizer.generate_synthetic_id()
        id2 = DataAnonymizer.generate_synthetic_id()

        assert id1.startswith("synth-")
        assert id2.startswith("synth-")
        assert id1 != id2
