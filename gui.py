import tkinter as tk
import tkinter.ttk as ttk
import requests
import threading
import re

root = 'http://127.0.0.1:8000'

# 資料庫數據請求(子進程)
def th_get_all_data():
    
    try:
        response = requests.get(root+'/quotes')
        # 成功
        if response.status_code == 200:
            data = response.json()
            window.after(0 ,lambda: get_success(data))
        # 資料不存在
        else: request_error(f'錯誤: {response.status_code}')
    except requests.exceptions.RequestException as e:
        request_error(f'錯誤: {e}')

# 新增資料請求(子進程)
def th_post_data():

    data = {'text': text.get('1.0' ,'end'),
            'author': var_author.get(),
            'tags': var_tags.get()}

    try:
        response = requests.post(root+'/quotes',json=data)
        if response.status_code == 200:
            window.after(0 ,post_success)
        elif response.status_code == 404:
            request_error('錯誤: 操作失敗，找不到目標資料')
        else: request_error(f'錯誤: {response.status_code}')
    except requests.exceptions.RequestException as e:
        request_error(f'錯誤: {e}')

# 更新資料請求(子進程)
def th_update_data():

    data = {'text': text.get('1.0' ,'end'),
            'author': var_author.get(),
            'tags': var_tags.get()}
    
    iid = tree.selection()[0]
    id = tree.item(iid)['values'][0]

    try:
        response = requests.put(f'{root}/quotes/{id}',json=data)
        if response.status_code == 200:
            window.after(0 ,update_success)
        elif response.status_code == 404:
            request_error('錯誤: 操作失敗，找不到目標資料')
        else: request_error(f'錯誤: {response.status_code}')
    except requests.exceptions.RequestException as e:
        request_error(f'錯誤: {e}')

# 刪除資料請求(子進程)
def th_delete_data():

    id = tree.selection()[0]

    try:
        response = requests.delete(f'{root}/quotes/{id}')
        if response.status_code == 200:
            window.after(0 ,delete_success)
        elif response.status_code == 404:
            request_error('錯誤: 操作失敗，找不到目標資料')
        else: request_error(f'錯誤: {response.status_code}')
    except requests.exceptions.RequestException as e:
        request_error(f'錯誤: {e}')

# 成功獲取資料庫數據後的處理
def get_success(data):

    # 清空資料顯示區
    for iid in tree.get_children():
        tree.delete(iid)

    # 顯示新的資料庫數據
    for quote in data:
        tree.insert('' ,index='end' ,values=(quote['id'] ,quote['author'] ,quote['text'] ,quote['tags'])  ,iid=quote['id'])
    re_btn.config(state=tk.NORMAL)

    # UI介面調整
    update_btn.config(state=tk.DISABLED)
    delete_btn.config(state=tk.DISABLED)
    tree.see('1')
    text.delete(1.0 ,'end')
    var_author.set('')
    var_tags.set('')
    bar_state['text'] = '資料載入完成'

# 成功新增資料後的處理
def post_success():

    add_btn.config(state=tk.NORMAL)
    bar_state['text'] = '新增成功'

# 成功更新資料後的處理
def update_success():

    update_btn.config(state=tk.NORMAL)
    bar_state['text'] = '更新成功'

# 成功刪除資料後的處理
def delete_success():

    delete_btn.config(state=tk.NORMAL)
    bar_state['text'] = '刪除成功'

# 失敗後的處理
def request_error(info):

    bar_state['text'] = info

# 資料顯示區的資料被點擊後的處理
def on_select(event):

    if tree.selection() == (): return
    
    id = tree.selection()[0]
    text.delete(1.0 ,'end')
    text.insert(1.0 ,chars=tree.item(id)['values'][2])
    var_author.set(tree.item(id)['values'][1])
    var_tags.set(tree.item(id)['values'][3])
    update_btn.config(state=tk.NORMAL)
    delete_btn.config(state=tk.NORMAL)

# 按鈕被點擊時後的處理
def on_click(event):

    # 獲取被點擊按鈕的ID
    id = str(event.widget)

    # 按鈕: 重新整理
    if id == '.!labelframe2.!button':
        bar_state['text'] = '連線中，請稍候...'
        threading.Thread(target=th_get_all_data ,daemon=True).start()
        re_btn.config(state=tk.DISABLED)
        return
    
    # 按鈕: 新增
    if id == '.!labelframe2.!button2':
        content = text.get('1.0' ,'end')
        content = re.sub(r'\s+' ,'' ,content)
        if content == '':
            request_error('錯誤: Text區塊不可為空')
            return
        bar_state['text'] = '連線中，請稍候...'
        threading.Thread(target=th_post_data ,daemon=True).start()
        add_btn.config(state=tk.DISABLED)
        return
    
    # 按鈕: 更新
    if id == '.!labelframe2.!button3':
        content = text.get('1.0' ,'end')
        content = re.sub(r'\s+' ,'' ,content)
        if content == '':
            request_error('錯誤: Text區塊不可為空')
            return
        bar_state['text'] = '連線中，請稍候...'
        threading.Thread(target=th_update_data ,daemon=True).start()
        update_btn.config(state=tk.DISABLED)
        return

    # 按鈕: 刪除
    if id == '.!labelframe2.!button4':
        bar_state['text'] = '連線中，請稍候...'
        threading.Thread(target=th_delete_data ,daemon=True).start()
        delete_btn.config(state=tk.DISABLED)


