from fastapi import APIRouter , Depends , status , HTTPException  
from sqlalchemy.orm import session
from typing import List

from database import get_db 
import schemas 
import models
from users import get_current_user
from cache import set_cached ,get_cached ,invalidate_user_tasks ,task_key,task_list_key #new

router = APIRouter(prefix="/tasks" , tags=["tasks"])

@router.post("/" , response_model=schemas.TaskResponse , status_code=status.HTTP_201_CREATED)
async def create_task(
    task: schemas.TaskCreate,
    db: session = Depends(get_db),
    current_user : models.User = Depends(get_current_user)
):
    new_task = models.Task(**task.model_dump(), owner_id = current_user.id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    #remove from redis bcoz value changes
    await invalidate_user_tasks(current_user.id)
    return new_task

@router.get("/", response_model=List[schemas.TaskResponse])
async def  list_task(
    skip: int = 0,
    limit: int = 10, 
    db : session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    key = task_list_key(current_user.id , skip , limit)

    #if present in redis return 
    cached = await get_cached(key)
    if cached is not None:
        return cached
    
    tasks = (
        db.query(models.Task)
        .filter(models.Task.owner_id == current_user.id)
        .offset(skip)
        .limit(limit)
        .all()
        )

    #if not present in cache
    result = []
    for t in tasks:
        validated = schemas.TaskResponse.model_validate(t)
        result.append(validated.model_dump(mode="json"))
    await set_cached(key , result)
    return tasks

@router.get("/{task_id}",response_model=schemas.TaskResponse)
async def get_task(
    task_id : int ,
    db: session = Depends(get_db),
    current_user : models.User = Depends(get_current_user)
):
    key = task_key(current_user.id , task_id)
    # if present return 
    cached = await get_cached(key)
    if cached is not None:
        return cached
    
    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , 
            detail="Task not found")
    if task.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this task")

    #if not present in cache
    result = schemas.TaskResponse.model_validate(task).model_dump(mode="json")
    await set_cached(key , result)
    return task

@router.put("/{task_id}",response_model=schemas.TaskResponse)
async def update_task(
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

    #remove from cache bcoz value changes
    await invalidate_user_tasks(current_user.id)
    return task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)

async def delete_task(
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

    #remove from cache because value changes
    await invalidate_user_tasks(current_user.id) 
    return None

    
