**Book Management System**
==========================

**Project Overview**
--------------------

The **Book Management System** is a RESTful API built using **FastAPI** and **MySQL**. It provides a platform for administrators to manage books and allows users to borrow and return books. The system includes secure authentication, role-based access control, and additional features like search and filtering.

Complete By - Sarita Joshi

**Features**
------------

### Core Features

-   **CRUD Operations**:
    -   Create, Read, Update, and Delete books (Admin only).

### Extra Features

-   **User Authentication**:
    -   Secure login using JWT tokens.
    -   Passwords are hashed before storage.
-   **Role-Based Access Control**:
    -   **Admins**: Manage books (CRUD operations).
    -   **Users**: Borrow and return books.
-   **Search and Filtering**:
    -   Search for books by title or author.
    -   Filter books by genre and publication year.
-   **Borrowing and Returning Books**:
    -   Users can borrow books with a 14-day due date.
    -   Return books to make them available for others.
-   **Batch Creation of Books**:
    -   Supports adding multiple books in a single request.
    -   Logs errors for failed inserts while processing valid entries.



**Technologies Used**
---------------------

-   **Backend Framework**: FastAPI
-   **Database**: MySQL (SQLAlchemy ORM)
-   **Security**: JWT Authentication, bcrypt for password hashing
-   **Testing Tool**: Postman
-   **Dependencies**:
    -   `fastapi`
    -   `uvicorn`
    -   `sqlalchemy`
    -   `pydantic`
    -   `mysql-connector-python`
    -   `passlib`
    -   `python-jose`



**System Flow**
---------------

1.  **User Registration and Login**:

    -   Users can sign up with a username, password, and role (`admin` or `user`).
    -   JWT tokens are generated upon successful login.
2.  **Book Management**:

    -   Admins can perform CRUD operations for books.
3.  **Search and Filter Books**:

    -   Books can be searched using title/author keywords or filtered by genre/year.
4.  **Borrow and Return Books**:

    -   Users can borrow books if available and return them after reading.
    -   Borrowed books are tracked with a due date.
5.  **Batch Book Creation**:

    -   Multiple books can be added in a single request with error handling for invalid entries.



**Setup Instructions**
----------------------

### Prerequisites

-   Python 3.8 or higher
-   MySQL installed and running
-   Postman (for testing)



### Steps to Run the Project

1.  **Clone the Repository**:

    bash

    Copy code

    `git clone <your-repo-link>
    cd book-management-system`

2.  **Install Dependencies**:

    bash

    Copy code

    `pip install fastapi uvicorn sqlalchemy mysql-connector-python passlib[bcrypt] python-jose pydantic`

3.  **Configure the MySQL Database**:

    -   Create a MySQL database named `book_db`.
    -   Update the database URL in the code:

        python

        Copy code

        `DATABASE_URL = "mysql+mysqlconnector://root:<password>@127.0.0.1:3306/book_db"`

4.  **Run the Application**:

    bash

    Copy code

    `uvicorn app:app --reload`

5.  **Access the API**:

    -   Open `http://127.0.0.1:8000/docs` in your browser to explore the API documentation.



**API Endpoints**
-----------------

### **Authentication**

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/register/` | Register a new user |
| POST | `/login/` | Authenticate and get JWT |

### **Book Management**

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/books/` | Retrieve all books with filters |
| POST | `/books/` | Create one or multiple books (Admin only) |
| PUT | `/books/{id}` | Update a book (Admin only) |
| DELETE | `/books/{id}` | Delete a book (Admin only) |

### **Borrowing Books**

| Method | Endpoint | Description |
| --- | --- | --- |
| POST | `/borrow/` | Borrow a book (User) |
| POST | `/return/` | Return a borrowed book (User) |


**Database Schema**
-------------------

### Users Table (`users`)

| Column | Type | Description |
| --- | --- | --- |
| id | INT | Primary Key |
| username | VARCHAR(50) | Unique username |
| hashed_password | VARCHAR | Secure hashed password |
| role | VARCHAR(20) | User role: admin/user |

### Books Table (`books`)

| Column | Type | Description |
| --- | --- | --- |
| id | INT | Primary Key |
| title | VARCHAR(255) | Book title |
| author | VARCHAR(255) | Book author |
| publication_year | INT | Year of publication |
| genre | VARCHAR(100) | Book genre |

### Borrowed Books Table (`borrowed_books`)

| Column | Type | Description |
| --- | --- | --- |
| id | INT | Primary Key |
| book_id | INT | Foreign Key (books.id) |
| user_id | INT | Foreign Key (users.id) |
| due_date | VARCHAR | Due date for return |
| returned | BOOLEAN | Return status |



**Future Improvements**
-----------------------

-   Implement update functionality for books.
-   Add pagination for large datasets.
-   Notify users of overdue books with automated reminders.



**Conclusion**
--------------

This project showcases a robust **Book Management System** with FastAPI and MySQL. It includes CRUD operations, authentication, and advanced features like search, borrowing, and returning books.