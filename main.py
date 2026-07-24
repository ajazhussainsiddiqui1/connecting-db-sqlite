from fastapi import FastAPI, HTTPException, status
import uvicorn
from pydantic import BaseModel
from contextlib import asynccontextmanager

from crud import create_task, get_all_tasks, get_task_by_id, update_task, delete_task
from database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    print("Tasks table verified/created successfully!") 
    yield



app = FastAPI(lifespan=lifespan)


# Stage 1: root and health endpoints

@app.get("/")
def home():
    return { "name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }


@app.get("/health")
def health():
    return { "status": "ok" }



# Stage 2: read endpoints with 404   (goes to extra)

# @app.get("/tasks")
# def get_tasks():
#     response = get_all_tasks()
    
#     tasks_dict = []
#     for task in response:
#         tasks_dict.append({"id":task.id, "title":task.title, "done":task.done})
#     return tasks_dict    



@app.get("/tasks/{id}")
def task_id(id:int):
    output = get_task_by_id(task_id=id)
    
    if output:
        return {'id':output.id, 'title':output.title, 'done':output.done}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail={ "error": f"Task {id} not found" })
    



# Stage 3: create with validation
class NewTask(BaseModel):
    title: str = None 


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def add_task(task: NewTask):

    title = task.title
    if title is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Title is required")
    
    response = create_task(title=title)
    
    return {"id":response.id, "title":response.title, "done":response.done} 



# Stage 4: full CRUD

class UpdateTask(BaseModel):
    title: str | None=None 
    done: bool | None=None


@app.put("/tasks/{id}")
def update_tasks(id:int, task_update:UpdateTask):

    response = update_task(task_id=id, title=task_update.title, done=task_update.done)  
    if response:
        return {"id":response.id, "title":response.title, "done":response.done} 
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"for id {id} task not found, {response}")


    

@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tasks(id:int):
    
    response = delete_task(task_id=id)
    if response:
        return response

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unknown id: {id}")    



#  optional extras

@app.get("/tasks")
def done_filter(done:bool | None=None, search:str | None=None):
    
    db_tasks = get_all_tasks()
    filtered_tasks = [{"id": task.id, "title": task.title, "done": task.done} for task in db_tasks] 

    if search:
        filtered_tasks = [task for task in filtered_tasks if search in task['title'].lower()]     

    if done is not None:
        filtered_tasks = [task for task in filtered_tasks if task['done']==done]
    
    return filtered_tasks


@app.get("/stats")
def get_stats():
    response = get_all_tasks()
    done = len([task for task in response if task.done])
    return {"total": len(response), "done": done, "open": len(response) - done}




if __name__ == "__main__":
    
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
