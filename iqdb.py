import tkinter as tk
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
import requests
import webbrowser
from bs4 import BeautifulSoup
import threading
import os
import tempfile


def drop(event):
    global temp_file_path
    # Clear the image label
    image_label.config(image='', text='')

    file_path = event.data
    global file_path_clean
    file_path_clean = file_path.replace('{', '').replace('}', '').replace(';', '')

    try:
        # Check if the file is a webp image
        if file_path_clean.lower().endswith('.webp'):
            # Convert webp to jpg and save in a temporary folder
            with Image.open(file_path_clean) as img:
                temp_dir = tempfile.gettempdir()
                temp_file_path = os.path.join(temp_dir, 'temp_image.jpg')
                img.convert('RGB').save(temp_file_path, 'JPEG')
                file_path_clean = temp_file_path

        # Try to open the image file
        img = Image.open(file_path_clean)
        img.thumbnail((root.winfo_width(), root.winfo_height() - 100))  # Resize image to fit the window
        img_tk = ImageTk.PhotoImage(img)

        # Display the image in the label
        image_label.config(image=img_tk)
        image_label.image = img_tk  # Keep a reference to avoid garbage collection
    except Exception as e:
        image_label.config(text="Failed to open image")
        print(f"Failed to open image: {e}")


def resize_image(event):
    if hasattr(image_label, 'image') and image_label.image:
        try:
            # Open the image file
            img = Image.open(file_path_clean)

            # Get the new dimensions of the image_label
            label_width = image_label.winfo_width()
            label_height = image_label.winfo_height()

            # Resize image to fit the label while maintaining aspect ratio
            img.thumbnail((label_width, label_height))
            img_tk = ImageTk.PhotoImage(img)

            # Display the resized image in the label
            image_label.config(image=img_tk)
            image_label.image = img_tk  # Keep a reference to avoid garbage collection
        except Exception as e:
            image_label.config(text="Failed to resize image")
            print(f"Failed to resize image: {e}")


def process_image():
    global processing
    processing = True
    show_loading_indicator()  # Show loading indicator while processing
    link_label.config(text="")  # Clear the link label text
    if file_path_clean:
        try:
            # Open the image file
            with open(file_path_clean, 'rb') as f:
                files = {'file': f}
                response = requests.post('https://iqdb.org/', files=files)
                response.raise_for_status()  # Check if the request was successful
            # Get the response text
            response_text = response.text
            show_best_match(response_text)
        except requests.RequestException as e:
            print(f"Error uploading image: {e}")
        finally:
            processing = False
            hide_loading_indicator()


def show_loading_indicator():
    global loading_text_id
    loading_text_id = root.after(0, update_loading_indicator, 0)


def update_loading_indicator(index):
    # Update the loading text animation
    if processing:
        dots = '.' * (index % 4)
        loading_label.config(text=f"Processing{dots}")
        root.after(500, update_loading_indicator, (index + 1) % 4)
    else:
        loading_label.config(text="")


def hide_loading_indicator():
    global loading_text_id
    if loading_text_id is not None:
        root.after_cancel(loading_text_id)
        loading_text_id = None


def show_best_match(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')

    # Locate the "Best match" section
    best_match_section = soup.find(string='Best match')
    if best_match_section:
        # Navigate to the parent table row and find the link
        best_match_row = best_match_section.find_parent('tr')
        if best_match_row:
            # Look for an anchor tag within the same row
            link_tag = best_match_row.find_next('a', href=True)
            if link_tag:
                img_link = link_tag.get('href')
                if img_link:
                    print(img_link)
                    # Update the link label text and make it clickable
                    link_label.config(text="Best match found: Click here", fg="blue", cursor="hand2")
                    link_label.bind("<Button-1>", lambda e: open_in_browser("http:" + img_link))
                else:
                    print("No href attribute found in the 'Best match' row link.")
                    link_label.config(text="No href attribute found in the 'Best match' row link.")
            else:
                print("No link tag found in the 'Best match' row.")
                link_label.config(text="No link tag found in the 'Best match' row.")
        else:
            print("No table row found for 'Best match'.")
            link_label.config(text="No table row found for 'Best match'.")
    else:
        print("No 'Best match' section found in the HTML content.")
        link_label.config(text="No 'Best match' section found in the HTML content.")


def on_button_click():
    threading.Thread(target=process_image, daemon=True).start()


def open_in_browser(url):
    webbrowser.open(url)


def toggle_always_on_top():
    if always_on_top_var.get():
        root.attributes('-topmost', 1)  # Make the window always on top
    else:
        root.attributes('-topmost', 0)  # Allow the window to be behind other windows


def delete_temp_image():
    global temp_file_path
    if temp_file_path and os.path.exists(temp_file_path):
        os.remove(temp_file_path)
        temp_file_path = None


root = TkinterDnD.Tk()  # Use TkinterDnD.Tk instead of tk.Tk
root.title("IQDB Image Search")
root.geometry("400x400")


image_label = tk.Label(root, text="Drop an image here", width=50, height=15, relief="solid")
image_label.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)
# Bind the resize function to the <Configure> event of the image_label
image_label.bind('<Configure>', resize_image)

button = tk.Button(root, text="Search", command=on_button_click, font=("Helvetica", 10, "bold"))
button.pack(pady=10)

# Add a label for the link above the button
link_label = tk.Label(root, text="", font=("Helvetica", 10, "underline"))
link_label.pack(pady=5)

# Add a label for the loading indicator
loading_label = tk.Label(root, text="", font=("Helvetica", 10))
loading_label.pack(pady=10)

# Add a checkbox to toggle "Always on Top"
always_on_top_var = tk.BooleanVar()
always_on_top_checkbox = tk.Checkbutton(root, text="Always on Top", variable=always_on_top_var,
                                        command=toggle_always_on_top)
always_on_top_checkbox.pack(pady=5)

# Initialize processing flag and loading indicator
processing = False
loading_text_id = None

root.drop_target_register(DND_FILES)
root.dnd_bind('<<Drop>>', drop)

# Ensure the temporary image is deleted when the application closes
temp_file_path = None
root.protocol("WM_DELETE_WINDOW", lambda: [delete_temp_image(), root.destroy()])

root.mainloop()