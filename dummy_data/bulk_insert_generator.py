from collections import OrderedDict
import faker

from faker_education import SchoolProvider
from datetime import datetime, timedelta
import random


locales = OrderedDict([
    ('en-US', 2)
])
fake = faker.Faker(locales)
fake.add_provider(SchoolProvider)

content = ""
########################### Operator ###########################
TABLE_NAME = "Operator"
TABLE_COLUMNS = ["Username", "Password", "First_Name", "Last_Name", "Email"]
operators_usernames = []
operators_passwords = []
for i in range(30):
    username = fake.unique.user_name()
    while '.' in username:  # check if the first character is a letter
        username = fake.user_name()
    operators_usernames.append(username)
    password = fake.password(length=8)
    while not password[0].isalpha():  # check if the first character is a letter
        password = fake.password(length=8)
    operators_passwords.append(password)
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.unique.email()
    content += f'("{username}","{password}", "{first_name}", "{last_name}","{email}"),\n'
content = content.rstrip(",\n")
content_operator = f'INSERT INTO {TABLE_NAME} ({", ".join(TABLE_COLUMNS)}) VALUES\n{content};\n'


########################### School ###########################
TABLE_NAME = "School"
TABLE_COLUMNS = ["Name", "Street", "Street_Number", "Postal_Code", "City", "Email", "Phone", "Principal_Full_Name", "Operator_ID"]
postal_codes = [fake.zipcode()[:5] for _ in range(30)]
Schools = []
content_school = ""
for i in range(30):
    name = fake.school_name()
    Schools.append(name)
    street = fake.street_name()
    street_number = random.randint(1, 999)
    postal_code = postal_codes[i]
    city = fake.city()
    email = fake.unique.email()
    phone = str(2100000000 + fake.unique.random_int(min=999999, max=69999999))
    principal_name = fake.name()
    operator_id = i + 1
    content_school += f'("{name}","{street}", "{street_number}", "{postal_code}", "{city}", "{email}", "{phone}", "{principal_name}", "{operator_id}"),\n'
content_school = content_school.rstrip(",\n")
content_school = f'INSERT INTO {TABLE_NAME} ({", ".join(TABLE_COLUMNS)}) VALUES\n{content_school};\n'


########################### Operator_Registration ###########################
TABLE_NAME = "Operator_Registration"
TABLE_COLUMNS = ["Username", "Password", "First_Name", "Last_Name", "Email", "School_Name"]
content_registration = ""
for i in range(5):
    username = fake.unique.user_name()
    while '.' in username:  # check if the first character is a letter
        username = fake.user_name()
    operators_usernames.append(username)
    password = fake.password(length=8)
    while not password[0].isalpha():  # check if the first character is a letter
        password = fake.password(length=8)
    operators_passwords.append(password)
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.unique.email()
    school_name = random.choice(Schools)
    content_registration += f'("{username}","{password}", "{first_name}", "{last_name}","{email}", "{school_name}"),\n'
content_registration = content_registration.rstrip(",\n")
content_registration = f'INSERT INTO {TABLE_NAME} ({", ".join(TABLE_COLUMNS)}) VALUES\n{content_registration};\n'


########################### User ###########################
TABLE_NAME = "User"
TABLE_COLUMNS = ["Username", "Password", "First_Name", "Last_Name", "Email", "School_Name", "Date_of_Birth", "Is_Teacher"]
students_usernames = []
students_passwords = []
teachers_usernames = []
teachers_passwords = []
User_Schools = []
content_user = ""
for i in range(1800):
    username = fake.unique.user_name()
    while '.' in username:  # check if the first character is a letter
        username = fake.user_name()
    students_usernames.append(username)
    password = fake.password()
    while not password[0].isalpha():  # check if the first character is a letter
        password = fake.password(length=8)
    students_passwords.append(password)
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.unique.email()
    school_name = random.choice(Schools)
    User_Schools.append(school_name)
    date_of_birth = fake.date_of_birth(minimum_age=6, maximum_age=18)
    content_user += f'("{username}","{password}","{first_name}","{last_name}","{email}","{school_name}","{date_of_birth}", {False}),\n'

