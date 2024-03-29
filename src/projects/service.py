from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.documents import service as doc_service
from src.logos.dependencies import get_logo_by_id
from src.models import ProjectUser
from src.projects import models as proj_models
from src.projects import schemas
from src.users.dependencies import get_user_by_username
from src.utils.aws.s3 import S3Client
from src.utils.logger.main import logger

s3 = S3Client()


def read_all(user_id: UUID, db: Session) -> list[schemas.Project]:
    proj_list_orm = (
        db.query(proj_models.Project)
        .join(ProjectUser)
        .filter(ProjectUser.user_id == user_id)
        .all()
    )
    return [schemas.Project.model_validate(proj) for proj in proj_list_orm]


def read(project: proj_models.Project) -> schemas.Project:
    return schemas.Project.model_validate(project)


def create(
    proj_create: schemas.ProjectCreate, user_id: UUID, db: Session
) -> schemas.Project:
    project = proj_models.Project(**proj_create.model_dump(), owner_id=user_id)
    db.add(project)
    db.commit()

    m2m_relationship = ProjectUser(user_id=user_id, project_id=project.id)
    db.add(m2m_relationship)
    db.commit()
    return schemas.Project.model_validate(project)


def update(
    project: proj_models.Project, proj_update: schemas.ProjectUpdate, db: Session
) -> schemas.Project:
    if proj_update.name is not None and proj_update.name != project.name:
        project.name = proj_update.name

    if (
        proj_update.description is not None
        and proj_update.description != project.description
    ):
        project.description = proj_update.description

    db.commit()
    return schemas.Project.model_validate(project)


def delete(project: proj_models.Project, owner_id: UUID, db: Session) -> None:
    if project.owner_id != owner_id:
        log_msg = "Current User: %s - IS NOT OWNER - Owner: %s"
        logger.error(log_msg, owner_id, project.owner_id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner can delete a project",
        )

    if project.documents:
        for document in project.documents:
            doc_service.delete(document, owner_id, project.owner_id, db)

    if project.logo_id:
        logo = get_logo_by_id(project.id, db)
        s3.delete(f"{project.id}_{logo.name}", "resized_logos")

    db.delete(project)
    db.commit()


def invite(
    project: proj_models.Project, username: str, owner_id: UUID, db: Session
) -> None:
    if project.owner_id != owner_id:
        log_msg = "Current User: %s - IS NOT OWNER - Owner: %s"
        logger.error(log_msg, owner_id, project.owner_id)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only project owner can invite to project",
        )

    user_to_invite = get_user_by_username(username, db)

    m2m_relationship = ProjectUser(user_id=user_to_invite.id, project_id=project.id)
    db.add(m2m_relationship)
    db.commit()
