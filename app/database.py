from datetime import datetime

from sqlalchemy import (
    create_engine,
    String,
    Integer,
    Float,
    Text,
    DateTime,
    ForeignKey,
    select,
)

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    selectinload,
    relationship,
    sessionmaker,
)

from .config import DATABASE_URL


connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }


engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


class Base(DeclarativeBase):
    pass


class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True
    )

    username: Mapped[str] = mapped_column(
        String(120)
    )

    age: Mapped[int] = mapped_column(
        Integer
    )

    weight: Mapped[float] = mapped_column(
        Float
    )

    goal: Mapped[str] = mapped_column(
        String(100)
    )

    intensity: Mapped[str] = mapped_column(
        String(30)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    plans: Mapped[list["Plan"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Plan(Base):

    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True
    )

    original_plan: Mapped[str] = mapped_column(
        Text
    )

    nutrition_tip: Mapped[str] = mapped_column(
        Text
    )

    updated_plan: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    feedback: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    user: Mapped[User] = relationship(
        back_populates="plans"
    )


def init_db():

    Base.metadata.create_all(
        bind=engine
    )


def save_user(data):

    with SessionLocal() as db:

        user = db.scalar(
            select(User).where(
                User.user_id == data.user_id
            )
        )

        if user:

            user.username = data.username
            user.age = data.age
            user.weight = data.weight
            user.goal = data.goal
            user.intensity = data.intensity

        else:

            user = User(
                user_id=data.user_id,
                username=data.username,
                age=data.age,
                weight=data.weight,
                goal=data.goal,
                intensity=data.intensity
            )

            db.add(user)

        db.commit()

        db.refresh(user)

        return user.id


def save_plan(
    user_pk,
    original_plan,
    nutrition_tip
):

    with SessionLocal() as db:

        plan = Plan(
            user_id=user_pk,
            original_plan=original_plan,
            nutrition_tip=nutrition_tip
        )

        db.add(plan)

        db.commit()

        db.refresh(plan)

        return plan.id


def get_user(user_id):

    with SessionLocal() as db:

        return db.scalar(
            select(User).where(
                User.user_id == user_id
            )
        )


def get_latest_plan(user_id):

    with SessionLocal() as db:

        return db.scalar(
            select(Plan)
            .join(User)
            .where(User.user_id == user_id)
            .order_by(Plan.id.desc())
        )


def update_plan(
    plan_id,
    updated_plan,
    feedback
):

    with SessionLocal() as db:

        plan = db.get(
            Plan,
            plan_id
        )

        if not plan:
            return None

        plan.updated_plan = updated_plan
        plan.feedback = feedback
        plan.updated_at = datetime.utcnow()

        db.commit()

        db.refresh(plan)

        return plan


def get_all_users():

    with SessionLocal() as db:

        return db.scalars(
            select(User)
            .options(selectinload(User.plans))
            .order_by(User.id.desc())
        ).all()