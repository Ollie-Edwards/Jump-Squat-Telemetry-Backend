import sqlite3
from contextlib import contextmanager
import pickle

class DatabaseController():
    def __init__(self):
        self.name = "jumpData.db"
        self.createTables()

    @contextmanager
    def get_conn(self):
        conn = sqlite3.connect(self.name)
        try:
            yield conn
        finally:
            conn.close()

    def createTables(self):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS jumps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    atleteId INTEGER NOT NULL,
                    timestamp DATETIME NOT NULL DEFAULT (datetime('now', 'localtime')),
                    name TEXT NOT NULL,
                    dataframe BLOB NOT NULL,
                    duration REAL,
                        
                    takeoff_velocity REAL,
                    jump_height REAL,
                    flight_time_suvat REAL,
                    flight_time_measured REAL,
                    peak_net_accel REAL,
                    avg_net_accel REAL,
                    time_to_peak_force REAL,
                    peak_grf REAL,
                    avg_grf REAL,
                    impulse REAL,
                    avg_power REAL,
                    peak_power REAL,
                    peak_rfd REAL
                )
            """)
            conn.commit()
        
    def saveJumpData(self, athleteId: int, name: str, df, duration: float):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO jumps (
                    atleteId,
                    name,
                    dataframe,
                    duration
                )
                    VALUES (?, ?, ?, ?)
                """, (
                    athleteId,
                    name,
                    pickle.dumps(df),
                    duration
                )
            )
            conn.commit()

    def getDataframe(self, id):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT dataframe FROM jumps WHERE id = ?", (id,))
            stored_pickle = cursor.fetchone()[0]

            df = pickle.loads(stored_pickle)
            return df
