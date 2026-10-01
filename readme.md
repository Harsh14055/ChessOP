# ♟️ ChessOP

**ChessOP** is a feature-rich, real-time multiplayer chess web application built with **Django**, **Django Channels**, **WebSockets**, and **Python-Chess**.

It provides an interactive chess experience with real-time multiplayer games, matchmaking, live chat, authentication, Elo rating updates, and dedicated chess-training tools — all wrapped in a modern dark UI inspired by platforms such as Lichess and Chess.com.

---

## ✨ Features

### ♟️ Real-Time Multiplayer

* Instant move synchronization using **WebSockets**
* Automatic turn validation
* Server-side chess move validation
* Real-time in-game chat
* Live game-state updates

### 🎯 Smart Matchmaking Lobby

* Browse available games through an open lobby
* Join games in real time
* Live player-slot management
* Join/leave notifications
* Automatic cleanup of abandoned or stale rooms

### 🔐 Authentication & Profiles

* User registration
* Secure login/logout workflows
* Persistent user profiles
* Player-specific game and rating information

### 📈 Elo Rating System

* Automatic Elo rating calculation
* Rating updates after completed games
* Persistent player ratings

### 🧠 Interactive Training

#### GM Trainer

Play through historic games from the perspective of famous grandmasters and learn from their decisions.

#### Board-Vision Flashcards

Practice visualizing chess positions from memory to improve board awareness and visualization skills.

### 🎨 Responsive UI/UX

* Modern dark-themed interface
* Chess.com/Lichess-inspired design
* Shared `base.html` layout
* Persistent navigation bar
* Responsive pages across the application
* Smooth and consistent styling

---

## 🛠️ Tech Stack

| Category                    | Technologies                |
| --------------------------- | --------------------------- |
| **Backend**                 | Python, Django              |
| **Real-Time Communication** | Django Channels, WebSockets |
| **ASGI Server**             | Daphne                      |
| **Channel Layer**           | Redis                       |
| **Chess Engine / Logic**    | Python-Chess                |
| **Database**                | SQLite                      |
| **Frontend**                | HTML5, CSS3, JavaScript     |
| **Communication**           | Vanilla WebSockets          |

---

## 📁 Project Structure

```text
ChessOP/
│
├── config/
│   ├── settings.py        # Django project settings
│   ├── asgi.py            # ASGI configuration
│   ├── urls.py            # Main URL configuration
│   └── wsgi.py            # WSGI configuration
│
├── core/
│   ├── static/            # CSS, JavaScript, images
│   │
│   ├── templates/core/
│   │   ├── base.html      # Global layout
│   │   ├── home.html      # Home page
│   │   ├── lobby.html     # Matchmaking lobby
│   │   ├── game.html      # Chess game interface
│   │   ├── login.html     # Login page
│   │   └── register.html  # Registration page
│   │
│   ├── consumers.py       # WebSocket consumers
│   ├── models.py          # Database models
│   ├── views.py           # HTTP request handlers
│   ├── routing.py         # WebSocket URL routing
│   └── utils.py           # Elo calculation & utilities
│
├── venv/                  # Python virtual environment
├── db.sqlite3             # SQLite development database
├── manage.py              # Django management utility
└── README.md              # Project documentation
```

---

# 🚀 Installation & Setup

Follow the steps below to run ChessLab locally.

## 1. Clone the Repository

```bash
git clone <YOUR_REPOSITORY_URL>
cd ChessOP
```

---

## 2. Create a Virtual Environment

```bash
python -m venv venv
```

### Windows

```powershell
venv\Scripts\activate
```

### macOS / Linux

```bash
source venv/bin/activate
```

---

## 3. Install Dependencies

Install the required Python packages:

```bash
pip install django channels daphne python-chess
```

> **Note:** If the project contains a `requirements.txt` file, it is recommended to install dependencies using:
>
> ```bash
> pip install -r requirements.txt
> ```

---

## 4. Apply Database Migrations

Create and apply the Django database migrations:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 5. Create a Superuser

To access the Django administration panel:

```bash
python manage.py createsuperuser
```

Follow the prompts to create your administrator account.

---

## 6. Start the Development Server

Since ChessLab uses **Django Channels** for real-time WebSocket communication, the project runs through an ASGI-compatible setup.

For development, you can start the server with:

```bash
python manage.py runserver
```

Alternatively, you can run the application using **Daphne**:

```bash
daphne config.asgi:application
```

---

## 7. Open the Application

Once the server is running, open:

```text
http://127.0.0.1:8000/
```

You should now be able to access the ChessLab web application.

---

# 🔄 How It Works

The application follows a real-time client-server architecture:

