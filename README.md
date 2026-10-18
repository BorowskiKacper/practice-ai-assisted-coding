# Arena Player

Arena Player is a deliberately imperfect multi-tenant game platform for AI-assisted coding interview practice. Companies create game modes, register players, queue them, create matches, and publish rankings.

Start with [the problem statement](docs/problem-statement.md), [background](docs/background.md), and the four tickets in `docs/tickets/`.

Run with the local MongoDB (`27017`) and Redis (`6379`) containers:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Open `http://localhost:8000/docs` for the API.
