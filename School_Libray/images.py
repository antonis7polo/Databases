import os
import requests
import mysql.connector

connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='your password',      
        database='School_Library_New'
)

cursor = connection.cursor()

# Folder to store images
IMG_FOLDER = "/your/full/path/to/static/images"

# Ensure the directory exists
os.makedirs(IMG_FOLDER, exist_ok=True)

# Fetch ISBNs from the Book table
cursor.execute("SELECT ISBN FROM Book")
books = cursor.fetchall()

for book in books:
    isbn = book[0]

    # Generate the URL for a random image from Lorem Picsum
    url = f"https://picsum.photos/200/300?random={isbn}"

    # Fetch the image data
    response = requests.get(url)

    # Save the image to a file
    img_file_path = os.path.join(IMG_FOLDER, f"{isbn}.jpg")
    with open(img_file_path, 'wb') as img_file:
        img_file.write(response.content)

    # Update the Image_URL field in the Book table
    image_url = f"images/{isbn}.jpg"
    cursor.execute(f"UPDATE Book SET Image_URL = '{image_url}' WHERE ISBN = '{isbn}'")
    connection.commit()