```text
                 ┌─────────────────────┐
                 │     Web Browser     │
                 │ HTML/CSS/JavaScript │
                 └──────────┬──────────┘
                            │
                     WebSocket / HTTP
                            │
                            ▼
                 ┌─────────────────────┐
                 │       Django        │
                 │   Views & Routing   │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │  Django Channels    │
                 │ WebSocket Consumers │
                 └──────────┬──────────┘
                            │
                       Channel Layer
                            │
                            ▼
                 ┌─────────────────────┐
                 │       Redis         │
                 │  Real-Time Backend  │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │     Chess Logic     │
                 │   Python-Chess      │
                 └──────────┬──────────┘
                            │
                            ▼
                 ┌─────────────────────┐
                 │      Database       │
                 │       SQLite        │
                 └─────────────────────┘
```

---

# 🎮 Core Application Flow

```text
User Registration / Login
          │
          ▼
      Home Page
          │
          ▼
    Matchmaking Lobby
          │
          ├───────────────┐
          │               │
       Create Game     Join Game
          │               │
          └───────┬───────┘
                  ▼
             Chess Game
                  │
          ┌───────┴────────┐
          │                │
       Moves            Live Chat
          │                │
          └───────┬────────┘
                  ▼
            Game Completion
                  │
                  ▼
             Elo Update
                  │
                  ▼
            Updated Profile
```

---

# 🧩 Main Components

| Component        | Responsibility                                                  |
| ---------------- | --------------------------------------------------------------- |
| `models.py`      | Defines users, games, profiles, and persistent application data |
| `views.py`       | Handles standard HTTP requests and page rendering               |
| `consumers.py`   | Handles WebSocket connections, moves, game state, and chat      |
| `routing.py`     | Maps WebSocket URLs to consumers                                |
| `utils.py`       | Contains Elo calculation and reusable helper functions          |
| `templates/`     | Contains the application's HTML pages                           |
| `static/`        | Contains CSS, JavaScript, and image assets                      |
| `config/asgi.py` | Configures the ASGI application and Channels                    |

---

# 🔌 Real-Time Communication

ChessLab uses **Django Channels + WebSockets** to provide real-time interaction.

When a player makes a move:

```text
Player A
   │
   │  WebSocket
   ▼
Django Channels
   │
   ├── Validate Move
   │
   ├── Update Game State
   │
   └── Broadcast Move
            │
            ▼
        Player B
```

This allows both players to see moves and other game events without refreshing the page.

---

# 📊 Elo Rating System

After a game finishes, ChessLab automatically updates the players' ratings based on the game result.

```text
Game Finished
      │
      ▼
Determine Result
      │
      ▼
Calculate Expected Scores
      │
      ▼
Calculate Elo Change
      │
      ▼
Update Player Ratings
```

---

# 🧠 Training Modes

### GM Trainer

Allows users to study historic chess games by following the moves played by grandmasters.

**Purpose:**

* Study opening decisions
* Understand strategic ideas
* Analyze tactical positions
* Learn from historical games

### Board-Vision Flashcards

Users are shown chess positions and challenged to reconstruct or visualize the board.

**Purpose:**

* Improve board visualization
* Develop calculation skills
* Strengthen piece-location memory
* Improve blindfold-chess abilities

---

# 🗄️ Database

ChessLab currently uses **SQLite** for development.

The database file is:

```text
db.sqlite3
```

For production deployment, the application can be configured to use a more scalable database such as PostgreSQL.

---

# 🔴 Redis

Redis is used as the **Channel Layer backend** for Django Channels.

It enables WebSocket consumers to communicate efficiently and supports real-time features such as:

* Multiplayer game synchronization
* Lobby updates
* Player join/leave events
* Live chat
* Room communication

---

# 🧪 Development

Useful Django commands:

```bash
# Run development server
python manage.py runserver

# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Open Django shell
python manage.py shell
```

---

# 🛡️ Production Considerations

Before deploying ChessLab to production, consider:

* Using **PostgreSQL** instead of SQLite
* Running Redis as a production service
* Configuring environment variables for secrets
* Setting `DEBUG=False`
* Configuring `ALLOWED_HOSTS`
* Using HTTPS/WSS
* Serving static files through a production-ready setup
* Running Daphne behind a reverse proxy such as Nginx
* Adding proper logging and monitoring

---

# 🚧 Future Improvements

Potential future enhancements include:

* [ ] Game clocks and time controls
* [ ] Spectator mode
* [ ] Game history and PGN export
* [ ] Chess engine analysis
* [ ] Leaderboards
* [ ] Friends and direct challenges
* [ ] Tournament system
* [ ] Player statistics
* [ ] PostgreSQL production support
* [ ] Docker deployment
* [ ] Mobile-responsive chessboard improvements

---