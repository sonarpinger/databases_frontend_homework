#!/usr/bin/env python

# database stuff
import psycopg2
import datetime
from pydantic import BaseModel
from typing import Optional 

# webserver stuff
import uvicorn
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse, RedirectResponse, JSONResponse

app = FastAPI()

templates = Jinja2Templates(directory='templates')
app.mount('/static', StaticFiles(directory='static'), name='static')

app.add_middleware(SessionMiddleware, secret_key='!thisisasupersecretkeyandyouwouldneverguessitevengivenatrillionyears!')

conn_string = "host=localhost dbname=hw5 user=postgres password=postgres"
conn = psycopg2.connect(conn_string)

class User(BaseModel):
  username: str
  uid: Optional[int] = None

class RequestDate(BaseModel):
  date: str

class InputEntry(BaseModel):
  date: str
  food_name: str
  food_quantity: int

def yeild_conn():
  yield conn

def yeild_cursor():
  yield conn.cursor()

def get_user_id(conn, cursor, username):
  try:
    pre_line = f"SELECT user_id FROM logged_users WHERE username = '"
    # arg = f"{{{username}}}'"
    arg = f"{username}'"
    line = pre_line + arg
    cursor.execute(
      line
    )
  except Exception as e:
    print(e)
    conn.rollback()
  
  if cursor.rowcount == -1 or cursor.rowcount == 0:
    print(f"User: {username} not found...")
    return None
  return cursor.fetchone()[0]

def get_logged_dates(conn, cursor, uid):
  # get the logged_foods for the user and print them by date
  pre_line = f"SELECT DISTINCT ON (date_logged) date_logged FROM logged_food WHERE user_id = "
  arg = f"{uid}"
  post_line = f" ORDER BY date_logged"
  line = pre_line + arg + post_line
  cursor.execute(
    line
  )
  rows = cursor.fetchall()
  dates = [row[0].strftime("%Y-%m-%d") for row in rows]
  return dates

def get_logged_foods(conn, cursor, uid, date):
# get the logged foods for the selected date
  pre_line = f"SELECT food_name, food_quantity FROM logged_food WHERE user_id = "
  arg1 = f"{uid} AND date_logged = "
  arg2 = f"'{date}'"
  line = pre_line + arg1 + arg2
  cursor.execute(
    line
  )
  rows = cursor.fetchall()
  logged_foods = []
  for row in rows:
    logged_foods.append({"food_name": row[0], "food_quantity": row[1]})
  return logged_foods

def get_food_nutrients(conn, cursor, uid, date):
  # associate the logged foods with the food_calorie_conversion_factor table using the fdc_id associated with the food_name
  # get the total nutrients for the selected date
  pre_line = f"WITH user_logged_foods AS (SELECT users.username, lf.food_name, lf.food_quantity FROM logged_users users JOIN logged_food lf ON users.user_id = lf.user_id WHERE users.user_id = "
  arg1 = f"{uid} AND date_logged = "
  arg2 = f"'{date}'"
  post_line = f"), food_info AS (SELECT ulf.username, ulf.food_quantity, ulf.food_name, f.fdc_id FROM user_logged_foods ulf JOIN food f ON ulf.food_name = f.description), food_nutrients AS (SELECT fi.username, fi.food_quantity, fi.food_name, nu.name, fo_nu.amount, nu.unit_name FROM food_info fi JOIN food_nutrient fo_nu ON fi.fdc_id = fo_nu.fdc_id JOIN nutrient nu ON fo_nu.nutrient_id = nu.id) SELECT SUM(CASE WHEN name = 'Protein' THEN amount * food_quantity ELSE 0 END) AS total_protein, SUM(CASE WHEN name = 'Total lipid (fat)' THEN amount * food_quantity ELSE 0 END) AS total_fat, SUM(CASE WHEN name = 'Carbohydrate, by difference' THEN amount * food_quantity ELSE 0 END) AS total_carbohydrate FROM food_nutrients"
  line = pre_line + arg1 + arg2 + post_line
  cursor.execute(
    line
  )
  rows = cursor.fetchall()
  return [{"total_protein": str(rows[0][0]), "total_fat": str(rows[0][1]), "total_carbohydrate": str(rows[0][2])}]

