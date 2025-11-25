"""Data ingestion service for customer usage and plan data."""

import csv
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from io import StringIO
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from app.core.logging import get_logger
from app.models.customer import Customer, CustomerUsage
from app.schemas.customer import CustomerUsageCreate

logger = get_logger(__name__)


class UsageDataRow(BaseModel):
    """Validated usage data row from CSV or API."""

    usage_date: date
    kwh_usage: Decimal = Field(ge=0)

    @field_validator("usage_date", mode="before")
    @classmethod
    def parse_date(cls, v: Any) -> date:
        """Parse date from various formats."""
        if isinstance(v, date):
            return v
        if isinstance(v, datetime):
            return v.date()
        if isinstance(v, str):
            # Try common date formats
            for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"]:
                try:
                    return datetime.strptime(v, fmt).date()
                except ValueError:
                    continue
            raise ValueError(f"Unable to parse date: {v}")
        raise ValueError(f"Invalid date type: {type(v)}")

    @field_validator("kwh_usage", mode="before")
    @classmethod
    def parse_kwh(cls, v: Any) -> Decimal:
        """Parse kWh usage from various formats."""
        if isinstance(v, Decimal):
            return v
        if isinstance(v, (int, float)):
            return Decimal(str(v))
        if isinstance(v, str):
            # Remove commas and whitespace
            cleaned = v.replace(",", "").strip()
            try:
                return Decimal(cleaned)
            except InvalidOperation:
                raise ValueError(f"Unable to parse kWh usage: {v}")
        raise ValueError(f"Invalid kWh type: {type(v)}")


class IngestionResult(BaseModel):
    """Result of data ingestion operation."""

    success: bool
    records_processed: int
    records_failed: int
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


