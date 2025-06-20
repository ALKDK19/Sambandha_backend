
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b99da7df9f29'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('chats', sa.Column('state', sa.String(), nullable=False, server_default='request'))
    op.alter_column('chats', 'state', server_default=None)


def downgrade() -> None:
    op.drop_column('chats', 'state')