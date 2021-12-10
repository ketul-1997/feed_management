from feed_apis.v1.route_login import access_token
from db.session import get_db
from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from feed_management.authorization.forms import LoginForm

from typing import List
from fastapi import responses, status
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

templates = Jinja2Templates(directory="templates")
router = APIRouter(include_in_schema=False)


@router.get("/")
def login_user(request: Request):
    return templates.TemplateResponse("authorization/login.html", {"request": request})


@router.get("/login")
def redirect_login(request: Request):
    return responses.RedirectResponse(
                "/", status_code=status.HTTP_302_FOUND
            )


@router.post("/")
async def login_user(request: Request, db: Session = Depends(get_db)):
    main_form = LoginForm(request)
    await main_form.load_content()
    if await main_form.check_valid():
        try:
            main_form.__dict__.update(msg="Login Done")
            response = templates.TemplateResponse(
                "authorization/chatbot.html", main_form.__dict__)
            access_token(response=response, form_data=main_form, db=db)
            return response
        except HTTPException:
            main_form.__dict__.update(msg="")
            main_form.__dict__.get("errors").append("Email or Password is incorrect")
            return templates.TemplateResponse("authorization/login.html", main_form.__dict__)
    return templates.TemplateResponse("authorization/login.html", main_form.__dict__)


class Connection:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = Connection()


@router.websocket("/client-id/{client_id}")
async def main_websocket(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(
                f"Me : {data}", websocket)
            await manager.broadcast(f"#{client_id}: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"{client_id} leaved group")
