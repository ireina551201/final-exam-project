import sqlite3
from pydantic import BaseModel ,Field
from fastapi import FastAPI ,HTTPException ,Response

class PostCreate(BaseModel):
    text: str
    author: str
    tags: str

class PostResponse(PostCreate): 
    id: int

def get_db_conn():

    conn = sqlite3.connect('quotes.db')
    conn.row_factory = sqlite3.Row
    return conn

app = FastAPI()

@app.get('/quotes' ,response_model=list[PostResponse])
def get_all_quotes():
    
    # 資料庫連線
    conn = get_db_conn()
    cursor = conn.cursor()

    # 資料獲取
    cursor.execute('SELECT * FROM quotes')
    table = cursor.fetchall()

    # 回傳資料格式化
    data = []
    for quote in table:
        data.append({'id':quote['id'],'text':quote['text'],'author':quote['author'],'tags':quote['tags']})

    # 關閉資料庫
    cursor.close()
    conn.close()
    
    return data

@app.post('/quotes' ,response_model=PostResponse)
def post_quote(data:PostCreate):

    # 資料庫連線
    conn = get_db_conn()
    cursor = conn.cursor()

    # 新增資料
    cursor.execute('INSERT INTO quotes (text ,author ,tags) VALUES (? ,? ,?)' ,(data.text ,data.author ,data.tags))
    id = cursor.lastrowid
    conn.commit()

    # 查詢新增後的資料
    cursor.execute('SELECT id ,text ,author ,tags FROM quotes WHERE id = ?' ,(id,))
    data = cursor.fetchone()

    # 關閉資料庫
    cursor.close()
    conn.close()

    return {'id':data['id'],'text':data['text'],'author':data['author'],'tags':data['tags']}

@app.put('/quotes/{id}' ,response_model=PostResponse)
def updata_quote(id:int ,data: PostCreate):

    # 資料庫連線
    conn = get_db_conn()
    cursor = conn.cursor()
    
    # 判斷id資料是否存在，如果不存在回傳404，反之則更新
    cursor.execute('SELECT 1 FROM quotes WHERE id = ?' ,(id,))
    if cursor.fetchone() is None:
        raise HTTPException(status_code=404 ,detail='Quote not found')
    else:
        cursor.execute('UPDATE quotes SET text = ? ,author = ? ,tags = ? WHERE id = ?' ,
                       (data.text ,data.author ,data.tags ,id))
        conn.commit()
    
    # 獲取更新後的資料
    cursor.execute('SELECT id ,text ,author ,tags FROM quotes WHERE id = ?' ,(id,))
    data = cursor.fetchone()

    # 關閉資料庫
    cursor.close()
    conn.close()

    return {'id':data['id'],'text':data['text'],'author':data['author'],'tags':data['tags']}

@app.delete('/quotes/{id}')
def delete_quote(id:int):

    # 資料庫連線
    conn = get_db_conn()
    cursor = conn.cursor()

    # 判斷id資料是否存在，如果不存在回傳404，反之則刪除
    cursor.execute('SELECT 1 FROM quotes WHERE id = ?' ,(id,))
    if cursor.fetchone() is None:
        raise HTTPException(status_code=404 ,detail='Quote not found')
    else:
        cursor.execute('DELETE FROM quotes WHERE id = ?' ,(id,))
        conn.commit()

    # 關閉資料庫
    cursor.close()
    conn.close()
    
    return {'message':'Quote deleted successfully'}