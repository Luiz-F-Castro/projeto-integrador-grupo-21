import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_employee, require_technician
from app.db.session import get_db
from app.models.enums import TicketPriority, TicketStatus
from app.schemas.ticket import (
    TicketAssignmentUpdate,
    TicketCreate,
    TicketDetail,
    TicketPriorityUpdate,
    TicketStatusUpdate,
    TicketSummary,
    UserRef,
)
from app.services.ticket_service import (
    assign_ticket,
    create_ticket,
    get_ticket_for_user,
    list_tickets,
    update_priority,
    update_status,
)

router = APIRouter(prefix="/api/v1/tickets", tags=["chamados"])


def _to_summary(ticket) -> TicketSummary:
    return TicketSummary(
        id=ticket.id,
        protocol=ticket.protocol,
        title=ticket.title,
        category=ticket.category,
        priority=ticket.priority,
        status=ticket.status,
        requester=UserRef(id=ticket.requester_id, name=""),
        assignee=UserRef(id=ticket.assignee_id, name="") if ticket.assignee_id else None,
        created_at=ticket.created_at,
        updated_at=ticket.updated_at,
    )


def _to_detail(ticket) -> TicketDetail:
    summary = _to_summary(ticket)
    return TicketDetail(**summary.model_dump(), description=ticket.description, events=[])


@router.post("", response_model=TicketDetail)
def open_ticket(
    payload: TicketCreate, db: Session = Depends(get_db), current_user=Depends(require_employee)
) -> TicketDetail:
    ticket = create_ticket(db, current_user, payload.title, payload.description, payload.category)
    return _to_detail(ticket)


@router.get("", response_model=list[TicketSummary])
def get_tickets(
    status_filter: TicketStatus | None = None,
    priority_filter: TicketPriority | None = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
) -> list[TicketSummary]:
    tickets = list_tickets(db, current_user, status_filter, priority_filter)
    return [_to_summary(ticket) for ticket in tickets]


@router.get("/{ticket_id}", response_model=TicketDetail)
def get_ticket(
    ticket_id: uuid.UUID, db: Session = Depends(get_db), current_user=Depends(get_current_user)
) -> TicketDetail:
    ticket = get_ticket_for_user(db, ticket_id, current_user)
    return _to_detail(ticket)


@router.patch("/{ticket_id}/assignment", response_model=TicketDetail)
def patch_assignment(
    ticket_id: uuid.UUID,
    payload: TicketAssignmentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_technician),
) -> TicketDetail:
    ticket = assign_ticket(db, ticket_id, payload.assignee_id, current_user)
    return _to_detail(ticket)


@router.patch("/{ticket_id}/priority", response_model=TicketDetail)
def patch_priority(
    ticket_id: uuid.UUID,
    payload: TicketPriorityUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_technician),
) -> TicketDetail:
    ticket = update_priority(db, ticket_id, payload.priority)
    return _to_detail(ticket)


@router.patch("/{ticket_id}/status", response_model=TicketDetail)
def patch_status(
    ticket_id: uuid.UUID,
    payload: TicketStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_technician),
) -> TicketDetail:
    ticket = update_status(db, ticket_id, payload.status, payload.comment, current_user)
    return _to_detail(ticket)