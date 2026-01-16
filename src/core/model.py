# Copyright (C) 2025 https://github.com/FranBarInstance/neutral-starter-py (See LICENCE)
"""
Base class for database operations with SQLAlchemy multi-engine support.

This module provides a Model class that handles SQL operations through JSON-defined
queries, with built-in error handling and transaction support, compatible with
SQLite, PostgreSQL, MySQL, and other SQLAlchemy-supported databases.
"""

import json
import random
import time
from typing import List, Tuple, Any, Union, Dict, Optional
from flask import current_app
from sqlalchemy import create_engine, text
from sqlalchemy.engine import CursorResult
from sqlalchemy.exc import SQLAlchemyError
from app.config import Config
# from constants import * # pylint: disable=wildcard-import,unused-wildcard-import


class Model:
    """Base class for handling database operations with SQLAlchemy.

    This class provides a foundation for executing SQL operations using JSON-defined queries,
    with built-in error handling, transaction support, and unique ID generation. All database
    operations are executed through the exec() method, which loads SQL queries from JSON files.

    Attributes:
        engine: SQLAlchemy engine instance
        last_error: Detailed technical error message for debugging
        user_error: User-friendly error message
        has_error: Flag indicating if there's an error
        error_code: Error code for error identification
    """
    DEFAULT_TYPE = '@portable'

    def __init__(self, db_url: str, db_type: str):
        """Initialize a new Model instance with database connection.

        Args:
            database_url: SQLAlchemy connection URL (default: from DATABASE constant)
                         Examples:
                         - SQLite: sqlite:///safe.db
                         - PostgreSQL: postgresql://user:password@localhost/dbname
                         - MySQL: mysql://user:password@localhost/dbname
        """
        try:
            self.db_type = db_type
            self.engine = create_engine(db_url)
            self.last_error = None          # Detailed technical error (for logs/debug)
            self.user_error = None          # Safe message to show to user
            self.has_error = False          # Flag to indicate if there's an error
            self.error_code = None          # Error code for identification
        except SQLAlchemyError as e:
            raise RuntimeError("Failed to initialize database engine") from e

    def create_uid(self, target: str, attempts: int = 10) -> Optional[int]:
        """Create a unique identifier that's guaranteed to be unique across all database tables.

        Args:
            target: The target table or entity type for which the UID is being created
            attempts: Maximum number of attempts to generate a unique ID (default: 10)

        Returns:
            int: A unique identifier between UUID_MIN and UUID_MAX that's guaranteed to be
                unique across all database tables, or None if failed
        """
        for _ in range(attempts):
            uid = random.randint(Config.UUID_MIN, Config.UUID_MAX)
            created = int(time.time())
            params = {
                "uid": uid,
                "target": target,
                "created": created
            }
            result = self.exec("app", "uid-create", params)
            if result and isinstance(result, dict) and result.get('success'):
                return uid
        return None


    def get_last_error(self) -> dict:
        """Get the last model error."""
        error_msg = self.user_error or 'Failed.'
        if current_app.debug:
            error_msg = self.last_error or 'Failed.'
        return {
            'success': False,
            'error': self.error_code or 'FAILED',
            'message': error_msg
        }

    def clear_error(self) -> None:
        """Reset all error-related attributes to their default state."""
        self.last_error = None
        self.user_error = None
        self.has_error = False
        self.error_code = None

    def _set_error(
        self,
        technical_msg: str,
        user_msg: str,
        error_code: str = None
    ) -> None:
        """Set error information with technical and user-friendly messages.

        Args:
            technical_msg: Detailed error message for debugging purposes
            user_msg: User-friendly error message that can be safely displayed
            error_code: Optional error code for error identification
        """
        self.has_error = True
        self.last_error = technical_msg
        self.user_error = user_msg
        self.error_code = error_code

    def exec(
        self,
        name: str,
        key: str,
        data: Union[Tuple, List[Tuple]] = None
    ) -> Union[
        List[Tuple[Any, ...]],  # SELECT
        Dict[str, Any],         # writing operations
        List[Dict[str, Any]],   # multiple transactions
        None                    # in case of error
    ]:
        """Execute SQL queries from JSON file, handling both single statements and transactions.

        Args:
            name: Name of the JSON file containing the queries
            key: Key of the specific query to execute
            data: Parameters for single query or list of parameters for transaction

        Returns:
            For SELECT: Query results as list of tuples
            For single INSERT/UPDATE/DELETE: Dictionary with operation details
            For transactions: List of operation results
            For other statements: True if successful
            None: if there was an error (check self.has_error and self.user_error)
        """
        self.clear_error()

        file_path = f"{Config.MODEL_DIR}/{name}.json"
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = json.load(file)
        except (FileNotFoundError, PermissionError) as e:
            self._set_error(
                f"File access error for {file_path}: {str(e)}",
                "System configuration error. Please contact administrator.",
                "FILE_ACCESS_ERROR"
            )
            return None
        except json.JSONDecodeError as e:
            self._set_error(
                f"Invalid JSON in {file_path}: {str(e)}",
                "System configuration error. Please contact administrator.",
                "CONFIG_ERROR"
            )
            return None

        db_type = f"@{self.db_type}"
        sql_content = content.get(key, {}).get(db_type, content.get(key, {}).get(self.DEFAULT_TYPE, ""))
        if isinstance(sql_content, str) and sql_content.startswith('@'):
            sql_content = content.get(key, {}).get(sql_content, "")

        # Check if the key exists in the JSON content
        if not sql_content:
            self._set_error(
                f"Key '{key}' not found in {file_path}",
                "Operation not available. Please contact administrator.",
                "OPERATION_NOT_FOUND"
            )
            return None

        # Case 1: Simple statement (string)
        if isinstance(sql_content, str):
            return self._execute_single(sql_content, data)

        # Case 2: Transaction (list of statements)
        elif isinstance(sql_content, list):
            return self._execute_transaction(sql_content, data)

        else:
            self._set_error(
                f"Invalid SQL content type for key '{key}'",
                "Configuration error. Please contact administrator.",
                "INVALID_CONFIG"
            )
            return None

    def _execute_single(
        self,
        sql: str,
        params: Tuple = None
    ) -> Union[Dict[str, Any], None]:
        """Execute a single SQL statement and return its result.

        Args:
            sql: SQL statement to execute
            params: Optional tuple of parameters for the SQL statement

        Returns:
            Dictionary containing operation results or None if error
        """
        try:
            with self.engine.begin() as conn:
                stmt = text(sql)
                result: CursorResult = conn.execute(stmt, params or {})

                operation = self._get_operation_type(sql)
                if operation == "SELECT":
                    rows = result.fetchall()
                    return {
                        'success': True,
                        'operation': operation,
                        'columns': result.keys(),
                        'rows': rows,
                        'rowcount': len(rows)
                    }
                elif operation:
                    return {
                        'success': result.rowcount > 0,
                        'rowcount': result.rowcount,
                        'operation': operation,
                        'lastrowid': result.lastrowid if operation == "INSERT" else None
                    }
                else:
                    return {'success': True, 'operation': 'OTHER'}

        except SQLAlchemyError as e:
            self._set_error(
                f"SQL error: {str(e)}",
                "Database operation error.",
                "DATABASE_ERROR"
            )
            return None
        except (TypeError, ValueError) as e:
            self._set_error(
                f"Parameter error: {str(e)}",
                "Invalid data. Please check the information entered.",
                "INVALID_DATA"
            )
            return None

    def _execute_transaction(
        self,
        statements: List[str],
        params_list: List[Tuple] = None
    ) -> Union[List[Dict[str, Any]], None]:
        """Execute multiple SQL statements as a single transaction.

        Args:
            statements: List of SQL statements to execute
            params_list: Optional list of parameter tuples for each statement

        Returns:
            List of dictionaries containing results for each statement or None if error
        """
        try:
            if params_list and len(params_list) != len(statements):
                self._set_error(
                    "Number of parameters doesn't match number of statements",
                    "Error in transaction data.",
                    "TRANSACTION_PARAM_ERROR"
                )
                return None

            params_list = params_list or [{}] * len(statements)
            results = []

            with self.engine.begin() as conn:
                for i, (sql, params) in enumerate(zip(statements, params_list)):
                    stmt = text(sql)
                    result: CursorResult = conn.execute(stmt, params)

                    operation = self._get_operation_type(sql)
                    if operation == "SELECT":
                        rows = result.fetchall()
                        results.append({
                            'success': True,
                            'operation': operation,
                            'statement_index': i,
                            'columns': result.keys(),
                            'rows': rows,
                            'rowcount': len(rows)
                        })
                    elif operation:
                        res = {
                            'success': result.rowcount > 0,
                            'rowcount': result.rowcount,
                            'operation': operation,
                            'statement_index': i
                        }
                        if operation == "INSERT":
                            res['lastrowid'] = result.lastrowid
                        results.append(res)
                    else:
                        results.append({
                            'success': True,
                            'operation': 'OTHER',
                            'statement_index': i
                        })

            return results

        except SQLAlchemyError as e:
            self._set_error(
                f"Transaction failed: {str(e)}",
                "Transaction error. Changes were not saved.",
                "TRANSACTION_ERROR"
            )
            return None
        except (TypeError, ValueError) as e:
            self._set_error(
                f"Transaction parameter error: {str(e)}",
                "Invalid data in transaction.",
                "TRANSACTION_DATA_ERROR"
            )
            return None

    def _get_operation_type(self, sql: str) -> Optional[str]:
        """Determine the type of SQL operation from a SQL statement.

        Args:
            sql: SQL statement to analyze

        Returns:
            The type of operation ('SELECT', 'INSERT', 'UPDATE', 'DELETE') or None
        """
        sql_upper = sql.strip().upper()
        if sql_upper.startswith("INSERT"):
            return "INSERT"
        elif sql_upper.startswith("UPDATE"):
            return "UPDATE"
        elif sql_upper.startswith("DELETE"):
            return "DELETE"
        elif sql_upper.startswith("SELECT"):
            return "SELECT"
        return None