if __name__ == '__main__':

    #==============#
    #   主視窗設定  #
    #==============#
    window = tk.Tk()
    window.title('名言佳句管理系統(Threading 版)')
    window.resizable(False,False)
    window.geometry('800x600')

    #===============#
    # 資料顯示區設定 #
    #===============#
    tree = ttk.Treeview(window ,columns=('ID' ,'Author' ,'Text' ,'Tags') ,show='headings' ,height=14)

    # 標題顯示
    tree.heading('ID' ,text='ID')
    tree.heading('Author' ,text='作者')
    tree.heading('Text' ,text='名言內容')
    tree.heading('Tags' ,text='標籤')
    
    # 欄位設定
    tree.column('ID' ,width=50)
    tree.column('Author' ,width=150)
    tree.column('Text' ,width=400)
    tree.column('Tags' ,width=150)

    # 排版
    tree.pack()

    #================#
    # 新增/編輯區設定 #
    #================#
    frame_edit = tk.LabelFrame(window ,text='編輯/新增區' ,width=750 ,height=175 ,pady=5 ,padx=5)
    frame_edit.pack_propagate(False)
    frame_edit.pack(pady=5)

    # 用於表格式的排版
    l_frame = tk.Frame(frame_edit)
    r_frame = tk.Frame(frame_edit)

    # 標籤設定
    label_text = tk.Label(frame_edit ,text='名言內容(Text):')
    label_author = tk.Label(l_frame ,text='作者(Author):')
    label_tags = tk.Label(r_frame ,text='標籤(Tags):')

    # 輸入框設定
    var_author = tk.StringVar()
    var_tags = tk.StringVar()
    entry_author = tk.Entry(l_frame ,textvariable=var_author)
    entry_tags = tk.Entry(r_frame ,textvariable=var_tags)
    text = tk.Text(frame_edit ,height=5 ,width=103 ,wrap=tk.WORD)
    
    # 排版
    label_text.pack(side='top' ,anchor='w')
    text.pack(side='top')
    l_frame.pack(side='left' ,expand=True ,fill='both')
    r_frame.pack(side='right' ,expand=True ,fill='both')
    label_author.pack(side='top' ,anchor='w' ,pady=5)
    label_tags.pack(side='top' ,anchor='w' ,pady=5)
    entry_author.pack(side='bottom' ,expand=True ,fill='x' ,padx=7)
    entry_tags.pack(side='bottom' ,expand=True ,fill='x' ,padx=7)

    #===============#
    # 操作選項區設定 #
    #===============#
    frame_opt = tk.LabelFrame(window ,text='操作選項' ,width=750 ,height=70 ,pady=1 ,padx=5)
    frame_opt.propagate(False)

    # 按鈕設定
    re_btn = tk.Button(frame_opt ,text='重新整理(Refresh)' ,bg='#97CBFF')
    add_btn = tk.Button(frame_opt ,text='新增(Add)' ,bg='#02DF82')
    update_btn = tk.Button(frame_opt ,text='更新(Update)' ,bg='#FF9D6F' ,state=tk.DISABLED)
    delete_btn = tk.Button(frame_opt ,text='刪除(Delete)' ,bg='#FF5151' ,state=tk.DISABLED)

    # 排版
    frame_opt.pack(side='top' ,pady=1)
    re_btn.pack(side='left' ,expand=True ,padx=5 ,fill='x')
    add_btn.pack(side='left' ,expand=True ,padx=5 ,fill='x')
    update_btn.pack(side='left' ,expand=True ,padx=5 ,fill='x')
    delete_btn.pack(side='left' ,expand=True ,padx=5 ,fill='x')

    #==============#
    #    狀態列    #
    #==============#
    bar_state = tk.Label(window ,text='狀態列(Status Bar)' ,relief=tk.SUNKEN ,anchor=tk.W ,padx=5 ,pady=5)
    bar_state.pack(side='top' ,fill='x' ,padx=25 ,pady=5)

    #==============#
    #   事件綁定    #
    #==============#
    tree.bind('<<TreeviewSelect>>' ,on_select)
    re_btn.bind('<ButtonRelease-1>' ,on_click)
    add_btn.bind('<ButtonRelease-1>' ,on_click)
    update_btn.bind('<ButtonRelease-1>' ,on_click)
    delete_btn.bind('<ButtonRelease-1>' ,on_click)

    # 顯示資料庫數據
    setattr(re_btn ,'widget' ,'.!labelframe2.!button')
    on_click(re_btn)

    window.mainloop()