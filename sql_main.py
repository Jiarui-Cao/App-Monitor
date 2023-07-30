import psycopg2
from config import config
import time


class database:
  def __init__(self, params):
    self.params = params
    self.conn = psycopg2.connect(**params)
    self.cur = self.conn.cursor()
  


  def establish_connection(self):
    self.conn = psycopg2.connect(**self.params)
    self.cur = self.conn.cursor()



  def create_tables(self):
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
      """,
      """
      CREATE TABLE IF NOT EXISTS time_series (
        ts_id SERIAL PRIMARY KEY,
        ts_time INT,
        ts_metric VARCHAR(255) NOT NULL,
        ts_value FLOAT,
        unit VARCHAR(255) NOT NULL
      )
      """
      )
    if self.conn is None:
      self.establish_connection()
    try:
      # execute create table commands
      for command in commands:
          self.cur.execute(command)
      # commit the changes
      self.conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
      print(error)



  def insert_metric(self, table, metric, value, unit):
    if table == "time_series":
      self.insert_metric_ts(metric, value, unit)
      return
    if table == "misc":
      sql = """INSERT INTO misc(misc_metric, misc_value, unit)
              VALUES(%s, %s, %s) RETURNING misc_id;"""
    elif table == "counter":
      sql = """INSERT INTO counter(counter_metric, counter_value, unit)
              VALUES(%s, %s, %s) RETURNING counter_id;"""

    if self.conn is None:
      self.establish_connection()
    try:
      self.cur.execute(sql, (metric, value, unit,))
      self.conn.commit
      # id = self.cur.fetchone()[0]
      # return [id, metric, value, unit]
    except (Exception, psycopg2.DatabaseError) as error:
      print(error)



  def insert_metric_ts(self, metric, value, unit):
    sql = """INSERT INTO time_series(ts_metric, ts_time, ts_value, unit)
            VALUES(%s, %s, %s, %s) RETURNING ts_id;"""
    if self.conn is None:
      self.establish_connection()
    try:
      seconds = int(time.time())
      self.cur.execute(sql, (metric, seconds, value, unit,))
      # id = self.cur.fetchone()[0]
      self.conn.commit()
      # return [id, metric, seconds, value, unit]
    except (Exception, psycopg2.DatabaseError) as error:
      print(error)



  def insert_metric_list(self, table, metric_list):
    if table == "time_series":
      self.insert_metric_list_ts(metric_list)
      return
    if table == "misc":
      sql = """INSERT INTO misc(misc_metric, misc_value, unit)
              VALUES(%s, %s, %s);"""
    elif table == "counter":
      sql = """INSERT INTO counter(counter_metric, counter_value, unit)
              VALUES(%s, %s, %s);"""

    try:
      self.cur.executemany(sql, metric_list)
      self.conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
      print(error)
  


  def insert_metric_list_ts(self, metric_list):
    sql = """INSERT INTO time_series(ts_metric, ts_value, unit, ts_time)
            VALUES(%s, %s, %s, %s);"""
    if self.conn is None:
      self.establish_connection()
    try:
      seconds = int(time.time())
      for i in range(len(metric_list)):
        metric_list[i] = metric_list[i] + (seconds,)
      self.cur.executemany(sql, metric_list)
      self.conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
      print(error)



  def update_metric(self, table, metric, new_value):
    if table == "time_series":
      self.update_metric_ts(metric, new_value)
      return
    
    metric_ref = table + "_metric"
    value_ref = table + "_value"
    query = f"""SELECT {value_ref} FROM {table} 
            WHERE {metric_ref} = '{metric}'"""
    sql = f""" UPDATE {table}
               SET {value_ref} = %s
               WHERE {metric_ref} = %s"""
    try:
      if table == "counter":
        self.cur.execute(query)
        old_value = self.cur.fetchone()[0]
        new_value = new_value + old_value
      self.cur.execute(sql, (new_value, metric,))
      self.conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
      print(error)
  


  def update_metric_ts(self, metric, new_value):
    query = f"""SELECT unit FROM time_series 
                WHERE ts_metric = '{metric}'
                ORDER BY ts_time"""
    sql = """INSERT INTO time_series(ts_metric, ts_time, ts_value, unit)
            VALUES(%s, %s, %s, %s) RETURNING ts_id;"""
   
    try:
      self.cur.execute(query)
      unit = self.cur.fetchone()[0]
      if unit:
        seconds = int(time.time())
        self.cur.execute(sql, (metric, seconds, new_value, unit,))
        self.conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
      print(error)



  def read_query(self, query):
    result = None
    try:
      self.cur.execute(query)
      result = self.cur.fetchall()
    except (Exception, psycopg2.DatabaseError) as err:
      print(f"Error: '{err}'")
    return result



  def get_all_metrics(self, table):
    id_ref = table + "_id"
    metric_ref = table + "_metric"
    value_ref = table + "_value"
    if table == "time_series":
      query = f"SELECT * FROM {table} ORDER BY ts_metric"
    else:
      query = f"SELECT {id_ref}, {metric_ref}, {value_ref}, unit FROM {table} ORDER BY {id_ref}"
    return self.read_query(query)



  def get_all_metric_names(self, table):
    if table == "time_series":
      query = f"SELECT DISTINCT ts_metric FROM {table}"
    else:
      query = f"SELECT {table}_metric FROM {table} ORDER BY {table}_id"
    return self.read_query(query)



  def get_metric(self, table, metric):

    id_ref = table + "_id"
    metric_ref = table + "_metric"
    value_ref = table + "_value"

    if table == "time_series":
      query = f"""
        SELECT * FROM {table}
        WHERE ts_metric = '{metric}'
        ORDER BY ts_time;
        """
    else:
      query = f"""
        SELECT {id_ref}, {metric_ref}, {value_ref}, unit
        FROM {table}
        WHERE {metric_ref} = '{metric}';
        """

    return self.read_query(query)



  def delete_metric(self, table, metric):
  
    rows_deleted = 0
    try:
      if table == "time_series":
        self.cur.execute(f"DELETE FROM {table} WHERE ts_metric = %s", (metric,))
      else:
        self.cur.execute(f"DELETE FROM {table} WHERE {table}_metric = %s", (metric,))
      rows_deleted = self.cur.rowcount
      self.conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
      print(error)

    return rows_deleted





db = database(config())
# db.create_tables()
# db.insert_metric("time_series", "storage", 20, "GB")
# db.insert_metric("time_series", "storage", 25, "GB")
# db.insert_metric("time_series", "storage", 30, "GB")
# db.insert_metric_list("time_series", [
#   ("alpha", 10, "MB",),
#   ("beta", 20, "MB",),
#   ("theta", 30, "MB",),
#   ("gamma", 40, "MB",),
# ])
# db.update_metric_ts("storage", 13)

# metrics = db.get_all_metrics("time_series")
# metrics = db.get_metric("time_series", "storage")
# names = db.get_all_metric_names("time_series")
# print(metrics)

# db.delete_metric("time_series", "storage")

# db.delete_metric("misc", "test")
# db.insert_metric("counter", "test", 100, "kg")
# db.insert_metric("misc", "test", 100, "kg")
# db.insert_metric_list("misc",[
#   ("gamma", 40, "MB",),
#   ("test", 100, "kg")
# ])

# db.update_metric("counter", "RAM", )



# def create_tables():
#   """ create 3 tables """
#   commands = (
#     """
#     CREATE TABLE IF NOT EXISTS misc (
#       misc_id SERIAL PRIMARY KEY,
#       misc_metric VARCHAR(255) UNIQUE NOT NULL,
#       misc_value FLOAT,
#       unit VARCHAR(255) NOT NULL
#     )
#     """,

