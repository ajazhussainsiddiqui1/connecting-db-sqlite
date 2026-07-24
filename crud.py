from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models import Task
from database import engine


def create_task(title:str, done:bool=False):
    with Session(engine) as session:
        try:
            new_task = Task(title=title, done=done)
            session.add(new_task)
            session.commit()
            session.refresh(new_task) # Refresh loads the database-generated ID back into the object

            session.expunge(new_task)  # Detach object from session so it can be safely used outside the block
            
            return new_task
        except SQLAlchemyError as e:
            session.rollback()         # rolling-back recent changes
            print(f"Error creating task: {e}")
            return None 


def get_all_tasks():
    with Session(engine) as session:
        try:
            statement = select(Task)
            tasks = session.scalars(statement=statement).all()

            for task in tasks:     # Create a detached copy of the list to use outside the session
                session.expunge(task)
            return list(tasks)    
        except SQLAlchemyError as e:
            print(f"Error fetching tasks: {e}")
            return []


def get_task_by_id(task_id:int):
    with Session(engine) as session:
        try:
            task = session.get(Task, task_id)
            if task:
                session.expunge(task)
            return task 
        except SQLAlchemyError as e:
            print(f"Error fetching task {task_id}: {e}")
            return None    


def update_task(task_id, title=None, done=None):
    with Session(engine) as session:
        try:
            task = session.get(Task, task_id)
            if not task:
                print(f"Task with ID {task_id} not Found.")       
                return None 
            if title is not None:
                task.title = title
            if done is not None:
                task.done = done 

            session.commit()
            session.refresh(task)
            session.expunge(task)
            return task 
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error updating task {task_id}: {e}")
            return 


def delete_task(task_id):
    with Session(engine) as session:
        try:
            task = session.get(Task, task_id)
            if not task:
                print(f"Task with ID {task_id} not found.")
                return False

            session.delete(task)
            session.commit()
            return True     
        except SQLAlchemyError as e:
            session.rollback()
            print(f"Error deleting task {task_id}: {e}")
            return False   
