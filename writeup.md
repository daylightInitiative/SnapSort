# SnapSort writeup

If you plan to use tkdnd make sure to use `TkinterDnd.Tk()` and NOT the traditional `tk.Tk()` you will get errors like this ```self.tk.call('tkdnd::drop_target', 'register', self._w, dndtypes)
_tkinter.TclError: invalid command name "tkdnd::drop_target"```
```python
from tkinterdnd2 import DND_FILES, TkinterDnD

# Create main window
root = TkinterDnD.Tk() # VERY IMPORTANT! do not use tk.Tk()!!!!
root.title("SortSnap - Drag-and-Drop Image Organizer")
root.geometry("600x450")
root.minsize(500, 400)
```

Secure copy code snippet
# Ensure secure file transferring
Using a checksum to safely move a file is ideal
```python
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
        print("Successfully moved file")
        return True

    except Exception as e:
        print(f"Move file exited with exception: {e}")
        if os.path.exists(dest_path):
            os.remove(dest_path)
        return False
  ```

# create the category folder if it hasnt been created
instead of manually creating the path you can use `os.path.join` for cross platform compatibility
```python
#proposed_category_folder_path = image_folder + f"\\{category_folder_name}"
proposed_category_folder_path = os.path.join(image_folder, category_folder_name)
```
