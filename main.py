import os
import sqlite3
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# CORS ruxsatnomasi (Mini App ulana olishi uchun)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_NAME = "school_bot_pro_v20.db"

def init_db():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fio TEXT NOT NULL,
                code TEXT UNIQUE NOT NULL,
                parent_chat_id INTEGER DEFAULT 0,
                tarix INTEGER DEFAULT 0,
                geo INTEGER DEFAULT 0,
                vazifa INTEGER DEFAULT 0,
                davomat TEXT DEFAULT 'Keldi',
                payment_amount INTEGER DEFAULT 0,
                payment_status TEXT DEFAULT 'To''lanmagan',
                payment_date TEXT DEFAULT '-',
                phone TEXT DEFAULT 'Kiritilmagan',
                group_name TEXT DEFAULT 'Asosiy guruh'
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS calendar_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_title TEXT NOT NULL,
                event_date TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_text TEXT NOT NULL
            )
        """)
        conn.commit()

init_db()

# Models
class StudentCreate(BaseModel):
    fio: str
    code: str

class ScoreUpdate(BaseModel):
    tarix: int
    geo: int
    vazifa: int

class PaymentUpdate(BaseModel):
    amount: int
    status: str

class AttendanceUpdate(BaseModel):
    davomat: str

class EventCreate(BaseModel):
    event_title: str
    event_date: str

class NoteCreate(BaseModel):
    note_text: str

# --- API ENDPOINTS ---

@app.get("/")
def home():
    return {"status": "e-Kundalik API ishlamoqda!"}

@app.get("/api/students")
def get_students():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, fio, code, tarix, geo, vazifa, davomat, payment_amount, payment_status, payment_date, phone FROM students")
        rows = cursor.fetchall()
        return [
            {
                "id": r[0], "fio": r[1], "code": r[2], "tarix": r[3],
                "geo": r[4], "vazifa": r[5], "davomat": r[6],
                "payment_amount": r[7], "payment_status": r[8],
                "payment_date": r[9], "phone": r[10]
            } for r in rows
        ]

@app.post("/api/students")
def add_student(st: StudentCreate):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO students (fio, code) VALUES (?, ?)", (st.fio, st.code))
            conn.commit()
            return {"message": "Muvaffaqiyatli qo'shildi"}
        except Exception as e:
            raise HTTPException(status_code=400, detail="Kod band yoki xatolik")

@app.delete("/api/students/{s_id}")
def delete_student(s_id: int):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id = ?", (s_id,))
        conn.commit()
        return {"message": "O'chirildi"}

@app.put("/api/students/{s_id}/scores")
def update_scores(s_id: int, sc: ScoreUpdate):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE students SET tarix = ?, geo = ?, vazifa = ? WHERE id = ?", (sc.tarix, sc.geo, sc.vazifa, s_id))
        conn.commit()
        return {"message": "Ballar yangilandi"}

@app.put("/api/students/{s_id}/attendance")
def update_attendance(s_id: int, att: AttendanceUpdate):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE students SET davomat = ? WHERE id = ?", (att.davomat, s_id))
        conn.commit()
        return {"message": "Davomat yangilandi"}

@app.put("/api/students/{s_id}/payment")
def update_payment(s_id: int, pay: PaymentUpdate):
    today = datetime.now().strftime("%d.%m.%Y") if pay.status == "To'langan" else "-"
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE students SET payment_amount = ?, payment_status = ?, payment_date = ? WHERE id = ?", (pay.amount, pay.status, today, s_id))
        conn.commit()
        return {"message": "To'lov yangilandi"}

# Taqvim va Eslatmalar
@app.get("/api/events")
def get_events():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, event_title, event_date FROM calendar_events")
        return [{"id": r[0], "title": r[1], "date": r[2]} for r in cursor.fetchall()]

@app.post("/api/events")
def add_event(ev: EventCreate):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO calendar_events (event_title, event_date) VALUES (?, ?)", (ev.event_title, ev.event_date))
        conn.commit()
        return {"message": "Tadbir qo'shildi"}

@app.get("/api/notes")
def get_notes():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, note_text FROM admin_notes")
        return [{"id": r[0], "text": r[1]} for r in cursor.fetchall()]

@app.post("/api/notes")
def add_note(note: NoteCreate):
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO admin_notes (note_text) VALUES (?)", (note.note_text,))
        conn.commit()
        return {"message": "Eslatma qo'shildi"}
