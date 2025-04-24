import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.widgets import DateEntry
import re

# เก็บข้อมูลกิจกรรมและข้อมูลทริป
activities = []
trip_info = {"name": "", "start_date": "", "end_date": "", "location": "", "total_budget": 0}

# สร้างรายการเวลา (ทุก 15 นาที ตั้งแต่ 00:00 ถึง 23:45)
time_options = [f"{h:02d}:{m:02d}" for h in range(24) for m in range(0, 60, 15)]

# เก็บอ้างอิงรูปภาพเพื่อป้องกัน garbage collection
image_references = []

def add_activity():
    time = time_combobox.get().strip()
    detail = detail_entry.get().strip()
    budget = budget_entry.get().strip()
    img_path = image_path.get().strip()
    if not time or not detail:
        messagebox.showwarning("แจ้งเตือน", "กรุณากรอกเวลาและกิจกรรม")
        return
    try:
        budget = float(budget) if budget else 0  # งบประมาณไม่บังคับ
    except ValueError:
        messagebox.showwarning("แจ้งเตือน", "งบประมาณต้องเป็นตัวเลข")
        return
    activities.append((time, detail, img_path, budget))
    update_activity_table()
    time_combobox.set("")
    detail_entry.delete(0, tk.END)
    budget_entry.delete(0, tk.END)
    image_path.set("")
    messagebox.showinfo("สำเร็จ", "เพิ่มกิจกรรมเรียบร้อย!")

def browse_image():
    filename = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")])
    if filename:
        image_path.set(filename)  # อัปเดต StringVar
        # ตรวจสอบว่า path แสดงใน UI
        image_label.config(text=filename if filename else "ไม่มีไฟล์เลือก")

def import_schedule():
    filename = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    if not filename:
        return
    try:
        global trip_info
        activities.clear()
        with open(filename, "r", encoding="utf-8") as f:
            lines = f.readlines()
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith("📅 ทริป:"):
                trip_info["name"] = line.replace("📅 ทริป:", "").strip()
                name_entry.delete(0, tk.END)
                name_entry.insert(0, trip_info["name"])
            elif line.startswith("📍 สถานที่:"):
                trip_info["location"] = line.replace("📍 สถานที่:", "").strip()
                location_entry.delete(0, tk.END)
                location_entry.insert(0, trip_info["location"])
            elif line.startswith("🗓️ วันที่:"):
                date_part = line.replace("🗓️ วันที่:", "").strip()
                start_date, end_date = date_part.split(" ถึง ")
                trip_info["start_date"] = start_date.strip()
                trip_info["end_date"] = end_date.strip()
                start_date_entry.entry.delete(0, tk.END)
                start_date_entry.entry.insert(0, start_date)
                end_date_entry.entry.delete(0, tk.END)
                end_date_entry.entry.insert(0, end_date)
            elif line.startswith("💰 งบประมาณรวม:"):
                trip_info["total_budget"] = float(line.replace("💰 งบประมาณรวม:", "").strip())
            elif " - " in line:
                match = re.match(r"(\d{2}:\d{2}) - (.+?)(?: \((\d+\.?\d*)\))?$", line)
                if match:
                    time, detail, budget = match.groups()
                    time = time.strip()
                    detail = detail.strip()
                    budget = float(budget) if budget else 0
                    if time in time_options:
                        activities.append((time, detail, "", budget))
        update_activity_table()
        messagebox.showinfo("สำเร็จ", f"นำเข้าไฟล์ {filename} เรียบร้อย!")
    except Exception as e:
        messagebox.showerror("เกิดข้อผิดพลาด", f"ไม่สามารถนำเข้าไฟล์: {str(e)}")

def update_activity_table():
    global image_references
    for row in activity_table.get_children():
        activity_table.delete(row)
    image_references = []
    # เรียงลำดับตามเวลา
    activities.sort(key=lambda x: x[0])  # เรียงตามเวลา (x[0])
    total_budget = 0
    for i, (time, detail, img, budget) in enumerate(activities):
        img_tk = None
        if img:
            try:
                img_obj = Image.open(img)
                img_obj.thumbnail((30, 30))
                img_tk = ImageTk.PhotoImage(img_obj)
                image_references.append(img_tk)
            except Exception as e:
                print(f"Error loading image {img}: {e}")
                img_tk = None
        activity_table.insert("", "end", values=(time, detail, f"{budget:.2f}" if budget else "0.00", ""), image=img_tk if img_tk else "")
        total_budget += budget
    trip_info["total_budget"] = total_budget
    total_budget_label.config(text=f"💰 งบประมาณรวม: {total_budget:.2f} บาท")
    for i, child in enumerate(activity_table.get_children()):
        delete_btn = ttk.Button(activity_table, text="✕", style="danger.TButton", width=2,
                               command=lambda idx=i: delete_activity(idx))
        activity_table.window_create(child, column=4, window=delete_btn)