#     """
#     CREATE TABLE IF NOT EXISTS counter (
#       counter_id SERIAL PRIMARY KEY,
#       counter_metric VARCHAR(255) UNIQUE NOT NULL,
#       counter_value FLOAT,
#       unit VARCHAR(255) NOT NULL
#     )
#     """)
#   conn = None
#   try:
#     params = config()
#     conn = psycopg2.connect(**params)
#     cur = conn.cursor()

#     # execute create table commands
#     for command in commands:
#         cur.execute(command)
#     # commit the changes
#     conn.commit()
#     cur.close()
#   except (Exception, psycopg2.DatabaseError) as error:
#     print(error)
#   finally:
#     if conn is not None:
#       conn.close()



# def insert_metric(table, metric, value, unit):
#   if table == "misc":
#     sql = """INSERT INTO misc(misc_metric, misc_value, unit)
#             VALUES(%s, %s, %s) RETURNING misc_id;"""
#   elif table == "counter":
#     sql = """INSERT INTO counter(counter_metric, counter_value, unit)
#             VALUES(%s, %s, %s) RETURNING counter_id;"""
#   conn = None
#   id = None

#   try:
#     params = config()
#     conn = psycopg2.connect(**params)
#     cur = conn.cursor()
#     # execute the INSERT statement
#     cur.execute(sql, (metric, value, unit,))
#     id = cur.fetchone()[0]
#     conn.commit()
#     cur.close()
#   except (Exception, psycopg2.DatabaseError) as error:
#     print(error)
#   finally:
#     if conn is not None:
#       conn.close()



