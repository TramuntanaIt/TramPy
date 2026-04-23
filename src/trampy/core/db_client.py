import pyodbc
import logging
import os

class UniversalDBClient:
    def __init__(self, dbServer, dbName, dbUser, dbPass, dbDriver = '{ODBC Driver 18 for SQL Server}' ):
        self.log = logging.getLogger(__name__)
        self.conn = None
        self.server = dbServer
        self.database = dbName
        self.username = dbUser
        self.password = dbPass
        self.driver = dbDriver

    def connect(self):
        try:
            conn_str = (
                f"DRIVER={self.driver};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"UID={self.username};"
                f"PWD={self.password};"
                "TrustServerCertificate=yes;" # Útil per a servidors locals
            )
            self.conn = pyodbc.connect(conn_str)
            self.log.info("✅ Connexió a la DB establerta amb èxit.")
            return True
        except Exception as e:
            self.log.error(f"❌ Error connectant a la DB: {e}")
            return False

    def execute_query(self, query, params=None):
        if not self.conn:
            self.connect()
        cursor = self.conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor
        except Exception as e:
            self.log.error(f"❌ Error executant query: {e}")
            return None
        
    def execute_stored_procedure(self, sp_name, params=None):
        """
        Executa un Stored Procedure i retorna el cursor.
        sp_name: Nom del procediment (ex: 'sp_GetProductUpdates')
        params: Llista o tupla de paràmetres (ex: ['2024-01-01', 10])
        """
        if not self.conn:
            self.connect()
            
        cursor = self.conn.cursor()
        try:
            # Construïm la crida: {CALL nom_sp (?, ?, ...)}
            # Aquesta sintaxi ODBC és la més robusta per a SQL Server
            if params:
                placeholders = ",".join(["?"] * len(params))
                sql = f"{{CALL {sp_name} ({placeholders})}}"
                cursor.execute(sql, params)
            else:
                sql = f"{{CALL {sp_name}}}"
                cursor.execute(sql)
            
            # Si el procediment fa modificacions (INSERT/UPDATE), fem commit
            #self.conn.commit() 
            return cursor
        except Exception as e:
            self.log.error(f"❌ Error executant Stored Procedure '{sp_name}': {e}")
            if self.conn:
                self.conn.rollback()
            return None        