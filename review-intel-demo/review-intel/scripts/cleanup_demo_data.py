
import sqlite3
from pathlib import Path

DB_PATH = Path("instance/app.db")
BACKUP_PATH = Path("instance/app_backup_before_cleanup.db")

if not DB_PATH.exists():
    raise FileNotFoundError(f"Database not found: {DB_PATH}")

if not BACKUP_PATH.exists():
    raise FileNotFoundError("Backup not found. Cleanup cancelled.")

con = sqlite3.connect(DB_PATH)

try:
    con.execute("PRAGMA foreign_keys = ON")

    # Confirm that every existing review belongs to the old demo set.
    total = con.execute(
        "SELECT COUNT(*) FROM reviews"
    ).fetchone()[0]

    demo = con.execute(
        "SELECT COUNT(*) FROM reviews WHERE external_id LIKE 'D%'"
    ).fetchone()[0]

    other = con.execute(
        "SELECT COUNT(*) FROM reviews WHERE external_id NOT LIKE 'D%'"
    ).fetchone()[0]

    users = con.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0]

    print("Reviews:", total)
    print("D-prefixed reviews:", demo)
    print("Other reviews:", other)
    print("Users to preserve:", users)

    if total != 500 or demo != 500 or other != 0:
        raise RuntimeError(
            "Unexpected review counts. Cleanup cancelled."
        )

    confirm = input(
        "Type DELETE OLD DEMO DATA to continue: "
    )

    if confirm != "DELETE OLD DEMO DATA":
        print("Cancelled. No records deleted.")
        raise SystemExit(0)

    con.execute("BEGIN")

    # Remove child records before their parent reviews.
    con.execute("""
        DELETE FROM review_analysis
        WHERE review_id IN (
            SELECT review_id
            FROM reviews
            WHERE external_id LIKE 'D%'
        )
    """)

    con.execute("""
        DELETE FROM reviews
        WHERE external_id LIKE 'D%'
    """)

    # These catalog tables contain only the old demo catalog.
    con.execute("DELETE FROM products")
    con.execute("DELETE FROM brands")
    con.execute("DELETE FROM categories")

    con.commit()

    print("Cleanup completed.")
    print("Remaining reviews:", con.execute(
        "SELECT COUNT(*) FROM reviews"
    ).fetchone()[0])
    print("Remaining users:", con.execute(
        "SELECT COUNT(*) FROM users"
    ).fetchone()[0])

except BaseException:
    con.rollback()
    raise
finally:
    con.close()
