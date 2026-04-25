## Copyright (c) 2025 Cloudera, Inc. All Rights Reserved.
##
## This file is licensed under the Apache License Version 2.0 (the "License").
## You may not use this file except in compliance with the License.
## You may obtain a copy of the License at http:##www.apache.org/licenses/LICENSE-2.0.
##
## This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS
## OF ANY KIND, either express or implied. Refer to the License for the specific
## permissions and limitations governing your use of the file.

import json
import os
from impala.dbapi import connect


# Helper to get Impala connection details from env vars
def get_db_connection():
    host = os.getenv("IMPALA_HOST", "coordinator-default-impala.example.com")
    port = int(os.getenv("IMPALA_PORT", "443"))
    user = os.getenv("IMPALA_USER", "username")
    password = os.getenv("IMPALA_PASSWORD", "password")
    database = os.getenv("IMPALA_DATABASE", "default")
    auth_mechanism = os.getenv("IMPALA_AUTH_MECHANISM", "LDAP")
    use_http_transport = os.getenv("IMPALA_USE_HTTP_TRANSPORT", "true")
    http_path = os.getenv("IMPALA_HTTP_PATH", "cliservice")
    use_ssl = os.getenv("IMPALA_USE_SSL", "true")

    return connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        auth_mechanism=auth_mechanism,
        use_http_transport=use_http_transport,
        http_path=http_path,
        use_ssl=use_ssl,
    )


def execute_query(query: str) -> str:
    conn = None

    # Implement rudimentary SQL injection prevention
    # In this case, we only allow read-only queries
    # This is a very basic check and should be improved for production use
    readonly_prefixes = ["select", "show", "describe", "with"]

    if not query.strip().lower().split()[0] in readonly_prefixes:
        return "Only read-only queries are allowed."

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(query)
        if cur.description:
            rows = cur.fetchall()
            result = json.dumps(rows, default=str)
        else:
            conn.commit()
            result = "Query executed successfully."
        cur.close()
        return result
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        if conn:
            conn.close()


def get_schema() -> str:
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SHOW TABLES")
        tables = cur.fetchall()
        schema = [table[0] for table in tables]
        return json.dumps(schema)
    except Exception as e:
        return f"Error: {str(e)}"
    finally:
        if conn:
            conn.close()
