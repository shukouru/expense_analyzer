# Expense Pattern Analyzer

Expense Pattern Analyzer is a Flask web application that helps users track their daily expenses and analyze their spending patterns.  
The app includes user authentication, expense management, budget tracking, spending alerts, and data visualizations.

## Features

- User registration, login, and logout
- User-specific expense data
- Add, edit, and delete expenses
- Move expenses to trash
- Restore expenses from trash
- Permanently delete expenses
- Search expenses by memo
- Filter expenses by category
- Sort expenses by date or amount
- Monthly budget setting
- Budget progress tracking
- Recommended daily spending calculation
- Monthly spending comparison
- Next month spending prediction
- Unusual spending alert
- Category breakdown
- Radar chart, bar chart, and line chart using Chart.js
- Responsive CSS layout

## Tech Stack

- Python
- Flask
- SQLite
- HTML
- CSS
- Chart.js
- Flask-Login
- Werkzeug Security

## Project Purpose

The purpose of this project is to build a practical web application that combines backend development, database management, authentication, and basic data analysis.
Unlike a simple expense tracker, this app focuses on analyzing spending behavior. It helps users understand where their money goes, compare monthly spending, track progress toward a budget, and predict next month’s spending based on recent data.

## Data Analysis Features

This app includes several data-focused features:

### Monthly Comparison

The dashboard compares this month’s spending with last month’s spending and shows the difference and percentage change.

### Budget Progress

Users can set a monthly budget. The app calculates:

- Total amount spent this month
- Remaining budget
- Percentage of budget used
- Recommended daily spending for the rest of the month

### Next Month Prediction

The app predicts next month’s spending based on the average spending from recent months.

### Unusual Spending Alert

Expenses that are much higher than the user’s average expense are marked as high spending.

### Data Visualization

The dashboard uses Chart.js to visualize spending data with:

- Radar chart for category balance
- Bar chart for category totals
- Line chart for monthly spending trends

## Screenshots

Add screenshots here:
<img width="1500" height="732" alt="スクリーンショット 2026-05-10 午後3 58 38" src="https://github.com/user-attachments/assets/76c5cb68-9737-4fee-a84c-1ad321843237" />
<img width="1501" height="777" alt="スクリーンショット 2026-05-10 午後3 58 26" src="https://github.com/user-attachments/assets/cf6c0fe6-3a38-418b-a528-4be1481b331f" />
<img width="1282" height="820" alt="スクリーンショット 2026-05-10 午後3 58 14" src="https://github.com/user-attachments/assets/2aeaeb17-baf4-4410-af41-b98fa6d8b738" />


```text
screenshots/dashboard.png
screenshots/expenses.png
screenshots/login.png
