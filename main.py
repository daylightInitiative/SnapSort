
from tkinterdnd2 import DND_FILES, TkinterDnD  

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import ImageTk, Image 
from tkinter.simpledialog import askstring
from tkinter import messagebox
import hashlib
import shlex
import shutil
import os

# Create main window
root = TkinterDnD.Tk() # VERY IMPORTANT! do not use tk.Tk()!!!!
root.title("SnapSort - Drag & Drop Image Organizer")
root.geometry("600x450")
root.minsize(500, 400)

# ---- Top Frame: Folder Selection ----
top_frame = tk.Frame(root, padx=10, pady=10)
top_frame.pack(fill="x")

folder_label = tk.Label(top_frame, text="📂 Folder:")
folder_label.pack(side="left")

folder_path = tk.StringVar()

folder_entry = tk.Entry(top_frame, textvariable=folder_path, width=40, state="readonly")
folder_entry.pack(side="left", padx=5)

def browse_folder():
    path = filedialog.askdirectory()
    if path:
        folder_path.set(path)
        #print(f"Set the new folder path to {folder_path.get()}")
        folder_entry.configure(state="normal")
        folder_entry.xview_moveto(1.0)  # Scroll to the far right
        folder_entry.configure(state="readonly")

browse_btn = ttk.Button(top_frame, text="Select Folder", command=browse_folder)
browse_btn.pack(side="left")

# ---- Middle Frame: Category & Buttons ----
middle_frame = tk.LabelFrame(root, text="🖼️ Drop Area", padx=10, pady=10, height=200)
middle_frame.pack(fill="both", expand=True, padx=10, pady=5)

drop_label = tk.Label(middle_frame, text="(Drop images here)", fg="gray")
drop_label.pack(pady=5)

# ---- Preview Section ----
preview_frame = tk.Frame(middle_frame)
preview_frame.pack(pady=10)

thumbnail = tk.Label(preview_frame, text="[Image Preview]")
thumbnail.pack(side="left", padx=10)

info_frame = tk.Frame(preview_frame)
info_frame.pack()

filename_label = tk.Label(info_frame, text="", height=1)
filename_label.pack(side="top", ipady=15)

dimensions_label = tk.Label(info_frame, text="", justify="left")
dimensions_label.pack(side="top")

filesize_label = tk.Label(info_frame, text="", justify="left")
filesize_label.pack(side="top")#side="bottom")

# ---- Bottom Frame: Category & Buttons ----
bottom_frame = tk.Frame(root, pady=10)
bottom_frame.pack(fill="x")

category_label = tk.Label(bottom_frame, text="Categorize as:")
category_label.pack(side="left", padx=(10, 5))

snap_categories = ["Screenshots", "Camera Roll"]



category_var = tk.StringVar()
category_dropdown = ttk.Combobox(bottom_frame, textvariable=category_var, values=snap_categories)
category_dropdown.pack(side="left")

def add_category():
    category_name = askstring("Create new category type", "Enter new Category Name:")
    if category_name and len(category_name) > 0:

        if not category_name in snap_categories:
            #print("created new category: ", category_name)
            snap_categories.append(category_name)
            category_dropdown.config(values=snap_categories)
            category_dropdown.set(category_name)

        else:
            messagebox.showerror("Create category", "Category already exists")


def checksum(file) -> str:
    with open(file, "rb") as f:
        file_hash = hashlib.md5()
        while chunk := f.read(8192):
            file_hash.update(chunk)
        return file_hash.hexdigest()

# Ensure secure file transferring
def safe_file_move(src_path, dest_path) -> bool: # if the transfer was successful
    # copy the file, get a checksum and then delete the original if they are the same.

    try:
        
        if not os.path.exists(src_path) or not os.path.exists(dest_path):
            return False

        src_checksum = checksum(src_path)
        file_copy = shutil.copy2(src_path, dest_path)
        # shutil.copy2 preserves metadata (vital for some pictures)
        
        dest_checksum = checksum(file_copy)

        # fail early
        if src_checksum != dest_checksum:
            messagebox.showinfo("Move file", "File copying interrupted, original did not match the copy.")
            os.remove(file_copy)
            return False
        
        # if it copied successfully delete the original
        os.remove(src_path)
        #print("Successfully moved file")
        return True

    except Exception as e:
        print(f"Move file exited with exception: {e}")
        if os.path.exists(dest_path):
            os.remove(dest_path)
        return False


