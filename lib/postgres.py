import psycopg2
from psycopg2 import sql
from psycopg2.extras import RealDictCursor
from SoccerAPI.lib.schema import Schema
from SoccerAPI.lib.env import Env

class PostgreSQL:
    def __init__(self, app):
        env = Env()
        self.connection_params = {
            "host": env.db_host,
            "port": env.db_port,
            "database": env.db_database,
            "user": env.db_user,
            "password": env.db_password
        }
        self.app = app
        self.schema = Schema()
        #Cache
        mapping_cache = {}
        tables = ["players", "teams", "leagues"]
        for table in tables:
            mapping = {}
            for team in self.get_all(table, dont_inflate=True):
                mapping[team["fapi_" + table[0:-1] + "_id"]] = team
            mapping_cache[table] = mapping
        self.cache = mapping_cache
        
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
                for key in record.keys():
                    res[key] = record[key]

        except Exception as e:
            print(f"Error: {e}")
        finally:
            # Close the connection
            connection.close()
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

    def search(self, table_name, query):
        schema = self.get_schema(table_name)

        #Check Cache
        if( len(query.keys()) == 1):
            key = list(query.keys())[0]
            if(key in ["fapi_team_id", "fapi_league_id", "fapi_player_id" ]):
                if str(query[key]) in self.cache[table_name].keys():
                    db_data = self.cache[table_name][str(query[key])]
                    return [ schema["class"](db_data, self)]

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