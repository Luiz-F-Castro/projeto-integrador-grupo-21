import uuid
from datetime import date, datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.enums import TicketCategory, TicketPriority, TicketStatus, UserRole
from app.models.ticket import Ticket, TicketEvent
from app.models.user import User

VALID_TRANSITIONS = {
    TicketStatus.OPEN: {TicketStatus.TRIAGE},
    TicketStatus.TRIAGE: {TicketStatus.IN_PROGRESS, TicketStatus.OPEN},
    TicketStatus.IN_PROGRESS: {TicketStatus.RESOLVED, TicketStatus.OPEN},
    TicketStatus.RESOLVED: set(),
}

HIGH_PRIORITY_CATEGORIES = {TicketCategory.NETWORK, TicketCategory.SECURITY}


def _initial_priority(category: TicketCategory) -> TicketPriority:
    return TicketPriority.HIGH if category in HIGH_PRIORITY_CATEGORIES else TicketPriority.MEDIUM


def _generate_protocol(db: Session) -> str:
    year = datetime.now(timezone.utc).year
    count_this_year = (
        db.query(func.count(Ticket.id))
        .filter(Ticket.created_at >= date(year, 1, 1))
        .scalar()
        or 0
    )
    return f"INC-{year}-{count_this_year + 1:04d}"


def create_ticket(db: Session, requester: User, title: str, description: str, category: TicketCategory) -> Ticket:
    ticket = Ticket(
        protocol=_generate_protocol(db),
        requester_id=requester.id,
        title=title,
        description=description,
        category=category,
        priority=_initial_priority(category),
        status=TicketStatus.OPEN,
    )
    db.add(ticket)
    db.flush()

    event = TicketEvent(
        ticket_id=ticket.id,
        author_id=requester.id,
        from_status=None,
        to_status=TicketStatus.OPEN,
        comment="Chamado aberto",
    )
    db.add(event)
    db.commit()
    db.refresh(ticket)
    return ticket


def list_tickets(db: Session, user: User, status_filter: TicketStatus | None, priority_filter: TicketPriority | None):
    stmt = db.query(Ticket)

    if user.role == UserRole.EMPLOYEE:
        stmt = stmt.filter(Ticket.requester_id == user.id)

    if status_filter:
        stmt = stmt.filter(Ticket.status == status_filter)

    if priority_filter:
        stmt = stmt.filter(Ticket.priority == priority_filter)

    return stmt.order_by(Ticket.created_at.desc()).all()


def get_ticket_for_user(db: Session, ticket_id: uuid.UUID, user: User) -> Ticket:
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()

    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chamado nao encontrado")

    if user.role == UserRole.EMPLOYEE and ticket.requester_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chamado nao encontrado")

    return ticket


def assign_ticket(db: Session, ticket_id: uuid.UUID, assignee_id: uuid.UUID, actor: User) -> Ticket:
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chamado nao encontrado")

    ticket.assignee_id = assignee_id
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def update_priority(db: Session, ticket_id: uuid.UUID, priority: TicketPriority) -> Ticket:
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chamado nao encontrado")

    ticket.priority = priority
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def update_status(
    db: Session, ticket_id: uuid.UUID, new_status: TicketStatus, comment: str | None, actor: User
) -> Ticket:
    ticket = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chamado nao encontrado")

    if ticket.status == TicketStatus.RESOLVED:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Chamado resolvido nao pode ser alterado")

    if new_status not in VALID_TRANSITIONS.get(ticket.status, set()):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Transicao de status invalida")

    previous_status = ticket.status
    ticket.status = new_status
    if new_status == TicketStatus.RESOLVED:
        ticket.resolved_at = datetime.now(timezone.utc)

    event = TicketEvent(
        ticket_id=ticket.id,
        author_id=actor.id,
        from_status=previous_status,
        to_status=new_status,
        comment=comment,
    )
    db.add_all([ticket, event])
    db.commit()
    db.refresh(ticket)
    return ticket


def employee_dashboard(db: Session, user: User) -> dict:
    base = db.query(Ticket).filter(Ticket.requester_id == user.id)
    return {
        "account_locked": user.account_locked,
        "open_tickets": base.filter(Ticket.status == TicketStatus.OPEN).count(),
        "in_progress_tickets": base.filter(
            Ticket.status.in_([TicketStatus.TRIAGE, TicketStatus.IN_PROGRESS])
        ).count(),
        "resolved_tickets": base.filter(Ticket.status == TicketStatus.RESOLVED).count(),
    }


def technician_dashboard(db: Session) -> dict:
    unassigned = db.query(Ticket).filter(Ticket.assignee_id.is_(None)).count()
    by_status = {
        status_value.value: db.query(Ticket).filter(Ticket.status == status_value).count()
        for status_value in TicketStatus
    }
    by_priority = {
        priority_value.value: db.query(Ticket).filter(Ticket.priority == priority_value).count()
        for priority_value in TicketPriority
    }
    return {
        "unassigned_tickets": unassigned,
        "by_status": by_status,
        "by_priority": by_priority,
    }