def delete_activity(index):
    activities.pop(index)
    update_activity_table()

def delete_selected_activities():
    selected_items = activity_table.selection()
    if not selected_items:
        messagebox.showwarning("แจ้งเตือน", "กรุณาเลือกรายการที่ต้องการลบ")
        return
    indices = sorted([activity_table.index(item) for item in selected_items], reverse=True)
    for index in indices:
        activities.pop(index)
    update_activity_table()
    messagebox.showinfo("สำเร็จ", "ลบรายการที่เลือกเรียบร้อย!")

def review_schedule():
    review_window = ttk.Toplevel(root)
    review_window.title("รีวิวแผนเที่ยว")
    review_window.geometry("600x400")
    
    ttk.Label(review_window, text=f"📅 ทริป: {trip_info['name']}", font=('TH Sarabun New', 14)).pack(anchor='w', padx=10)
    ttk.Label(review_window, text=f"📍 สถานที่: {trip_info['location']}", font=('TH Sarabun New', 14)).pack(anchor='w', padx=10)
    ttk.Label(review_window, text=f"🗓️ วันที่: {trip_info['start_date']} ถึง {trip_info['end_date']}", font=('TH Sarabun New', 14)).pack(anchor='w', padx=10)
    ttk.Label(review_window, text=f"💰 งบประมาณรวม: {trip_info['total_budget']:.2f} บาท", font=('TH Sarabun New', 14)).pack(anchor='w', padx=10)
    
    review_table = ttk.Treeview(review_window, columns=("Time", "Detail", "Budget", "Image"), show="headings", height=10)
    review_table.heading("Time", text="เวลา")
    review_table.heading("Detail", text="กิจกรรม")
    review_table.heading("Budget", text="งบประมาณ (บาท)")
    review_table.heading("Image", text="รูปภาพ")
    review_table.column("Time", width=100, anchor="center")
    review_table.column("Detail", width=250)
    review_table.column("Budget", width=100, anchor="center")
    review_table.column("Image", width=100, anchor="center")
    
    scrollbar = ttk.Scrollbar(review_window, orient="vertical", command=review_table.yview)
    review_table.configure(yscrollcommand=scrollbar.set)
    review_table.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scrollbar.pack(side="right", fill="y")
    
    review_images = []
    for time, detail, img, budget in activities:
        img_tk = None
        if img:
            try:
                img_obj = Image.open(img)
                img_obj.thumbnail((50, 50))
                img_tk = ImageTk.PhotoImage(img_obj)
                review_images.append(img_tk)
            except:
                img_tk = None
        review_table.insert("", "end", values=(time, detail, f"{budget:.2f}" if budget else "0.00", ""), image=img_tk if img_tk else "")

def save_and_print():
    try:
        trip_name = name_entry.get().strip()
        location = location_entry.get().strip()
        start_date = start_date_entry.entry.get().strip()
        end_date = end_date_entry.entry.get().strip()
        if not trip_name or not location or not start_date or not end_date:
            messagebox.showwarning("แจ้งเตือน", "กรุณากรอกข้อมูลทริปให้ครบถ้วน")
            return
        trip_info.update({
            "name": trip_name,
            "location": location,
            "start_date": start_date,
            "end_date": end_date
        })
        with open("ตารางเที่ยว.txt", "w", encoding="utf-8") as f:
            f.write(f"📅 ทริป: {trip_info['name']}\n")
            f.write(f"📍 สถานที่: {trip_info['location']}\n")
            f.write(f"🗓️ วันที่: {trip_info['start_date']} ถึง {trip_info['end_date']}\n")
            f.write(f"💰 งบประมาณรวม: {trip_info['total_budget']:.2f}\n\n")
            for time, detail, _, budget in activities:
                if budget:
                    f.write(f"{time} - {detail} ({budget:.2f})\n")
                else:
                    f.write(f"{time} - {detail}\n")
        messagebox.showinfo("บันทึกแล้ว", "บันทึกไฟล์เป็น 'ตารางเที่ยว.txt' สำเร็จ")
    except Exception as e:
        messagebox.showerror("เกิดข้อผิดพลาด", str(e))

# สร้าง UI
root = ttk.Window(themename="flatly")
root.title("โปรแกรมจัดตารางเที่ยว")
root.geometry("700x800")

# Header
header = ttk.Label(root, text="🗺️ จัดตารางเที่ยวง่าย ๆ", font=('TH Sarabun New', 24, 'bold'), bootstyle="primary")
header.pack(pady=10)