class DataIngestionService:
    """Service for ingesting customer usage data from various sources."""

    def parse_csv(
        self,
        csv_content: str,
        date_column: str = "date",
        usage_column: str = "kwh",
    ) -> tuple[list[CustomerUsageCreate], IngestionResult]:
        """Parse usage data from CSV content.

        Args:
            csv_content: Raw CSV string content
            date_column: Name of the date column
            usage_column: Name of the kWh usage column

        Returns:
            Tuple of (parsed usage records, ingestion result)
        """
        usage_records: list[CustomerUsageCreate] = []
        errors: list[str] = []
        warnings: list[str] = []

        try:
            reader = csv.DictReader(StringIO(csv_content))

            # Validate columns exist
            if reader.fieldnames is None:
                return [], IngestionResult(
                    success=False,
                    records_processed=0,
                    records_failed=0,
                    errors=["CSV file appears to be empty or invalid"],
                )

            fieldnames = [f.lower().strip() for f in reader.fieldnames]
            date_col = self._find_column(fieldnames, date_column, ["date", "month", "period"])
            usage_col = self._find_column(fieldnames, usage_column, ["kwh", "usage", "consumption", "kwh_usage"])

            if date_col is None:
                errors.append(f"Could not find date column. Expected: {date_column}")
            if usage_col is None:
                errors.append(f"Could not find usage column. Expected: {usage_column}")

            if errors:
                return [], IngestionResult(
                    success=False,
                    records_processed=0,
                    records_failed=0,
                    errors=errors,
                )

            # Parse rows
            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is 1)
                try:
                    # Get values using case-insensitive matching
                    row_lower = {k.lower().strip(): v for k, v in row.items()}
                    date_val = row_lower.get(date_col, "")
                    usage_val = row_lower.get(usage_col, "")

                    if not date_val or not usage_val:
                        errors.append(f"Row {row_num}: Missing required values")
                        continue

                    # Validate and parse
                    validated = UsageDataRow(
                        usage_date=date_val,
                        kwh_usage=usage_val,
                    )

                    usage_records.append(
                        CustomerUsageCreate(
                            usage_date=validated.usage_date,
                            kwh_usage=validated.kwh_usage,
                        )
                    )

                except ValueError as e:
                    errors.append(f"Row {row_num}: {str(e)}")

        except csv.Error as e:
            return [], IngestionResult(
                success=False,
                records_processed=0,
                records_failed=0,
                errors=[f"CSV parsing error: {str(e)}"],
            )

        # Validate data quality
        if usage_records:
            quality_warnings = self._validate_data_quality(usage_records)
            warnings.extend(quality_warnings)

        result = IngestionResult(
            success=len(usage_records) > 0,
            records_processed=len(usage_records),
            records_failed=len(errors),
            errors=errors[:10],  # Limit to first 10 errors
            warnings=warnings,
        )

        return usage_records, result

    def parse_json(
        self,
        data: list[dict[str, Any]],
    ) -> tuple[list[CustomerUsageCreate], IngestionResult]:
        """Parse usage data from JSON/dict format.

        Args:
            data: List of dictionaries with usage data

        Returns:
            Tuple of (parsed usage records, ingestion result)
        """
        usage_records: list[CustomerUsageCreate] = []
        errors: list[str] = []
        warnings: list[str] = []

        for idx, item in enumerate(data):
            try:
                # Try common field names
                date_val = (
                    item.get("usage_date")
                    or item.get("date")
                    or item.get("month")
                    or item.get("period")
                )
                usage_val = (
                    item.get("kwh_usage")
                    or item.get("kwh")
                    or item.get("usage")
                    or item.get("consumption")
                )

                if date_val is None or usage_val is None:
                    errors.append(f"Item {idx}: Missing required fields")
                    continue

                validated = UsageDataRow(
                    usage_date=date_val,
                    kwh_usage=usage_val,
                )

                usage_records.append(
                    CustomerUsageCreate(
                        usage_date=validated.usage_date,
                        kwh_usage=validated.kwh_usage,
                    )
                )

            except ValueError as e:
                errors.append(f"Item {idx}: {str(e)}")

        # Validate data quality
        if usage_records:
            quality_warnings = self._validate_data_quality(usage_records)
            warnings.extend(quality_warnings)

        result = IngestionResult(
            success=len(usage_records) > 0,
            records_processed=len(usage_records),
            records_failed=len(errors),
            errors=errors[:10],
            warnings=warnings,
        )

        return usage_records, result

    def _find_column(
        self,
        fieldnames: list[str],
        preferred: str,
        alternatives: list[str],
    ) -> str | None:
        """Find a column name from possible alternatives."""
        preferred_lower = preferred.lower()
        if preferred_lower in fieldnames:
            return preferred_lower

        for alt in alternatives:
            alt_lower = alt.lower()
            if alt_lower in fieldnames:
                return alt_lower

        return None

    def _validate_data_quality(
        self,
        records: list[CustomerUsageCreate],
    ) -> list[str]:
        """Validate data quality and return warnings."""
        warnings: list[str] = []

        if len(records) < 3:
            warnings.append(
                f"Only {len(records)} months of data provided. "
                "Minimum 3 months required, 12 months recommended."
            )
        elif len(records) < 12:
            warnings.append(
                f"Only {len(records)} months of data provided. "
                "12 months recommended for accurate projections."
            )

        # Check for gaps in dates
        sorted_records = sorted(records, key=lambda r: r.usage_date)
        for i in range(1, len(sorted_records)):
            prev_date = sorted_records[i - 1].usage_date
            curr_date = sorted_records[i].usage_date

            # Calculate month difference
            month_diff = (curr_date.year - prev_date.year) * 12 + (
                curr_date.month - prev_date.month
            )
            if month_diff > 1:
                warnings.append(
                    f"Gap detected between {prev_date} and {curr_date}. "
                    "Missing data may affect projection accuracy."
                )

        # Check for unusually high or low values
        usage_values = [r.kwh_usage for r in records]
        avg_usage = sum(usage_values) / len(usage_values)

        for record in records:
            if record.kwh_usage > avg_usage * 3:
                warnings.append(
                    f"Unusually high usage on {record.usage_date}: "
                    f"{record.kwh_usage} kWh (3x average)"
                )
            elif record.kwh_usage < avg_usage * 0.2 and record.kwh_usage > 0:
                warnings.append(
                    f"Unusually low usage on {record.usage_date}: "
                    f"{record.kwh_usage} kWh (5x below average)"
                )

        return warnings[:5]  # Limit warnings


class DataAnonymizer:
    """Service for anonymizing customer data for GDPR compliance."""

    @staticmethod
    def anonymize_customer_id(external_id: str) -> str:
        """Generate anonymized customer identifier.

        Uses a one-way hash to create a consistent but non-reversible ID.
        """
        import hashlib

        # Add a salt for additional security
        salt = "arbor-energy-salt-2025"
        combined = f"{salt}:{external_id}"
        return hashlib.sha256(combined.encode()).hexdigest()[:16]

    @staticmethod
    def generate_synthetic_id() -> str:
        """Generate a random synthetic customer ID."""
        import secrets
        return f"synth-{secrets.token_hex(8)}"
