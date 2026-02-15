# 📅 Event Planner - Python Desktop Application

**Event Planner** is a robust desktop management tool developed in Python, designed to help users organize, track, and receive notifications for their scheduled events and tasks. The application features a modular architecture and uses a local database for persistent data storage.

## 🛠️ Tech Stack & Technologies
The project leverages a modern Python stack for desktop development:
* **Language**: Python 3.x (100% codebase)
* **GUI Framework**: `Tkinter` with `tkcalendar` integration for seamless date selection
* **Database**: `SQLite` for reliable local data persistence
* **Task Scheduling**: The `schedule` library for real-time alert management
* **Notifications**: `plyer` for triggering native system-level desktop alerts

## 📂 Project Structure
The repository follows a clean, modular structure for easy maintenance:

* **app.py**: The main entry point containing the GUI logic and core application flow
* **database.py**: Handles SQL queries and the SQLite database connection
* **models.py**: Defines the data structures and objects used throughout the app
* **notifications.py**: Manages the background scheduling and delivery of notifications
* **reports.py**: Logic for generating and viewing event-based reports
* **utils.py**: Helper functions for data processing and formatting
* **themes.py**: Customization logic for UI appearance (Dark/Light modes)
* **requirements.txt**: List of dependencies required to run the environment

## 🚀 Key Features
1. **Full CRUD Operations**: Create, read, update, and delete events with specific details
2. **Automated Alerts**: Real-time desktop notifications for upcoming events
3. **JSON Import/Export**: Capability to transfer and backup event data using structured JSON files
4. **UI Customization**: Support for different visual themes to enhance user experience

## 🔧 Installation
1. Clone the repository:
   ```bash
  git clone https://github.com/stefandaniel98/Event-Planner.git
  
2. Install dependencies:
   pip install -r requirements.txt

3. Run the application:
   python app.py
