import mysql.connector
from mysql.connector import Error
import hashlib


def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            database="space_invaders_db",
            user="root",
            password=""
        )
    except Error as e:
        print("Database error:", e)
        return None


def hash_password(password):
    return hashlib.sha256(
        password.encode()
    ).hexdigest()


def register_player(username, password):
    conn = get_db_connection()

    if not conn:
        return None

    cursor = None

    try:
        cursor = conn.cursor(buffered=True)

        cursor.execute(
            """
            INSERT INTO players
            (username, password_hash)
            VALUES (%s, %s)
            """,
            (
                username.strip(),
                hash_password(password)
            )
        )

        conn.commit()

        return cursor.lastrowid

    except Error as e:
        print("Register error:", e)
        return None

    finally:
        if cursor:
            cursor.close()

        conn.close()


def login_player(username, password):
    conn = get_db_connection()

    if not conn:
        return None

    cursor = None

    try:
        cursor = conn.cursor(
            dictionary=True,
            buffered=True
        )

        cursor.execute(
            """
            SELECT
                player_id,
                username,
                password_hash
            FROM players
            WHERE username=%s
            """,
            (username.strip(),)
        )

        player = cursor.fetchone()

        if player:
            if player["password_hash"] == hash_password(password):

                return {
                    "player_id": player["player_id"],
                    "username": player["username"]
                }

        return None

    except Error as e:
        print("Login error:", e)
        return None

    finally:
        if cursor:
            cursor.close()

        conn.close()


def save_score(player_id, score, level=1):
    conn = get_db_connection()

    if not conn:
        return False

    cursor = None

    try:
        cursor = conn.cursor(buffered=True)

        level = max(
            1,
            min(99, int(level))
        )

        score = max(
            0,
            int(score)
        )

        cursor.execute(
            """
            INSERT INTO scores
            (
                player_id,
                score,
                level
            )
            VALUES
            (
                %s,
                %s,
                %s
            )
            """,
            (
                player_id,
                score,
                level
            )
        )

        conn.commit()

        print(
            f"Score saved: {score} | Level saved: {level}"
        )

        return True

    except Error as e:
        print("Score error:", e)
        return False

    finally:
        if cursor:
            cursor.close()

        conn.close()


def get_highest_score(player_id):
    conn = get_db_connection()

    if not conn:
        return 0

    cursor = None

    try:
        cursor = conn.cursor(buffered=True)

        cursor.execute(
            """
            SELECT
                COALESCE(MAX(score), 0)
            FROM scores
            WHERE player_id=%s
            """,
            (player_id,)
        )

        result = cursor.fetchone()

        return result[0] if result else 0

    except Error as e:
        print("Highest score error:", e)
        return 0

    finally:
        if cursor:
            cursor.close()

        conn.close()


def load_leaderboard():
    conn = get_db_connection()

    if not conn:
        return []

    cursor = None

    try:
        cursor = conn.cursor(
            dictionary=True,
            buffered=True
        )

        cursor.execute(
            """
            SELECT
                players.player_id,
                players.username,
                scores.score,
                scores.level
            FROM scores
            INNER JOIN players
                ON scores.player_id = players.player_id
            INNER JOIN
            (
                SELECT
                    player_id,
                    MAX(score) AS highest_score
                FROM scores
                GROUP BY player_id
            ) highest
                ON scores.player_id = highest.player_id
                AND scores.score = highest.highest_score
            ORDER BY
                scores.score DESC
            LIMIT 10
            """
        )

        return cursor.fetchall()

    except Error as e:
        print("Leaderboard error:", e)
        return []

    finally:
        if cursor:
            cursor.close()

        conn.close()


def update_player_profile(player_id, username):
    conn = get_db_connection()

    if not conn:
        return False

    cursor = None

    try:
        cursor = conn.cursor(buffered=True)

        cursor.execute(
            """
            UPDATE players
            SET username=%s
            WHERE player_id=%s
            """,
            (
                username.strip(),
                player_id
            )
        )

        conn.commit()

        return cursor.rowcount > 0

    except Error as e:
        print("Update error:", e)
        return False

    finally:
        if cursor:
            cursor.close()

        conn.close()


def delete_player(player_id):
    conn = get_db_connection()

    if not conn:
        return False

    cursor = None

    try:
        cursor = conn.cursor(buffered=True)

        cursor.execute(
            """
            DELETE FROM players
            WHERE player_id=%s
            """,
            (player_id,)
        )

        conn.commit()

        return cursor.rowcount > 0

    except Error as e:
        print("Delete error:", e)
        return False

    finally:
        if cursor:
            cursor.close()

        conn.close()


if __name__ == "__main__":
    conn = get_db_connection()

    if conn and conn.is_connected():
        print(
            "Successfully connected to "
            "space_invaders_db via XAMPP!"
        )

        conn.close()