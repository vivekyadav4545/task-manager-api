from fastapi import APIRouter , Depends , status , HTTPException  
from sqlalchemy.orm import session
from typing import List

from database import get_db 
import schemas 
import models
from users import get_current_user

router = APIRouter(prefix="/tasks" , tags=["tasks"])

@router.post("/" , response_model=schemas.TaskResponse , status_code=status.HTTP_201_CREATED)
def create_task(
    task: schemas.TaskCreate,
    db: session = Depends(get_db),
    current_user : models.User = Depends(get_current_user)
):
    new_task = models.Task(**task.model_dump(), owner_id = current_user.id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@router.get("/", response_model=List[schemas.TaskResponse])
def list_task(
    skip: int = 0,
    limit: int = 10, 
    db : session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    tasks = (
        db.query(models.Task)
        .filter(models.Task.owner_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
        )
    return tasks

@router.get("/{task_id}",response_model=schemas.TaskResponse)
def get_task(
    task_id : int ,
    db: session = Depends(get_db),
    current_user : models.User = Depends(get_current_user)
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , 
            detail="Task not found")
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this task")

    return task

@router.put("/{task_id}",response_model=schemas.TaskResponse)
def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate ,
    db: session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Not authorized to update this task")

    update_data = task_update.model_dump(exclude_unset=True)

    for field , value in update_data.items():
        setattr(task ,field ,value)

    db.commit()
    db.refresh(task)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)

def delete_task(
    task_id: int ,
    db: session=Depends(get_db),
    current_user: models.User= Depends(get_current_user)
):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="Task not found")
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN ,detail="Not authorized to delete this task")

    db.delete(task)
    db.commit()
    return None

    