def move_to_category():
    global current_file
    # get the current category
    category_folder_name = category_dropdown.get()

    if category_folder_name and len(queue) > 0:

        # ensure the browse_folder has been set
        if not folder_path.get():
            return messagebox.showinfo("Move to category", "Must set the folder first")

        
        image_folder = os.path.abspath(folder_path.get())

        # create the category folder if it hasnt been created
        #proposed_category_folder_path = image_folder + f"\\{category_folder_name}"
        proposed_category_folder_path = os.path.join(image_folder, category_folder_name)
        if not os.path.exists(proposed_category_folder_path):
            os.mkdir(proposed_category_folder_path)

        # move the file to the new location
        filename = os.path.basename(current_file)

        #destination_path = image_folder + f"\\{category_folder_name}\\{filename}"
        destination_path = os.path.join(image_folder, category_folder_name, filename)
        print(current_file + " -> " + destination_path)

        if destination_path:
            #print("path exists, moving")
            shutil.move(current_file, destination_path)

        clear_button_press()


move_btn = ttk.Button(bottom_frame, text="Move ➤", command=move_to_category)
move_btn.pack(side="left", padx=10)


add_cat_btn = ttk.Button(bottom_frame, text="+ Add Category", command=add_category)
add_cat_btn.pack(side="right", padx=5)

def getFilesizeFmt(bytes):
    a = {0: 'B', 1: 'KB', 2: 'MB', 3: 'GB', 4: 'TB', 5: 'PB', 6: 'EB'}
    index = 0
    numBytes = float(bytes) # bytes can be not a whole number

    # stop if we're under the next unit
    while numBytes >= 1024 and index < len(a) - 1: 
        numBytes /= 1024
        index += 1

    return f"{numBytes:.1f} {a[index]}"

queue = []
current_file = None

def update_current_image():
    global current_file

    if not queue:
        #print("Queue is empty. No image to display.")
        current_file = None
        #thumbnail.config(image="")  # Clear the image
        thumbnail.config(image="", text="[No image loaded]")
        filesize_label.config(text="")
        dimensions_label.config(text="")
        thumbnail.image = None
        return

    current_file = queue[-1] 
    THUMBNAIL_SIZE = (250, 250)

    try:
        with Image.open(current_file) as img:
            width, height = img.size
            dimensions_label.config(text=f"Resolution: {width}x{height}")
            
            img.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
            thumbnail_photoimage = ImageTk.PhotoImage(img)

            thumbnail.config(image=thumbnail_photoimage)
            thumbnail.image = thumbnail_photoimage  # Keep reference
            filename_label.config(text=f"{os.path.basename(current_file)} ({len(queue)} left)")

            filesize = os.path.getsize(current_file)
            filesize_label.config(text=f"Size: {getFilesizeFmt(filesize)}")

            
    except FileNotFoundError:
        print("File not found.")
    except Image.UnidentifiedImageError:
        print("Invalid image file.")
    except Exception as e:
        print(f"Unexpected error: {e}")
  

def drop(event):
    #print("dropped new photo")
    files = shlex.split(event.data)  # Handles multiple files with spaces
    for file in files:

        file = os.path.abspath(file)

        # no duplicates
        filename, file_extension = os.path.splitext(file)
        allowed_filetypes = [".jpeg", ".jpg", ".png", ".webp", ".bmp"]

        if not os.path.exists(file):
            messagebox.showerror("Drag and drop photo", "File does not exist at time of processing.")
            return

        if not os.access(file, os.R_OK):
            messagebox.showerror("Drag and drop photo", "Cannot access file, insufficient permissions")
            return
        
        if not file_extension in allowed_filetypes:
            messagebox.showerror("Drag and drop photo", "Unsupported filetype.")
            return

        if not file in queue:
            print("valid file: " + file)
            queue.append(file)
        else:
            messagebox.showerror("Drag and drop photo", "This photo has already been added to the queue")
            return
    update_current_image()

    
        
def clear_button_press():
    global current_file
    # remove the current_file
    #print(current_file)
    #print(queue, type(current_file))

    if current_file in queue:
        #print("exists in the queue")
        queue.remove(current_file)

    filename_label.config(text="")
    update_current_image()
        
clear_btn = ttk.Button(bottom_frame, text="❌ Clear", command=clear_button_press)
clear_btn.pack(side="right", padx=5)



middle_frame.drop_target_register(DND_FILES)
middle_frame.dnd_bind('<<Drop>>', drop)

try:
    root.mainloop()
except KeyboardInterrupt:
    root.destroy()
except Exception as e:
    print("Unhandled Exception: " + e)
    root.destroy()
