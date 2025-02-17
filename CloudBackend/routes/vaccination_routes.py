from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, extract
from typing import List

from core.database import get_db
from core import auth
from core.models.models import User, VaccinationType, VaccinationHistory
from core.models import schemas

router = APIRouter()

@router.get(
    "/history", response_model=schemas.VaccinationFullHistoryResponse
)
def get_vaccination_history(email: str, db: Session = Depends(get_db)):
    # First, verify the email exists in the users table
    user = db.query(User).filter(User.email == email).first()

    # If user not found, raise an HTTP exception
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User with this email not found",
        )

    # Prepare user info
    user_info = {
        "user_name": f"{user.first_name} {user.last_name}",
        "user_email": user.email,
    }

    # Get all vaccine types
    vaccine_types = db.query(VaccinationType).all()

    # Prepare vaccination history
    vaccination_history = []

    for vaccine_type in vaccine_types:
        # Fetch vaccination entries for this user and vaccine type
        existing_doses = (
            db.query(VaccinationHistory)
            .filter(
                and_(
                    VaccinationHistory.user_email == email,
                    VaccinationHistory.vaccine_type_id == vaccine_type.id,
                )
            )
            .order_by(VaccinationHistory.dose_number)
            .all()
        )

        # Create a complete dose list with existing entries and empty entries
        dose_data = []
        for i in range(1, vaccine_type.max_doses + 1):
            # Try to find an existing dose for this number
            existing_dose = next(
                (dose for dose in existing_doses if dose.dose_number == i), None
            )

            if existing_dose:
                # If dose exists, use its data
                dose_data.append(
                    {
                        "dose_number": existing_dose.dose_number,
                        "vaccination_date": existing_dose.vaccination_date,
                        "is_taken": existing_dose.is_taken,
                    }
                )
            else:
                # If no dose exists, create an empty entry
                dose_data.append(
                    {
                        "dose_number": i,
                        "vaccination_date": None,
                        "is_taken": False,
                    }
                )

        vaccination_history.append(
            {
                "vaccine_code": vaccine_type.vaccine_code,
                "vaccine_name": vaccine_type.vaccine_name,
                "doses": dose_data,
            }
        )

    # Return the full response structure
    return schemas.VaccinationFullHistoryResponse(
        user_info=schemas.UserInfoResponseNoLogin(
            user_name=f"{user.first_name} {user.last_name}",
            user_email=user.email
        ),
        vaccination_history=vaccination_history
    )
    
@router.post("/get-vaccination-history/by-jwt/", response_model=schemas.VaccinationFullHistoryResponse)
def get_vaccination_history_by_jwt(jwt: schemas.TokenInput, db: Session = Depends(get_db)):
    user_email = auth.get_current_user(token=jwt.token, db=db)
    user = db.query(User).filter(User.email == user_email).first()
    
    return get_vaccination_history(email=user.email, db=db)

@router.post("/vaccination-history")
def update_vaccination_history(
    payload: schemas.VaccinationEntryCreate,
    db: Session = Depends(get_db),
):
    # Verify vaccinator authentication and authorization
    try:
        current_user_email = auth.get_current_user(token=payload.token, db=db)
        
        print(current_user_email)
        
        current_user = db.query(User).filter(User.email == current_user_email).first()
        
        print(current_user.user_type)
        
        # Check if vaccinator has the required user group (group ID 2)
        if current_user.user_type != '2':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only authorized healthcare workers can update vaccination records",
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Authentication failed {e}"
        )

    # Check if recipient user exists
    recipient_user = (
        db.query(User).filter(User.email == payload.email).first()
    )

    if not recipient_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Recipient user not found"
        )

    # Find the vaccine type
    vaccine_type = (
        db.query(VaccinationType)
        .filter_by(vaccine_code=payload.vaccine_code)
        .first()
    )

    if not vaccine_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vaccine type not found"
        )

    # Check if dose number is valid
    if payload.dose_number < 1 or payload.dose_number > vaccine_type.max_doses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid dose number"
        )

    # Validate previous doses for this vaccine type
    if payload.dose_number > 1 and payload.is_taken:
        # Check all previous doses
        previous_doses = (
            db.query(VaccinationHistory)
            .filter(
                and_(
                    VaccinationHistory.user_email == payload.email,
                    VaccinationHistory.vaccine_type_id == vaccine_type.id,
                    VaccinationHistory.dose_number < payload.dose_number,
                )
            )
            .order_by(VaccinationHistory.dose_number)
            .all()
        )

        # If there are fewer previous doses than expected, or any previous dose is not taken
        if len(previous_doses) < payload.dose_number - 1 or any(
            not dose.is_taken for dose in previous_doses
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot add dose {payload.dose_number} before completing previous doses",
            )

    # Find existing entry or create new
    existing_entry = (
        db.query(VaccinationHistory)
        .filter(
            and_(
                VaccinationHistory.user_email == payload.email,
                VaccinationHistory.vaccine_type_id == vaccine_type.id,
                VaccinationHistory.dose_number == payload.dose_number,
            )
        )
        .first()
    )

    if existing_entry:
        # Update existing entry
        existing_entry.vaccination_date = payload.vaccination_date
        existing_entry.is_taken = payload.is_taken
    else:
        # Create new entry
        new_entry = VaccinationHistory(
            user_email=payload.email,
            vaccine_type_id=vaccine_type.id,
            dose_number=payload.dose_number,
            vaccination_date=payload.vaccination_date,
            is_taken=payload.is_taken,
        )
        db.add(new_entry)

    db.commit()
    db.refresh(existing_entry) if existing_entry else None

    return {"message": "Vaccination history updated successfully"}

@router.get("/stats")
def get_vaccination_stats(token: str, db: Session = Depends(get_db)):
    try:
        # Verify user and check if they're a healthcare worker (user_type = 2)
        current_user_email = auth.get_current_user(token=token, db=db)
        
        current_user = db.query(User).filter(User.email == current_user_email).first()
        
        if current_user.user_type != '2':
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only healthcare workers can access statistics"
            )

        # Get current year
        current_year = datetime.now().year

        # Query monthly vaccination counts
        monthly_stats = (
            db.query(
                extract('month', VaccinationHistory.vaccination_date).label('month'),
                func.count().label('count')
            )
            .filter(
                extract('year', VaccinationHistory.vaccination_date) == current_year,
                VaccinationHistory.is_taken == True
            )
            .group_by(extract('month', VaccinationHistory.vaccination_date))
            .all()
        )

        # Create a dictionary with all months initialized to 0
        monthly_data = {i: 0 for i in range(1, 13)}
        
        # Update with actual values
        for stat in monthly_stats:
            # Convert Decimal to int for month
            month_num = int(stat.month)
            monthly_data[month_num] = stat.count

        # Convert to list format with proper ordering
        monthly_data = [
            {"month": int(month), "vaccinations": count}
            for month, count in monthly_data.items()
        ]

        # Sort by month number to ensure correct ordering
        monthly_data.sort(key=lambda x: x["month"])

        # Query vaccine type distribution
        vaccine_stats = (
            db.query(
                VaccinationType.vaccine_name,
                func.count().label('count')
            )
            .join(VaccinationHistory)
            .filter(VaccinationHistory.is_taken == True)
            .group_by(VaccinationType.vaccine_name)
            .all()
        )

        vaccine_distribution = [
            {"name": stat.vaccine_name, "value": int(stat.count)}
            for stat in vaccine_stats
        ]

        return {
            "monthly_data": monthly_data,
            "vaccine_distribution": vaccine_distribution
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )