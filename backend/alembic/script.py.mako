"""${message}"""

revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    """TODO: Add upgrade migration steps."""
    pass


def downgrade() -> None:
    """TODO: Add downgrade migration steps."""
    pass
