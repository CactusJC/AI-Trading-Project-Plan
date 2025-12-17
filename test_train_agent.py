import os
import sqlite3
import tempfile

from train_agent import verify_training_data


def _make_db(rows):
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    conn = sqlite3.connect(path)
    conn.execute("CREATE TABLE data (value INTEGER)")
    if rows:
        conn.executemany("INSERT INTO data(value) VALUES (?)", [(i,) for i in range(rows)])
    conn.commit()
    conn.close()
    return path


def test_verify_training_data_true_when_enough_rows():
    db_path = _make_db(rows=5)
    try:
        assert verify_training_data(db_path, table_name='data', min_rows=3)
    finally:
        os.remove(db_path)


def test_verify_training_data_false_when_not_enough():
    db_path = _make_db(rows=1)
    try:
        assert not verify_training_data(db_path, table_name='data', min_rows=3)
    finally:
        os.remove(db_path)
