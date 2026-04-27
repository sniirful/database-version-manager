import sys
from dataclasses import dataclass, field
from typing import List, Optional
import mysql.connector


@dataclass
class _Transaction:
    host: str
    port: int
    user: str
    password: str
    target_version: int
    _conn: Optional[object] = field(default=None, init=False)
    _cursor: Optional[object] = field(default=None, init=False)
    _statements: List[tuple] = field(default_factory=list, init=False)

    def _ensure_connection(self):
        if self._conn is not None:
            return

        # Connect without selecting a default database, since callers may run
        # CREATE DATABASE and USE statements first.
        self._conn = mysql.connector.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            autocommit=False,
        )
        self._cursor = self._conn.cursor()

    def run_sql(self, sql: str, params: Optional[tuple] = None):
        if not isinstance(sql, str) or not sql.strip():
            return

        self._statements.append((sql, params or ()))

    def execute_select(self, sql: str, params: Optional[tuple] = None):
        if not isinstance(sql, str) or not sql.strip():
            return None

        self._ensure_connection()
        self._cursor.execute(sql, params or ())
        return self._cursor.fetchall()

    def commit(self):
        self._ensure_connection()
        try:
            database_version = None
            try:
                row = self.execute_select("SELECT version FROM version_manager.version")
                database_version = row[0][0] if row is not None and len(row) > 0 and len(row[0]) > 0 else None
                if database_version is not None and self.target_version <= database_version:
                    return
            except Exception:
                # In case the database doesn't exist yet, ignore errors. It will be created below.
                pass

            for statement, params in self._statements:
                self._cursor.execute(statement, params)

            self._cursor.execute("CREATE DATABASE IF NOT EXISTS version_manager")
            self._cursor.execute("USE version_manager")
            self._cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS version
                (
                    version INT NOT NULL PRIMARY KEY
                )
                """
            )

            if database_version is None:
                self._cursor.execute("INSERT INTO version (version) VALUES (%s)", (self.target_version,))
            else:
                self._cursor.execute("UPDATE version SET version = %s", (self.target_version,))

            self._conn.commit()
        except Exception:
            try:
                if self._conn is not None:
                    self._conn.rollback()
            finally:
                raise
        finally:
            try:
                if self._cursor is not None:
                    self._cursor.close()
            finally:
                if self._conn is not None:
                    self._conn.close()


def get_database_transaction(version: int):
    # Expected CLI invocation style: `python3 v1.py host port username password`
    # The same function is imported by both prepare.py and v1.py; we fetch
    # credentials from sys.argv as specified by the requirements.
    if len(sys.argv) < 5:
        raise RuntimeError(
            "Expected arguments: host port username password (invocation: `python3 <script>.py host port user password`)"
        )

    host = sys.argv[1]
    try:
        port = int(sys.argv[2])
    except Exception as e:
        raise RuntimeError("Port must be an integer") from e
    user = sys.argv[3]
    password = sys.argv[4]

    return _Transaction(host=host, port=port, user=user, password=password, target_version=version)
