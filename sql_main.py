import psycopg2
from config import config


def create_tables():
  """ create 3 tables """
  commands = (
    """
    CREATE TABLE IF NOT EXISTS misc (
      misc_id SERIAL PRIMARY KEY,
      misc_metric VARCHAR(255) UNIQUE NOT NULL,
      misc_value FLOAT,
      unit VARCHAR(255) NOT NULL
    )
    """,

    """
    CREATE TABLE IF NOT EXISTS counter (
      counter_id SERIAL PRIMARY KEY,
      counter_metric VARCHAR(255) UNIQUE NOT NULL,
      counter_value FLOAT,
      unit VARCHAR(255) NOT NULL
    )
    """)
  conn = None
  try:
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()

    # execute create table commands
    for command in commands:
        cur.execute(command)
    # commit the changes
    conn.commit()
    cur.close()
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
  finally:
    if conn is not None:
      conn.close()



def insert_metric(table, metric, value, unit):
  if table == "misc":
    sql = """INSERT INTO misc(misc_metric, misc_value, unit)
            VALUES(%s, %s, %s) RETURNING misc_id;"""
  elif table == "counter":
    sql = """INSERT INTO counter(counter_metric, counter_value, unit)
            VALUES(%s, %s, %s) RETURNING counter_id;"""
  conn = None
  id = None

  try:
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    # execute the INSERT statement
    cur.execute(sql, (metric, value, unit,))
    id = cur.fetchone()[0]
    conn.commit()
    cur.close()
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
  finally:
    if conn is not None:
      conn.close()



def insert_metric_list(table, metric_list):
  if table == "misc":
    sql = """INSERT INTO misc(misc_metric, misc_value, unit)
            VALUES(%s, %s, %s);"""
  elif table == "counter":
    sql = """INSERT INTO counter(counter_metric, counter_value, unit)
            VALUES(%s, %s, %s);"""
  conn = None

  try:
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    # execute the INSERT statement
    cur.executemany(sql, metric_list)
    conn.commit()
    cur.close()
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
  finally:
    if conn is not None:
      conn.close()



def update_metric(table, metric, new_value):

  metric_ref = table + "_metric"
  value_ref = table + "_value"

  sql = f""" UPDATE {table}
              SET {value_ref} = %s
              WHERE {metric_ref} = %s"""
  conn = None

  try:
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    # execute the INSERT statement
    cur.execute(sql, (new_value, metric,))
    conn.commit()
    cur.close()
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
  finally:
    if conn is not None:
      conn.close()



def read_query(conn, query):
  cur = conn.cursor()
  result = None
  try:
    cur.execute(query)
    result = cur.fetchall()
    cur.close()
  except (Exception, psycopg2.DatabaseError) as err:
    print(f"Error: '{err}'")
  finally:
    if conn is not None:
      conn.close()

  return result



def get_all_metrics(table):

  id_ref = table + "_id"
  metric_ref = table + "_metric"
  value_ref = table + "_value"

  query = f"SELECT {id_ref}, {metric_ref}, {value_ref}, unit FROM {table} ORDER BY {id_ref}"

  params = config()
  conn = psycopg2.connect(**params)
  return read_query(conn, query)



def get_all_metric_names(table):
  query = f"SELECT {table}_metric FROM {table} ORDER BY {table}_id"
  params = config()
  conn = psycopg2.connect(**params)
  return read_query(conn, query)



def get_metric(table, metric):

  id_ref = table + "_id"
  metric_ref = table + "_metric"
  value_ref = table + "_value"

  query = f"""
    SELECT {id_ref}, {metric_ref}, {value_ref}, unit
    FROM {table}
    WHERE {metric_ref} = '{metric}';
    """
  
  params = config()
  conn = psycopg2.connect(**params)
  return read_query(conn, query)



def delete_metric(table, metric):
  
  conn = None
  rows_deleted = 0
  try:
    params = config()
    conn = psycopg2.connect(**params)
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {table} WHERE {table}_metric = %s", (metric,))
    rows_deleted = cur.rowcount
    conn.commit()
    cur.close()
  except (Exception, psycopg2.DatabaseError) as error:
    print(error)
  finally:
    if conn is not None:
      conn.close()

  return rows_deleted








# create_tables()

# insert_metric("misc", "SRAM", 10, "GB")
# insert_metric("counter", "RAM", 16, "GB")

# insert_metric_list("misc",[
#   ("alpha", 10, "MB",),
#   ("beta", 20, "MB",),
#   ("theta", 30, "MB",),
#   ("gamma", 40, "MB",),
# ])

# insert_metric_list("counter",[
#   ("alpha", 10, "MB",),
#   ("beta", 20, "MB",),
#   ("theta", 30, "MB",),
#   ("gamma", 40, "MB",),
# ])

# update_metric("misc", "alpha", 1000)

# res1 = get_all_metrics("misc")
# res2 = get_all_metrics("counter")
# print(res1)
# print(res2)

# deleted1 = delete_metric("misc", "gamma")
# print(deleted1)

# query1 = get_metric("misc", "alpha")
# print(query1)