for i in range(200):
    username = fake.unique.user_name()
    while '.' in username:  # check if the first character is a letter
        username = fake.user_name()
    teachers_usernames.append(username)
    password = fake.password()
    while not password[0].isalpha():  # check if the first character is a letter
        password = fake.password(length=8)
    teachers_passwords.append(password)
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.unique.email()
    school_name = random.choice(Schools)
    User_Schools.append(school_name)
    date_of_birth = fake.date_of_birth(minimum_age=22, maximum_age=70)
    content_user += f'("{username}","{password}","{first_name}","{last_name}","{email}","{school_name}","{date_of_birth}", {True}),\n'
content_user = content_user.rstrip(",\n")
content_user = f'INSERT INTO {TABLE_NAME} ({", ".join(TABLE_COLUMNS)}) VALUES\n{content_user};\n'


########################### Pending_Registrations ###########################
TABLE_NAME = "Pending_Registrations"
TABLE_COLUMNS = ["Username", "Password", "First_Name", "Last_Name", "Email", "School_Name", "Date_of_Birth", "Is_Teacher"]
content_pending_registrations = ""
for i in range(40):
    username = fake.unique.user_name()
    while '.' in username:  # check if the first character is a letter
        username = fake.user_name()
    students_usernames.append(username)
    password = fake.password()
    while not password[0].isalpha():  # check if the first character is a letter
        password = fake.password(length=8)
    students_passwords.append(password)
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.unique.email()
    school_name = random.choice(Schools)
    date_of_birth = fake.date_of_birth(minimum_age=6, maximum_age=18)
    content_pending_registrations += f'("{username}","{password}","{first_name}","{last_name}","{email}","{school_name}","{date_of_birth}", {False}),\n'

for i in range(30):
    username = fake.unique.user_name()
    while '.' in username:  # check if the first character is a letter
        username = fake.user_name()
    teachers_usernames.append(username)
    password = fake.password()
    while not password[0].isalpha():  # check if the first character is a letter
        password = fake.password(length=8)
    teachers_passwords.append(password)
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.unique.email()
    school_name = random.choice(Schools)
    date_of_birth = fake.date_of_birth(minimum_age=22, maximum_age=70)
    content_pending_registrations += f'("{username}","{password}","{first_name}","{last_name}","{email}","{school_name}","{date_of_birth}", {True}),\n'
content_pending_registrations = content_pending_registrations.rstrip(",\n")
content_pending_registrations = f'INSERT INTO {TABLE_NAME} ({", ".join(TABLE_COLUMNS)}) VALUES\n{content_pending_registrations};\n'


########################### Administrator ###########################
TABLE_NAME = "Administrator"
TABLE_COLUMNS = ["Username", "Password", "First_Name", "Last_Name", "Email"]

content_administrator = ""
for i in range(5):
    username = fake.unique.user_name()
    while '.' in username:  # check if the first character is a letter
        username = fake.user_name()
    password = fake.password()
    while not password[0].isalpha():  # check if the first character is a letter
        password = fake.password(length=8)
    first_name = fake.first_name()
    last_name = fake.last_name()
    email = fake.unique.email()
    content_administrator += f'("{username}","{password}","{first_name}","{last_name}","{email}"),\n'
content_administrator = content_administrator.rstrip(",\n")
content_administrator = f'INSERT INTO {TABLE_NAME} ({", ".join(TABLE_COLUMNS)}) VALUES\n{content_administrator};\n'


########################### Book ###########################
TABLE_NAME = "Book"
TABLE_COLUMNS = ["ISBN", "Title", "Number_of_Pages", "Publisher", "Language", "Summary"]
isbn_list = set()
while len(isbn_list) < 400:
    isbn_list.add(str(random.randint(1000000000000, 9999999999999)))
content_book = ""
for isbn in isbn_list:
    title = fake.sentence(nb_words=5)
    pages = random.randint(50, 900)
    publisher = fake.company()
    language = random.choice(['Greek', 'English', 'French', 'Spanish'])
    summary = fake.paragraph(nb_sentences=3)
    content_book += f'("{isbn}", "{title}", "{pages}", "{publisher}", "{language}", "{summary}"),\n'