# Trip Info Frame
trip_frame = ttk.Frame(root, padding=10)
trip_frame.pack(fill='x')

ttk.Label(trip_frame, text="ชื่อทริป").grid(row=0, column=0, sticky='w', pady=2)
name_entry = ttk.Entry(trip_frame)
name_entry.grid(row=0, column=1, sticky='ew', pady=2)

ttk.Label(trip_frame, text="สถานที่").grid(row=1, column=0, sticky='w', pady=2)
location_entry = ttk.Entry(trip_frame)
location_entry.grid(row=1, column=1, sticky='ew', pady=2)

ttk.Label(trip_frame, text="วันที่เที่ยว").grid(row=2, column=0, sticky='w', pady=2)
start_date_entry = DateEntry(trip_frame, dateformat="%Y-%m-%d")
start_date_entry.grid(row=2, column=1, sticky='w', pady=2)

ttk.Label(trip_frame, text="วันกลับ").grid(row=3, column=0, sticky='w', pady=2)
end_date_entry = DateEntry(trip_frame, dateformat="%Y-%m-%d")
end_date_entry.grid(row=3, column=1, sticky='w', pady=2)

trip_frame.columnconfigure(1, weight=1)

# Input Frame
input_frame = ttk.Frame(root, padding=10)
input_frame.pack(fill='x')

# Time, Activity, and Budget Input
time_frame = ttk.Frame(input_frame)
time_frame.pack(fill='x', pady=2)

ttk.Label(time_frame, text="เวลา").pack(side='left', padx=(0, 5))
time_combobox = ttk.Combobox(time_frame, values=time_options, width=10)
time_combobox.pack(side='left')

ttk.Label(time_frame, text="กิจกรรม").pack(side='left', padx=(10, 5))
detail_entry = ttk.Entry(time_frame, width=30)
detail_entry.pack(side='left')

ttk.Label(time_frame, text="งบ (บาท)").pack(side='left', padx=(10, 5))
budget_entry = ttk.Entry(time_frame, width=10)
budget_entry.pack(side='left')

# Image Input
image_frame = ttk.Frame(input_frame)
image_frame.pack(fill='x', pady=5)
image_path = tk.StringVar()
ttk.Button(image_frame, text="📷 เลือกภาพ (ไม่บังคับ)", command=browse_image, style="secondary.TButton").pack(side='left', pady=5)
image_label = ttk.Label(image_frame, text="ไม่มีไฟล์เลือก", wraplength=300)
image_label.pack(side='left', padx=5)

# Add and Import Buttons
action_frame = ttk.Frame(root)
action_frame.pack(pady=10)
ttk.Button(action_frame, text="➕ เพิ่มกิจกรรม", command=add_activity, style="success.TButton").pack(side='left', padx=5)
ttk.Button(action_frame, text="📂 นำเข้าไฟล์", command=import_schedule, style="warning.TButton").pack(side='left', padx=5)
ttk.Button(action_frame, text="🗑️ ลบรายการที่เลือก", command=delete_selected_activities, style="danger.TButton").pack(side='left', padx=5)

# Activity Table
table_frame = ttk.Frame(root)
table_frame.pack(fill='both', expand=True, padx=10, pady=10)

activity_table = ttk.Treeview(table_frame, columns=("Time", "Detail", "Budget", "Image", "Action"), show="headings", height=10, selectmode="extended")
activity_table.heading("Time", text="เวลา")
activity_table.heading("Detail", text="กิจกรรม")
activity_table.heading("Budget", text="งบประมาณ (บาท)")
activity_table.heading("Image", text="รูปภาพ")
activity_table.heading("Action", text="ลบ")
activity_table.column("Time", width=100, anchor="center")
activity_table.column("Detail", width=250)
activity_table.column("Budget", width=100, anchor="center")
activity_table.column("Image", width=50, anchor="center")
activity_table.column("Action", width=50, anchor="center")

# Scrollbar
scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=activity_table.yview)
activity_table.configure(yscrollcommand=scrollbar.set)
activity_table.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# Total Budget Label
total_budget_label = ttk.Label(root, text="💰 งบประมาณรวม: 0.00 บาท", font=('TH Sarabun New', 14), bootstyle="primary")
total_budget_label.pack(pady=5)

# Bottom Buttons
button_frame = ttk.Frame(root)
button_frame.pack(pady=10)
ttk.Button(button_frame, text="👁 ดูตัวอย่าง", command=review_schedule, style="info.TButton").pack(side='left', padx=5)
ttk.Button(button_frame, text="💾 บันทึก", command=save_and_print, style="primary.TButton").pack(side='left', padx=5)

# เริ่มโปรแกรม
root.mainloop()