# def insert_metric_list(table, metric_list):
#   if table == "misc":
#     sql = """INSERT INTO misc(misc_metric, misc_value, unit)
#             VALUES(%s, %s, %s);"""
#   elif table == "counter":
#     sql = """INSERT INTO counter(counter_metric, counter_value, unit)
#             VALUES(%s, %s, %s);"""
#   conn = None

#   try:
#     params = config()
#     conn = psycopg2.connect(**params)
#     cur = conn.cursor()
#     # execute the INSERT statement
#     cur.executemany(sql, metric_list)
#     conn.commit()
#     cur.close()
#   except (Exception, psycopg2.DatabaseError) as error:
#     print(error)
#   finally:
#     if conn is not None:
#       conn.close()



# def update_metric(table, metric, new_value):

#   metric_ref = table + "_metric"
#   value_ref = table + "_value"

#   sql = f""" UPDATE {table}
#               SET {value_ref} = %s
#               WHERE {metric_ref} = %s"""
#   conn = None

#   try:
#     params = config()
#     conn = psycopg2.connect(**params)
#     cur = conn.cursor()
#     # execute the INSERT statement
#     cur.execute(sql, (new_value, metric,))
#     conn.commit()
#     cur.close()
#   except (Exception, psycopg2.DatabaseError) as error:
#     print(error)
#   finally:
#     if conn is not None:
#       conn.close()



# def read_query(conn, query):
#   cur = conn.cursor()
#   result = None
#   try:
#     cur.execute(query)
#     result = cur.fetchall()
#     cur.close()
#   except (Exception, psycopg2.DatabaseError) as err:
#     print(f"Error: '{err}'")
#   finally:
#     if conn is not None:
#       conn.close()

#   return result



# def get_all_metrics(table):

#   id_ref = table + "_id"
#   metric_ref = table + "_metric"
#   value_ref = table + "_value"

#   query = f"SELECT {id_ref}, {metric_ref}, {value_ref}, unit FROM {table} ORDER BY {id_ref}"

#   params = config()
#   conn = psycopg2.connect(**params)
#   return read_query(conn, query)



# def get_all_metric_names(table):
#   query = f"SELECT {table}_metric FROM {table} ORDER BY {table}_id"
#   params = config()
#   conn = psycopg2.connect(**params)
#   return read_query(conn, query)



# def get_metric(table, metric):

#   id_ref = table + "_id"
#   metric_ref = table + "_metric"
#   value_ref = table + "_value"

#   query = f"""
#     SELECT {id_ref}, {metric_ref}, {value_ref}, unit
#     FROM {table}
#     WHERE {metric_ref} = '{metric}';
#     """
  
#   params = config()
#   conn = psycopg2.connect(**params)
#   return read_query(conn, query)



# def delete_metric(table, metric):
  
#   conn = None
#   rows_deleted = 0
#   try:
#     params = config()
#     conn = psycopg2.connect(**params)
#     cur = conn.cursor()
#     cur.execute(f"DELETE FROM {table} WHERE {table}_metric = %s", (metric,))
#     rows_deleted = cur.rowcount
#     conn.commit()
#     cur.close()
#   except (Exception, psycopg2.DatabaseError) as error:
#     print(error)
#   finally:
#     if conn is not None:
#       conn.close()

#   return rows_deleted








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