isbn_list2 = set()
while len(isbn_list2) < 15:
    isbn_list2.add(str(random.randint(1000000000000, 9999999999999)))
for isbn in isbn_list2:
    title = fake.sentence(nb_words=5)
    pages = random.randint(50, 900)
    publisher = fake.company()
    language = random.choice(['Greek', 'English', 'French', 'Spanish'])
    summary = fake.paragraph(nb_sentences=3)
    content_book += f'("{isbn}", "{title}", "{pages}", "{publisher}", "{language}", "{summary}"),\n'
content_book = content_book.rstrip(",\n")
content_book = f'INSERT INTO {TABLE_NAME} ({", ".join(TABLE_COLUMNS)}) VALUES\n{content_book};\n'


########################### Author ###########################
TABLE_NAME = "Author"
TABLE_COLUMNS = ["First_Name", "Last_Name"]
content_author = ""
for i in range(160):
    first_name = fake.first_name()
    last_name = fake.last_name()
    content_author += f'("{first_name}","{last_name}"),\n'
content_author = content_author.rstrip(",\n")
content_author = f'INSERT INTO {TABLE_NAME} ({", ".join(TABLE_COLUMNS)}) VALUES\n{content_author};\n'


########################### Book_Author ###########################
TABLE_NAME = "Book_Author"
TABLE_COLUMNS = ["Author_ID", "ISBN"]
books = list(isbn_list)
content_book_author = ""
for isbn in books:
    selected_objects = random.sample(list(range(1, 151)), random.randint(1, 3))
    for author_id in selected_objects:
        content_book_author += f'("{author_id}","{isbn}"),\n'

books2 = list(isbn_list2)
for isbn in books2:
    selected_objects = random.sample(list(range(151,161)),random.randint(1,2))
    for author_id in selected_objects:
        content_book_author += f'("{author_id}","{isbn}"),\n'
content_book_author = content_book_author.rstrip(",\n")
content_book_author = f'INSERT INTO {TABLE_NAME} ({", ".join(TABLE_COLUMNS)}) VALUES\n{content_book_author};\n'


########################### Keyword ###########################
TABLE_NAME = "Keyword"
TABLE_COLUMNS = ["Keyword"]
content_keyword = ""
for i in range(500):
    keyword = fake.unique.word()
    content_keyword += f'("{keyword}"),\n'

content_keyword = content_keyword.rstrip(",\n")
content_keyword = f'INSERT INTO {TABLE_NAME} ({", ".join(TABLE_COLUMNS)}) VALUES\n{content_keyword};\n'


########################### Book_Keyword ###########################
TABLE_NAME = "Book_Keyword"
TABLE_COLUMNS = ["Keyword_ID", "ISBN"]
content_book_keyword = ""
for isbn in books:
    selected_objects = random.sample(list(range(1, 501)), random.randint(1, 5))
    for keyword_id in selected_objects:
        content_book_keyword += f'("{keyword_id}","{isbn}"),\n'
for isbn in books2:
    selected_objects = random.sample(list(range(1,501)),random.randint(1,5))
    for keyword_id in selected_objects:
        content_book_keyword += f'("{keyword_id}","{isbn}"),\n'

content_book_keyword = content_book_keyword.rstrip(",\n")
content_book_keyword = f'INSERT INTO {TABLE_NAME} ({", ".join(TABLE_COLUMNS)}) VALUES\n{content_book_keyword};\n'


########################### Category ###########################
TABLE_NAME = "Category"
TABLE_COLUMNS = ["Genre"]
book_genres = [
    "Science Fiction", "Mystery", "Romance", "Thriller", "Historical Fiction",
    "Fantasy", "Young Adult", "Nonfiction", "Horror", "Memoir", "Biography",
    "Children's", "Poetry", "Self-help", "Business", "Cooking", "Travel",
    "Dystopian", "Crime", "Comics", "Art", "Graphic Novels", "Science",
    "Religion", "Sports"
]
content_category = ""
for genre in book_genres:
    content_category += f'("{genre}"),\n'

content_category = content_category.rstrip(",\n")
content_category = f'INSERT INTO {TABLE_NAME} ({", ".join(TABLE_COLUMNS)}) VALUES\n{content_category};\n'


