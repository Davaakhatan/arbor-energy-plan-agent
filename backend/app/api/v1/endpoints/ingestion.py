"""Data ingestion API endpoints."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.repositories.customer import CustomerRepository
from app.schemas.customer import CustomerCreate, CustomerResponse
from app.services.ingestion import DataAnonymizer, DataIngestionService, IngestionResult

router = APIRouter()


class CSVIngestionResponse(BaseModel):
    """Response for CSV ingestion."""

    customer: CustomerResponse
    ingestion_result: IngestionResult


class JSONIngestionRequest(BaseModel):
    """Request for JSON usage data ingestion."""

    external_id: str | None = None
    anonymize: bool = True
    usage_data: list[dict]


@router.post("/csv", response_model=CSVIngestionResponse)
async def ingest_csv(
    file: UploadFile = File(...),
    external_id: str | None = None,
    anonymize: bool = True,
    db: AsyncSession = Depends(get_db),
) -> CSVIngestionResponse:
    """Ingest customer usage data from CSV file.

    The CSV should contain columns for date and kWh usage.
    Supported column names:
    - Date: date, month, period, usage_date
    - Usage: kwh, usage, consumption, kwh_usage

    Example CSV:
    ```
    date,kwh
    2024-01-01,950
    2024-02-01,875
    ...
    ```
    """
    # Validate file type
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file",
        )

    # Read file content
    try:
        content = await file.read()
        csv_content = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be UTF-8 encoded",
        )

    # Parse CSV
    ingestion_service = DataIngestionService()
    usage_records, result = ingestion_service.parse_csv(csv_content)

    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Failed to parse CSV file",
                "errors": result.errors,
            },
        )

    # Generate or anonymize customer ID
    if external_id:
        if anonymize:
            customer_external_id = DataAnonymizer.anonymize_customer_id(external_id)
        else:
            customer_external_id = external_id
    else:
        customer_external_id = DataAnonymizer.generate_synthetic_id()

    # Create customer with usage data
    repo = CustomerRepository(db)

    # Check if customer already exists
    existing = await repo.get_by_external_id(customer_external_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Customer with external_id '{customer_external_id}' already exists. "
            "Use a different ID or delete the existing customer first.",
        )

    customer_data = CustomerCreate(
        external_id=customer_external_id,
        usage_data=usage_records,
    )
    customer = await repo.create(customer_data)

    return CSVIngestionResponse(
        customer=CustomerResponse.model_validate(customer),
        ingestion_result=result,
    )


@router.post("/json", response_model=CSVIngestionResponse)
async def ingest_json(
    request: JSONIngestionRequest,
    db: AsyncSession = Depends(get_db),
) -> CSVIngestionResponse:
    """Ingest customer usage data from JSON.

    Example request:
    ```json
    {
        "external_id": "customer-123",
        "anonymize": true,
        "usage_data": [
            {"date": "2024-01-01", "kwh": 950},
            {"date": "2024-02-01", "kwh": 875}
        ]
    }
    ```
    """
    # Parse JSON data
    ingestion_service = DataIngestionService()
    usage_records, result = ingestion_service.parse_json(request.usage_data)

    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Failed to parse usage data",
                "errors": result.errors,
            },
        )

    # Generate or anonymize customer ID
    if request.external_id:
        if request.anonymize:
            customer_external_id = DataAnonymizer.anonymize_customer_id(
                request.external_id
            )
        else:
            customer_external_id = request.external_id
    else:
        customer_external_id = DataAnonymizer.generate_synthetic_id()

    # Create customer with usage data
    repo = CustomerRepository(db)

    # Check if customer already exists
    existing = await repo.get_by_external_id(customer_external_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Customer with external_id '{customer_external_id}' already exists.",
        )

    customer_data = CustomerCreate(
        external_id=customer_external_id,
        usage_data=usage_records,
    )
    customer = await repo.create(customer_data)

    return CSVIngestionResponse(
        customer=CustomerResponse.model_validate(customer),
        ingestion_result=result,
    )
