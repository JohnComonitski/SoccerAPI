import requests
import json
import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from .schema import Schema
import zlib
import base64
from typing import Any


class PostgreSQL:
    r"""The main database object.

    :ivar app: app data configuration. This value is usually passed from the
      main ``SoccerAPI`` object.
    :vartype app: dict
    :ivar schema: a class containing data in the form of dictionaries
    :ivar has_connection: tells if database connection is possible. If one
      or more of the connection parameters are missing this value is set to
      ``0``, otherwise it is set to ``1``.
    :vartype has_connection: int
    :ivar connection_params: PostgreSQL connection settings.
    :ivar cache: cache data.
    """
    def __init__(self, app: dict):
        r"""Create a new instance.

        :param app: see previous description.
        :type app: dict
        """
        self.app = app
        config = app["config"]
        self.schema = Schema()

        self.has_connection = 1
        connection_keys = [ "db_host", "db_port", "db_database", "db_user", "db_password" ]
        for key in connection_keys:
            if key not in config:
                self.has_connection = 0

        if(self.has_connection):
            self.connection_params = {
                "host": config["db_host"],
                "port": config["db_port"],
                "database": config["db_database"],
                "user": config["db_user"],
                "password": config["db_password"]
            }

        #Cache
        self.cache = self.build_cache()

    def build_cache(self):
        data = self.get_cache_data()
        cache = {
            "players" : { "understat_id" : {}, "fbref_id" : {}, "tm_id" : {}, "fapi_id" : {}, "player_id" : {} },
            "teams" : { "understat_id" : {}, "fbref_id" : {}, "tm_id" : {}, "fapi_id" : {}, "team_id" : {} },
            "leagues" : { "understat_id" : {}, "fbref_id" : {}, "tm_id" : {}, "fapi_id" : {}, "league_id" : {} }
        }
        for table in data:
            singular = table[0:-1]
            table_data = data[table]
            for record in table_data:
                row = {}
                for key in record.keys():
                    row[key] = record[key]
                    
                for key in record.keys():
                    if key == "fbref_" + singular + "_id":
                        cache[table]["fbref_" + singular + "_id"][str(row[key])] = row
                    elif key == "tm_" + singular + "_id":
                        cache[table]["tm_" + singular + "_id"][str(row[key])] = row
                    elif key == "fapi_" + singular + "_id":
                        cache[table]["fapi_" + singular + "_id"][str(row[key])] = row
                    elif key == singular + "_id":
                        cache[table][singular + "_id"][str(row[key])] = row
                    if key == "understat_" + singular + "_id":
                        cache[table]["understat_" + singular + "_id"][str(row[key])] = row
        return cache
        
    def get_cache_data(self):
        endpoint = "https://3juig81jql.execute-api.us-west-2.amazonaws.com/v1/soccerapi"
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0'}
        res = requests.get(endpoint, headers=headers)
        decompressed = zlib.decompress(base64.b64decode(res.text)).decode('utf-8')
        return json.loads(decompressed)

    def build_schema(self):
        for k,table_info in vars(self.schema).items():
            if(table_info):
                table_name = table_info["name"]
                primary_key = table_info["primary_key"]
                columns = table_info["columns"]

                sql_query = f"CREATE TABLE IF NOT EXISTS {table_name} ( "

                for column in columns:
                    column_name = column["sql"]
                    data_type = column["type"]
                    is_primary_key = "PRIMARY KEY" if column_name == primary_key and column["primary_key"] else ""
                    if(column.get("increment") and column_name == primary_key):
                        auto_increment = "SERIAL"
                        data_type = ""
                    else:
                        auto_increment = ""

                    sql_query += f"    {column_name} {data_type} {auto_increment} {is_primary_key},"

                # Remove the trailing comma and newline for the last column
                sql_query = sql_query.rstrip(",")

                # Add the closing parenthesis
                sql_query += ");"
                self.raw_query(sql_query)

    def get_schema(self, table):
        return self.schema.get_schema(table)

    def create_connection(self):
        return psycopg2.connect(**self.connection_params)

    def create(self, table_name, data):
        if not self.has_connection:
            print("Error: No database connection")
            return

        if not data or not isinstance(data, list) or not data[0]:
            print("Error: Data list is empty or does not contain dictionaries.")
            return

        connection = self.create_connection()

        try:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                columns = data[0].keys()
                values = [tuple(d[column] for column in columns) for d in data]

                # Generate the SQL query
                insert_query = sql.SQL("INSERT INTO {} ({}) VALUES {}").format(
                    sql.Identifier(table_name),
                    sql.SQL(', ').join(map(sql.Identifier, columns)),
                    sql.SQL(', ').join(sql.SQL("(" + ",".join(["%s"] * len(columns)) + ")") for _ in range(len(data)))
                )

                # Execute the query
                values_to_insert = []
                for tuple_values in values:
                    for tuple_value in tuple_values:
                        values_to_insert.append(tuple_value)
                
                cursor.execute(insert_query, values_to_insert)

            # Commit the changes
            connection.commit()

        except Exception as e:
            print(f"Error: {e}")
            connection.rollback()
        finally:
            # Close the connection
            connection.close()

    def get_all(self, table_name, dont_inflate=None):
        schema = self.get_schema(table_name)

        if not self.has_connection:
            print("Error: No database connection")
            return

        connection = self.create_connection()
        res = []

        try:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Generate the SQL query
                query = sql.SQL("SELECT * FROM {}").format(
                    sql.Identifier(table_name),
                )
                cursor.execute(query)

                for record in cursor:
                    row = {}
                    for key in record.keys():
                        row[key] = record[key]
                    if(dont_inflate):
                        res.append(row)
                    else:
                        res.append(schema["class"](row, self))

        except Exception as e:
            print(f"Error: {e}")
        finally:
            # Close the connection
            connection.close()
            return res

    def get(self, table_name, primary_key):
        schema = self.get_schema(table_name)

        if str(primary_key) in self.cache[table_name][schema["primary_key"]]:
            data = self.cache[table_name][schema["primary_key"]][str(primary_key)]
            return schema["class"](data, self)

        if not self.has_connection:
            print("Error: No database connection")
            return

        connection = self.create_connection()
        res = {}

        try:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Generate the SQL query
                query = sql.SQL("SELECT * FROM {} WHERE {} = {}").format(
                    sql.Identifier(table_name),
                    sql.SQL(schema["primary_key"]),
                    sql.SQL(str(primary_key))
                )
                cursor.execute(query)

                record = cursor.fetchone()
                if(record):
                    for key in record.keys():
                        res[key] = record[key]
        except Exception as e:
            print(f"Error: {e}")
        finally:
            # Close the connection
            connection.close()
            if schema["primary_key"] not in res:
                return None
            return schema["class"](res, self)
        
    def build_query(self, query, use_or):
        query_params = []
        for key in query.keys():
            if(key == "not"):
                query_params.append("( NOT " + self.build_query(query[key], 0) + " )")
            elif(key == "or"):
                query_params.append(self.build_query(query[key], 1))
            elif(key == "and"):
                query_params.append(self.build_query(query[key], 0))
            else:
                if(str(query[key]) == "null"):
                    query_params.append(" ( " + str(key) + " IS NULL ) ")
                elif(isinstance(query[key], list)):
                    tmp = []
                    for item in query[key]:
                        tmp.append(self.build_query({ key : item }, 0))
                    query_params.append(" ( " + " OR ".join(tmp)+ " ) ")
                else:
                    query_params.append(str(key) + " = '" + str(query[key]) + "'")

        if(use_or):
            return " ( " + " OR ".join(query_params) + " ) "
        else:
            return " ( " + " AND ".join(query_params) + " ) "

    def search(self, table_name: str, query: dict) -> list[Any]:
        r"""Find and return objects.

        :param table_name: database table to search on. possible values are
                           ``players``, ``teams`` or ``leagues``.
        :param query: key-value pair for the ID type to be searched.

          Examples:

          >>> api.db.search(table_name=players, {'player_id': '12345'})
          >>> api.db.search(table_name=players, {'fapi_id': '12345'})
          >>> api.db.search(table_name=players, {'tm_id': '12345'})
          >>> api.db.search(table_name=players, {'fbref_id' : '12345'})

        :type table_name: str
        :type query: dict[str]
        :returns: a list of objects that the search yields.
        :rtype: list[Any]
        """
        schema = self.get_schema(table_name)
        #Check Cache 
        if( len(query.keys()) == 1 ):
            key = list(query.keys())[0]
            if( "_id" in key ):
                if str(query[key]) in self.cache[table_name][key]:
                    data = self.cache[table_name][key][str(query[key])]
                    return [ schema["class"](data, self) ]

        if not self.has_connection:
            print("Error: No database connection")
            return

        #Cache Fail Make Search
        connection = self.create_connection()

        res = []
        try:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                query_params = self.build_query(query, 0)
                # Generate the SQL query
                update_query = sql.SQL("SELECT * FROM {} WHERE {}").format(
                    sql.Identifier(table_name),
                    sql.SQL(query_params),
                )
                cursor.execute(update_query)

                for record in cursor:
                    row = {}
                    for key in record.keys():
                        row[key] = record[key]
                    if("class" in schema):
                        res.append(schema["class"](row, self))
                    else:
                        res.append(row)
        except Exception as e:
            print(f"Error: {e}")

        finally:
            # Close the connection
            connection.close()
            return res

    def update(self, table_name, primary_key, data):
        if not self.has_connection:
            print("Error: No database connection")
            return

        connection = self.create_connection()
        try:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Prep Updates
                updates = []
                for key in data.keys():
                    updates.append(key + " = '" + str(data[key]) + "'")
                
                schema = self.get_schema(table_name)

                updates_sql = (', ').join(updates)

                # Generate the SQL query
                update_query = sql.SQL("UPDATE {} SET {} WHERE {} = '{}'").format(
                    sql.Identifier(table_name),
                    sql.SQL(updates_sql),
                    sql.SQL(schema["primary_key"]),
                    sql.SQL(primary_key)
                )
                cursor.execute(update_query)

        except Exception as e:
            print(f"Error: {e}")

        finally:
            connection.commit()
            # Close the connection
            connection.close()

    def delete(self, table_name, primary_key):
        if not self.has_connection:
            print("Error: No database connection")
            return

        schema = self.get_schema(table_name)
        connection = self.create_connection()
        try:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Generate the SQL query
                update_query = sql.SQL("DELETE FROM {} WHERE {} = '{}'").format(
                    sql.Identifier(table_name),
                    sql.SQL(schema["primary_key"]),
                    sql.SQL(primary_key)
                )
                cursor.execute(update_query)
                connection.commit()

        except Exception as e:
            print(f"Error: {e}")

        finally:
            # Close the connection
            connection.close()

    def raw_query(self, query):
        if not self.has_connection:
            print("Error: No database connection")
            return

        connection = self.create_connection()
        res = []

        try:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                # Generate the SQL query
                raw_query = sql.SQL(query).format()
                cursor.execute(raw_query)
                connection.commit()

                for record in cursor:
                    row = {}
                    for key in record.keys():
                        row[key] = record[key]
                    res.append(row)

        except Exception as e:
            pass
        finally:
            # Close the connection
            connection.close()
            return res