########################### Book_Category ###########################
TABLE_NAME = "Book_Category"
TABLE_COLUMNS = ["Category_ID", "ISBN"]
content_book_category = ""
for isbn in books:
    selected_objects = random.sample(list(range(1, len(book_genres) + 1)), random.randint(1, 3))
    for category_id in selected_objects:
        content_book_category += f'("{category_id}","{isbn}"),\n'

for isbn in books2:
    selected_objects = random.sample(list(range(1,(len(book_genres)+1))), random.randint(1,3))
    for category_id in selected_objects:
        content_book_category += f'("{category_id}","{isbn}"),\n'

content_book_category = content_book_category.rstrip(",\n")
content_book_category = f'INSERT INTO {TABLE_NAME} ({", ".join(TABLE_COLUMNS)}) VALUES\n{content_book_category};\n'


########################### School_Books ###########################
TABLE_NAME = "School_Books"
TABLE_COLUMNS = ["School_Name", "ISBN", "Available_Copies"]
School_Books_List = {}
content_school_books = ""
for school in Schools:
    selected_books = random.sample(books, random.randint(20, 100))
    School_Books_List[school] = selected_books
    for isbn in selected_books:
        available_copies = random.randint(0, 30)
        content_school_books += f'("{school}","{isbn}", "{available_copies}"),\n'


for school in Schools:
    selected_books = random.sample(books2, random.randint(0,3))
    for isbn in selected_books:
        available_copies = random.randint(0,30)
        content_school_books += f'("{school}","{isbn}", "{available_copies}"),\n'

content_school_books = content_school_books.rstrip(",\n")
content_school_books = f'INSERT INTO {TABLE_NAME} ({", ".join(TABLE_COLUMNS)}) VALUES\n{content_school_books};\n'


########################### Book_Reservation ###########################
today = datetime.now().date()
TABLE_NAME = "Book_Reservation"
TABLE_COLUMNS = ["ISBN","User_ID","Reservation_Date","Is_Rented"]
content_reservation = ""
# Get a subset of users
selected_users = random.sample(list(range(1,2001)), 300)
for user_id in selected_users:
    # Assign the user's school based on the User_School_List
    user_school = User_Schools[user_id-1]
    isbn = random.choice(School_Books_List[user_school])
    start_date = today - timedelta(days=7)
    reservation_date = fake.date_between(start_date=start_date, end_date=today)
    is_rented = random.choice([True,False])
    content_reservation += f'("{isbn}","{user_id}", "{reservation_date}", {is_rented}),\n'

content_reservation = content_reservation.rstrip(",\n")
content_reservation = f'INSERT INTO {TABLE_NAME} ({", ".join(TABLE_COLUMNS)}) VALUES\n{content_reservation};\n'


########################### Rental ###########################
TABLE_NAME = "Rental"
TABLE_COLUMNS = ["ISBN", "User_ID", "Rental_Date", "Return_Date"]
user_rental_weeks = {}
rented_books = {user_id: [] for user_id in range(1, 2001)}
content_rental = ""

def check_rental_week(user, rental_date):
    # Generate dates 7 days before and after rental_date

    
    if user in user_rental_weeks:
        for rental in user_rental_weeks[user]:
            start_date = rental - timedelta(days=7)
            end_date = rental + timedelta(days=7)
            if (start_date <= rental_date)  and (rental_date <= end_date):
                return True
    
    if user not in user_rental_weeks:
        user_rental_weeks[user] = set()
    user_rental_weeks[user].add(rental_date)
    return False

for user in range(1, 2001):
    school = User_Schools[user - 1]
    available_books = School_Books_List[school]
    selected_books = random.sample(available_books, min(len(available_books), random.randint(0, 10)))
    for isbn in selected_books:
        end_date = today - timedelta(days=7)
        rental_date = fake.date_between(start_date='-4y', end_date=end_date)
        if check_rental_week(user, rental_date):
            continue
        return_date = rental_date + timedelta(days=random.randint(1, 30))
        if return_date > today:
            return_date = today
        content_rental += f'("{isbn}","{user}", "{rental_date}", "{return_date}"),\n'
        rented_books[user].append(isbn)

