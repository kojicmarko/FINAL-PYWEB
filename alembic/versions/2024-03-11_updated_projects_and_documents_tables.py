"""updated projects and documents tables

Revision ID: f4541e89938b
Revises: 07ffc299dbad
Create Date: 2024-03-11 14:44:40.749399

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f4541e89938b"
down_revision: Union[str, None] = "07ffc299dbad"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("documents_project_id_fkey", "documents", type_="foreignkey")
    op.create_foreign_key(
        None, "documents", "projects", ["project_id"], ["id"], ondelete="CASCADE"
    )
    op.drop_constraint("projects_logo_id_fkey", "projects", type_="foreignkey")
    op.create_foreign_key(
        None, "projects", "logos", ["logo_id"], ["id"], ondelete="SET NULL"
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "projects", type_="foreignkey")
    op.create_foreign_key(
        "projects_logo_id_fkey", "projects", "logos", ["logo_id"], ["id"]
    )
    op.drop_constraint(None, "documents", type_="foreignkey")
    op.create_foreign_key(
        "documents_project_id_fkey", "documents", "projects", ["project_id"], ["id"]
    )
    # ### end Alembic commands ###
