from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from app.database import get_db
from app.models import Complaint, Status
from app.schemas import ComplaintCreate, ComplaintOut, StatusUpdate
from app.services.triage_service import run_triage
from app.services.state_machine import validate_transition

router = APIRouter(prefix="/api/complaints", tags=["complaints"])


@router.post("", response_model=ComplaintOut, status_code=201)
def create_complaint(payload: ComplaintCreate, db: Session = Depends(get_db)):
    category, priority, summary, provider, latency_ms = run_triage(payload.text, payload.location)

    complaint = Complaint(
        text=payload.text,
        location=payload.location,
        reporter_contact=payload.reporter_contact,
        category=category,
        priority=priority,
        ai_summary=summary,
        triaged_by=provider,
        triage_latency_ms=latency_ms,
    )
    db.add(complaint)
    db.commit()
    db.refresh(complaint)
    return complaint


@router.get("", response_model=list[ComplaintOut])
def list_complaints(
    category: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    query = db.query(Complaint)
    if category:
        query = query.filter(Complaint.category == category)
    if priority:
        query = query.filter(Complaint.priority == priority)
    if status:
        query = query.filter(Complaint.status == status)

    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return items


@router.get("/{complaint_id}", response_model=ComplaintOut)
def get_complaint(complaint_id: UUID, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return complaint


@router.patch("/{complaint_id}/status", response_model=ComplaintOut)
def update_status(complaint_id: UUID, payload: StatusUpdate, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    if not validate_transition(complaint.status, payload.status):
        raise HTTPException(
            status_code=409,
            detail=f"Invalid transition from {complaint.status} to {payload.status}",
        )

    complaint.status = payload.status
    db.commit()
    db.refresh(complaint)
    return complaint