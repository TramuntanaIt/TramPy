from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import logging

log = logging.getLogger("IMPORT_API_SQL") # Recuperem el logger

class UniversalDBClient:
    def __init__(self, connection_string):
        try:
            self.engine = create_engine(connection_string, echo=False, connect_args={'timeout': 10})
            # Provem la connexió immediatament
            with self.engine.connect() as conn:
                pass
            log.info("Connexió a la BBDD establerta correctament.")
        except SQLAlchemyError as e:
            log.error(f"Error connectant a la BBDD: Verifiqueu si el Driver ODBC està instal·lat. Detalls: {e}")
            raise

    def execute_query(self, query, params=None):
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query), params or {})
                return [dict(row._mapping) for row in result]
        except SQLAlchemyError as e:
            log.error(f"Error executant consulta SQL: {e}")
            return []            