def add_entry(conn, cursor, uid, input_date, food_name, food_quantity):
  # add the logged food to the logged_food table
  pre_line = f"INSERT INTO logged_food (user_id, food_name, food_quantity, date_logged) VALUES ("
  arg1 = f"{uid}, "
  arg2 = f"'{food_name}', "
  arg3 = f"{food_quantity}, "
  arg4 = f"'{input_date}')"
  line = pre_line + arg1 + arg2 + arg3 + arg4
  cursor.execute(
    line
  )
  conn.commit()

@app.get("/")
async def root(request: Request):
  return templates.TemplateResponse('index.html', {'request': request})

@app.get("/dashboard")
async def root(request: Request):
  return templates.TemplateResponse('index.html', {'request': request})

@app.get("/submit-entry")
async def root(request: Request):
  return templates.TemplateResponse('index.html', {'request': request})

@app.post("/login")
async def login(request: Request, user: User, conn = Depends(yeild_conn), cursor = Depends(yeild_cursor)):
  try:
    username = user.username
  except Exception as e:
    print(e)
    return JSONResponse(content={"error": "Invalid request"}, status=400)
  uid = get_user_id(conn, cursor, username)
  if uid is None:
    return JSONResponse(content={"error": "User not found"}, status_code=404)
  user.uid = uid
  request.session['username'] = username
  return JSONResponse(content={"message": "User logged in"}, status_code=200)

@app.get("/get_logged_dates")
async def return_logged_dates(request: Request, conn = Depends(yeild_conn), cursor = Depends(yeild_cursor)):
  username = request.session.get('username')
  uid = get_user_id(conn, cursor, username)
  if uid is None:
    return JSONResponse(content={"error": "User not found"}, status_code=404)
  dates = get_logged_dates(conn, cursor, uid)
  print(dates)
  return JSONResponse(content={"dates": dates}, status_code=200)

@app.post("/get_logged_foods")
async def return_logged_foods(request: Request, date: RequestDate, conn = Depends(yeild_conn), cursor = Depends(yeild_cursor)):
  username = request.session.get('username')
  date = date.date
  uid = get_user_id(conn, cursor, username)
  if uid is None:
    return JSONResponse(content={"error": "User not found"}, status_code=404)
  logged_foods = get_logged_foods(conn, cursor, uid, date)
  return JSONResponse(content={"logged_foods": logged_foods}, status_code=200)

@app.post("/get_food_nutrients")
async def return_food_nutrients(request: Request, date: RequestDate, conn = Depends(yeild_conn), cursor = Depends(yeild_cursor)):
  username = request.session.get('username')
  date = date.date
  uid = get_user_id(conn, cursor, username)
  if uid is None:
    return JSONResponse(content={"error": "User not found"}, status_code=404)
  food_nutrients = get_food_nutrients(conn, cursor, uid, date)
  return JSONResponse(content={"food_nutrients": food_nutrients}, status_code=200)

@app.post("/submit_entry")
async def submit_entry(request: Request, input_entry: InputEntry, conn = Depends(yeild_conn), cursor = Depends(yeild_cursor)):
  username = request.session.get('username')
  uid = get_user_id(conn, cursor, username)
  if uid is None:
    return JSONResponse(content={"error": "User not found"}, status_code=404)
  input_date = input_entry.date
  input_food = input_entry.food_name
  input_amount = input_entry.food_quantity
  add_entry(conn, cursor, uid, input_date, input_food, input_amount)
  return JSONResponse(content={"message": "Entry added"}, status_code=200)

@app.get("/logout")
async def logout(request: Request):
  request.session.pop('username', None)
  return JSONResponse(content={"message": "User logged out"}, status_code=200)

if __name__ == "__main__":
  uvicorn.run('main:app', host='127.0.0.1', port=8000)
