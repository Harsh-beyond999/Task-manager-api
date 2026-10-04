from fastapi import FastAPI , HTTPException , status , Depends
from database import get_all_tasks,get_task,insert_task,delete_task,update_task_db,get_connection,create_table
from database import create_user,get_user_by_username,get_user_by_id,get_all_users
from typing import Literal
from pwdlib import PasswordHash
from jose import jwt
from datetime import datetime , timedelta
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY") 
ALGORITHM = os.getenv("ALGORITHM")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return user_id

    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

password_hash = PasswordHash.recommended()


app = FastAPI()




from pydantic import BaseModel,Field,field_validator
class Task(BaseModel):
    name : str = Field(min_length=1) 
    status : Literal ["Completed" , "Pending"]  
class TaskUpdate(BaseModel):
    name: str | None = None
    status: Literal["Pending", "Completed"] | None = None

class TaskResponse(BaseModel):
    id: int
    name: str
    status: Literal["Pending", "Completed"]    

class UserCreate(BaseModel):
    username : str = Field(pattern=r"^[a-z][a-z0-9._]*$")
    password : str     
    @field_validator("password")
    @classmethod
    def validate_password(cls,password):

        if not any(char.islower() for char in password):
            raise ValueError("Password must contain a lowercase alphabet")
        if not any(char.isupper() for char in password):
            raise ValueError("Password must contain an uppercase alphabet")
        
        
        if not any(char.isalpha() for char in password):
            raise ValueError("Password must contain an alphabet")

        if not any(char.isdigit() for char in password):
            raise ValueError("Password must contain a number")

        if not any(not char.isalnum() for char in password):
            raise ValueError("Password must contain a special character")

        return password


class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    user_id : int
    username : str    

@app.get("/")
def home():
    return("message : hello , from my backend")

@app.get("/about")
def about_page():
    return("'about' : this is about page")
@app.get("/tasks" , response_model=list[TaskResponse] )
def tasks(current_user = Depends(get_current_user)):
    return get_all_tasks(current_user)

@app.get("/tasks/{task_id}" , response_model=TaskResponse)
def get_task_by_task_id(task_id: int,current_user = Depends(get_current_user)):
    task = get_task(task_id,current_user)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return task


@app.post("/tasks",status_code=status.HTTP_201_CREATED)
def create_task(task: Task,current_user = Depends(get_current_user)):
    new_id = insert_task(task.name, task.status,current_user)

    return {
        "id": new_id,
        "name": task.name,
        "status": task.status
    }
@app.delete("/tasks/{task_id}", status_code=204)
def delete_task_endpoint(task_id: int,current_user=Depends(get_current_user)):
    task = get_task(task_id,current_user)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    delete_task(task_id,current_user)

    

@app.put("/tasks/{task_id}")
def update_task(task_id : int , task : Task,current_user=Depends(get_current_user)):
    existing_task = get_task(task_id,current_user)

    if existing_task is None:
     raise HTTPException(status_code=404, detail="Task not found")

    update_task_db(task_id, task.name, task.status,current_user)

    updated_task = get_task(task_id,current_user)
    return {
    "message": "task updated successfully",
    "old task": existing_task,
    "new task": updated_task
       }
    

@app.patch("/tasks/{task_id}")
def patch_task(task_id: int, task: TaskUpdate,current_user = Depends(get_current_user)):
    existing_task = get_task(task_id,current_user)

    if existing_task is None:
      raise HTTPException(status_code=404, detail="Task not found")
    new_name = task.name if task.name is not None else existing_task['name']
    new_status = task.status if task.status is not None else existing_task['status']
    update_task_db(task_id,new_name,new_status,current_user)
    updated_task = get_task(task_id,current_user)
    return {
    "message": "task patched successfully",
    "old task": existing_task,
    "updated task": updated_task
    }
@app.post("/users",response_model=UserResponse,status_code=201)
def register_user(user : UserCreate):
    existing_user = get_user_by_username(user.username)

    if existing_user is not None:
     raise HTTPException(
        status_code=409,
        detail="Username already exists"
    )
    hashed_password = password_hash.hash(user.password)
    user_id = create_user(user.username,hashed_password)
    return { "user_id":user_id ,
            "username" : user.username}
@app.post("/login")
def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    db_user = get_user_by_username(form_data.username)

    if db_user is None:
        raise HTTPException(status_code=404,detail="Incorrect username/password")

    if not password_hash.verify(
        form_data.password,
        db_user['password_hash']):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )
        

    access_token = create_access_token(db_user["user_id"])
    return {
        "access_token" : access_token ,
        "token_type" : "bearer"
    }

def create_access_token(user_id):
    payload = {
        "sub": str(user_id),
        "exp": datetime.utcnow() + timedelta(minutes=30)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return token   

def get_current_admin(current_user=Depends(get_current_user)):

    user = get_user_by_id(current_user)
    print("CURRENT USER ID:", current_user)
    print("USER FROM DB:", user)

    if user['role'] != 'admin':
        raise HTTPException(
    status_code=403,
    detail="Admin access required"
        )
    
    return(user)

@app.get("/users", response_model= list[UserResponse])

def get_users(current_admin = Depends(get_current_admin)):
    return get_all_users()