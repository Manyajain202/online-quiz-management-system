                            ONLINE QUIZ MANAGEMENT SYSTEM
                         Project README / Reference Document
Online Quiz Management System
A web-based Online Quiz Management System developed using Flask, SQLite, HTML5, CSS3, and JavaScript. The application provides student registration and login, quiz participation, timed quizzes, automatic score calculation, result display, result storage, and an administrator interface for creating quizzes and questions.
Features
•	Student Registration and Login
•	Student Dashboard
•	Quiz Listing and Selection
•	Timed Online Quizzes
•	Multiple-Choice Questions
•	Automatic Score Calculation
•	Percentage Calculation
•	Result Display
•	Result Storage in SQLite
•	Quiz History / Results
•	Admin Login
•	Admin Dashboard
•	Create Quiz and Add Questions
•	Quiz Duration Setting
•	Responsive Pink/Rose Interface
•	SQLite Database Storage
Tech Stack
Frontend
•	HTML5
•	CSS3
•	JavaScript
Backend
•	Python
•	Flask
Database
•	SQLite
Project Structure
Online-Quiz-Management-System/
│── index.html
│── style.css
│── script.js
│── backend/
│   ├── app.py
│   └── quiz.db (created automatically when the application runs)
│── pages/
│   ├── login.html
│   ├── register.html
│   ├── student-dashboard.html
│   ├── quiz.html
│   ├── result.html
│   ├── admin-dashboard.html
│   └── create-quiz.html
Database Tables
The system uses SQLite to store user, quiz, question, and result information.
Table	Important Fields
Users	User ID, Name, Email, Password, Role
Quizzes	Quiz ID, Title, Description, Duration
Questions	Question ID, Quiz ID, Question Text, Options, Correct Answer
Results	Result ID, User ID, Quiz ID, Score, Total, Percentage, Time Taken
Application Workflow
1. Open the application
2. Register a student account
3. Login using registered credentials
4. Open the Student Dashboard
5. Select an available quiz
6. Read and answer the questions
7. Complete the quiz within the displayed time limit
8. Submit the quiz
9. Calculate the score and percentage automatically
10. Display the result
11. Store the result in the SQLite database
12. Admin can login and create quizzes/questions
API Integration
The application uses Flask routes and JSON API endpoints to connect the frontend with the backend and SQLite database. The main operations include registration, login, logout, retrieving quizzes, creating quizzes, and saving quiz results.
Example flow:
User Action
↓
JavaScript Request
↓
Flask API Route
↓
SQLite Database
↓
JSON Response
↓
Update Web Page
Core functionality does not require an external API; it works using Flask, JavaScript, and SQLite.
User Interface
•	Navigation Bar
•	Dashboard Cards
•	Quiz Cards
•	Question and Option Forms
•	Live Quiz Timer
•	Score Display
•	Result Summary
•	Admin Dashboard
•	Quiz Creation Form
•	Responsive Pink/Rose Design
Installation
1. Download or extract the project.
2. Open the project folder in Visual Studio Code.
3. Open the terminal and go to the backend folder:
cd backend
4. Start the Flask application:
python app.py
5. Open the application in your browser:
http://127.0.0.1:5000/
The SQLite database and default quiz data are initialized by the Flask application when required.
Default Admin Login
Email: admin@quizmaster.com
Password: admin123
Screenshots

<img width="1280" height="768" alt="quiz (1)" src="https://github.com/user-attachments/assets/6c3c960f-10c3-4264-a359-17e7f9a6ea35" />
<img width="1266" height="754" alt="quiz (2)" src="https://github.com/user-attachments/assets/1d465bd5-601c-42af-98a0-8b6b85acf986" />
<img width="1280" height="768" alt="quiz (3)" src="https://github.com/user-attachments/assets/bed89393-802c-4f90-9ba7-f47a52c7b899" />
<img width="1280" height="768" alt="quiz (4)" src="https://github.com/user-attachments/assets/2e43332b-064f-42e6-a556-902f0dad5ddb" />




Future Enhancements
•	Quiz editing and deletion
•	Question editing
•	More detailed student performance analytics
•	Leaderboard
•	Category-wise quizzes
•	Email notifications
•	PDF result reports
•	Deployment to a public hosting platform
Learning Outcomes
•	Python programming
•	Flask web application development
•	HTML and CSS
•	JavaScript and frontend-backend communication
•	SQLite database management
•	REST-style API development
•	User authentication and sessions
•	Quiz and result management
Author
Student Name: Manya jain
Course: BCA
Project: Online Quiz Management System
Technologies: Python | Flask | SQLite | HTML | CSS | JavaScript
GitHub
https://github.com/Manyajain202/online-quiz-management-system
License
This project is developed for educational, academic, internship, and portfolio purposes.