selected_users = random.sample(list(range(1, 2001)), 400)

# Subset of users for the first operation
selected_users_1 = selected_users[:100]

# For each user in the first subset, select a book and generate a rental date from the past year
for user in selected_users_1:  
    school = User_Schools[user-1]  # get the school for this user
    available_books = School_Books_List[school]  # get the list of books for this school
    selected_books = random.sample(available_books, 1)  # select some of the available books
    for isbn in selected_books:
        rental_date = fake.date_between(start_date='-1y', end_date='today')
        if check_rental_week(user, rental_date):
            continue
        content_rental += f'("{isbn}","{user}", "{rental_date}", NULL),\n'
        rented_books[user].append(isbn)


# Subset of users for the second operation
selected_users_2 = selected_users[100:400]

# For each user in the second subset, select another book and generate a rental date from the past week
for user in selected_users_2:  
    school = User_Schools[user-1]  # get the school for this user
    available_books = School_Books_List[school]  # get the list of books for this school
    selected_books = random.sample(available_books, 1)  # select some of the available books
    start_date = today - timedelta(days=7)
    rental_date = fake.date_between(start_date=start_date, end_date='today')
    if check_rental_week(user, rental_date):
        continue
    content_rental += f'("{isbn}","{user}", "{rental_date}", NULL),\n'
    rented_books[user].append(isbn)
content_rental = content_rental.rstrip(",\n")
content_rental = f'INSERT INTO {TABLE_NAME} ({", ".join(TABLE_COLUMNS)}) VALUES\n{content_rental};\n'


########################### Published_Book_Review ###########################
TABLE_NAME = "Published_Book_Review"
TABLE_COLUMNS = ["ISBN", "User_ID", "Review_Text", "Review_Date", "Likert_Review"]
selected_users = random.sample(list(range(1, 2001)), 1500)
content_published_review = ""
for user_id in selected_users:
    user_school = User_Schools[user_id - 1]
    if user_school in School_Books_List:
        book_list = [isbn for isbn in School_Books_List[user_school] if isbn in rented_books[user_id]]
        isbns = random.sample(book_list, min(len(book_list), random.randint(3, 10)))
        for isbn in isbns:
            review_text = fake.text(max_nb_chars=1000)
            review_date = fake.date_between(start_date='-4y', end_date=today)
            likert_review = random.choice(['1', '2', '3', '4', '5'])
            content_published_review += f'("{isbn}","{user_id}", "{review_text}", "{review_date}", "{likert_review}"),\n'

content_published_review = content_published_review.rstrip(",\n")
content_published_review = f'INSERT INTO {TABLE_NAME} ({", ".join(TABLE_COLUMNS)}) VALUES\n{content_published_review};\n'


########################### Book_Review ###########################
TABLE_NAME = "Book_Review"
TABLE_COLUMNS = ["ISBN", "User_ID", "Review_Text", "Review_Date", "Likert_Review"]
selected_users = random.sample(list(range(1, 2001)), 210)
content_review = ""
for user_id in selected_users:
    user_school = User_Schools[user_id - 1]
    if user_school in School_Books_List:
        book_list = [isbn for isbn in School_Books_List[user_school] if isbn in rented_books[user_id]]
        isbns = random.sample(book_list, min(len(book_list), random.randint(0, 2)))
        for isbn in isbns:
            review_text = fake.text(max_nb_chars=1000)
            review_date = fake.date_between(start_date='-4y', end_date=today)
            likert_review = random.choice(['1', '2', '3', '4', '5'])
            content_review += f'("{isbn}","{user_id}", "{review_text}", "{review_date}", "{likert_review}"),\n'

content_review = content_review.rstrip(",\n")
content_review = f'INSERT INTO {TABLE_NAME} ({", ".join(TABLE_COLUMNS)}) VALUES\n{content_review};\n'



# Combine all content into a single string
content = content_operator + content_school + content_registration + content_user + content_pending_registrations + content_administrator + content_book + content_author + content_book_author + content_keyword + content_book_keyword + content_category + content_book_category + content_school_books + content_reservation + content_rental + content_published_review + content_review 


# Write the content to the file
with open("database_content.sql", "w") as file:
    file.write(content)
