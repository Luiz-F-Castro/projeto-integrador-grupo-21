# Modelo fisico do banco

Diagrama de relacionamento entre as entidades do Portal de Autoatendimento de TI,
conforme definido em `docs/planejamento/05-contratos-dados-e-telas.md`.

```mermaid
erDiagram
    USERS ||--o{ ARTICLE_FEEDBACK : envia
    ARTICLES ||--o{ ARTICLE_FEEDBACK : recebe
    USERS ||--o{ UNLOCK_REQUESTS : solicita
    USERS ||--o{ TICKETS : abre
    USERS ||--o{ TICKETS : atende
    TICKETS ||--o{ TICKET_EVENTS : possui
    USERS ||--o{ TICKET_EVENTS : registra
```

## Enums

- `user_role`: EMPLOYEE, TECHNICIAN
- `article_category`: ACCESS, SOFTWARE, NETWORK, HARDWARE, SECURITY
- `ticket_category`: ACCESS, SOFTWARE, NETWORK, HARDWARE, SECURITY, OTHER
- `ticket_priority`: LOW, MEDIUM, HIGH, CRITICAL
- `ticket_status`: OPEN, TRIAGE, IN_PROGRESS, RESOLVED
- `unlock_status`: PENDING, VERIFIED, EXPIRED, BLOCKED

O DDL completo esta em `database/schema.sql`. As migrations equivalentes ficam em
`backend/migrations/`, geradas via Alembic a partir dos models em `backend/app/models/`.