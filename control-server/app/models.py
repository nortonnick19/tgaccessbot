from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    Text,
    Index,
)

from sqlalchemy.orm import relationship

from database import Base


# =====================================
# Servers
# =====================================

class Server(Base):

    __tablename__ = "servers"

    id = Column(
        Integer,
        primary_key=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    domain = Column(
        String(255),
        nullable=False,
        unique=True
    )

    ip = Column(
        String(45),
        nullable=False
    )

    active = Column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )


    access_requests = relationship(
        "AccessRequest",
        back_populates="server"
    )


    whitelist = relationship(
        "Whitelist",
        back_populates="server"
    )


    logs = relationship(
        "AuditLog",
        back_populates="server"
    )


# =====================================
# Telegram Users / Admins
# =====================================

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True
    )

    telegram_id = Column(
        String(50),
        unique=True,
        nullable=False
    )

    username = Column(
        String(100)
    )

    full_name = Column(
        String(200)
    )

    role = Column(
        String(50),
        default="ADMIN"
    )

    active = Column(
        Boolean,
        default=True
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# =====================================
# Access Requests
# =====================================

class AccessRequest(Base):

    __tablename__ = "access_requests"


    id = Column(
        Integer,
        primary_key=True
    )


    server_id = Column(
        Integer,
        ForeignKey(
            "servers.id"
        ),
        nullable=False
    )


    username = Column(
        String(100),
        nullable=False
    )


    source_ip = Column(
        String(45),
        nullable=False
    )


    event_type = Column(
        String(50),
        nullable=False
    )


    status = Column(
        String(30),
        default="WAITING"
    )


    reason = Column(
        Text
    )


    approved_by = Column(
        String(100)
    )


    approved_at = Column(
        DateTime
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


    server = relationship(
        "Server",
        back_populates="access_requests"
    )


Index(
    "idx_access_ip",
    AccessRequest.source_ip
)


Index(
    "idx_access_status",
    AccessRequest.status
)


# =====================================
# IP Whitelist
# =====================================

class Whitelist(Base):

    __tablename__ = "whitelist"


    id = Column(
        Integer,
        primary_key=True
    )


    server_id = Column(
        Integer,
        ForeignKey(
            "servers.id"
        ),
        nullable=False
    )


    ip = Column(
        String(45),
        nullable=False
    )


    username = Column(
        String(100)
    )


    permanent = Column(
        Boolean,
        default=False
    )


    expires_at = Column(
        DateTime
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


    server = relationship(
        "Server",
        back_populates="whitelist"
    )



# =====================================
# Audit Logs
# =====================================

class AuditLog(Base):

    __tablename__ = "audit_logs"


    id = Column(
        Integer,
        primary_key=True
    )


    server_id = Column(
        Integer,
        ForeignKey(
            "servers.id"
        )
    )


    action = Column(
        String(100),
        nullable=False
    )


    details = Column(
        Text
    )


    user = Column(
        String(100)
    )


    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


    server = relationship(
        "Server",
        back_populates="logs"
    )
