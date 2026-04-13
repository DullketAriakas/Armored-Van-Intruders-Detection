import sqlite3

class DataBase:

    def __init__(self,db_name,table):
        """
        Inicialización del objeto
        
        Args:
            db_name (str): Nombre de la BDD en la que se va a trabajar
            table (str): Nombre de la tabla con la que se quiere trabajar

        """
        self.db= db_name
        self.table = table
        self.connection = sqlite3.connect(db_name + '.db')
        self.connection.row_factory = sqlite3.Row
        self.columns=None # Se guardan al crear la tabla
    
    def _load_columns_from_table(self):
        """
        Carga el esquema de columnas desde la tabla existente en la base de datos.

        Raises:
            sqlite3.Error: Si ocurre un error al consultar el esquema
        """
        cursor = self.connection.cursor()
        cursor.execute(f"PRAGMA table_info({self.table})")
        
        rows = cursor.fetchall()
        
        self.columns = []
        for row in rows:
            col_info = {
                'nombre': row[1],  # column name
                'tipo': row[2],    # data type
            }
            
            # Agregar restricciones si existen
            restricciones = []
            if row[3]:  # notnull
                restricciones.append('NOT NULL')
            if row[5]:  # primary key
                restricciones.append('PRIMARY KEY')
            
            if restricciones:
                col_info['restricciones'] = ' '.join(restricciones)
            
            self.columns.append(col_info)
    
    def close_connection(self):
        """
        Cierra la conexión a la base de datos
        
        Returns:
            bool: True si se cerró correctamente, False en caso contrario
        
        Raises:
            Exception: Propaga cualquier excepción que ocurra al cerrar
        
        """
        try:
            return self.connection.close()
        except Exception as e:
            print(f"Error {e}")
            raise


    def create_table(self,columns):

        """
        Crea la tabla inicializada en la base de datos

        Args:
            columns (dict): Diccionario con definiciones de columnas
                            [{'name': str, 'type': str, 'restrictions': str (opcional)}]
        
        Returns:
            bool: True si se creó, False si ya existía
      
        Raises:
            Exception: Propaga cualquier excepción que ocurra al ejecutar la query
        
        """
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name=?
        ''', (self.table,))
        
        if cursor.fetchone() is not None:
            print(f"La tabla '{self.table}' ya existe")
            self._load_columns_from_table()
            return False


        definitions = []
        for col in columns:
            definition = f"{col['name']} {col['type']}"
            if 'restrictions' in col:
                definition += f" {col['restrictions']}"
            definitions.append(definition)

        columns_sql = ',\n            '.join(definitions)

        query = f'''
        CREATE TABLE IF NOT EXISTS {self.table} (
        {columns_sql}
        )
        '''
        try:
            with self.connection:
                self.connection.execute(query)

            self.columns = columns
            print(f"Table {self.table} was created")
            return True
        except Exception as e:
            print(f"Error {e}")
            raise

    def insert(self, row):
        """
        Obtiene todas las columnas de la tabla con una condición dada
        
        Args:
            row (dic): Diccionario con los pares columna - dato que se quieren insertar en la tabla
        
        Raises:
            Exception: Propaga cualquier excepción que ocurra al ejecutar la query
        
        """

        # Verificar que las columnas del diccionario existen en la tabla
        if self.columns:
            columns_table = [col['name'] for col in self.columns]
            for column in row.keys():
                if column not in columns_table:
                    raise ValueError(f"La columna '{column}' no existe en la tabla {self.table}")
        
        # Construir la query dinámicamente
        columns = ', '.join(row.keys())
        placeholders = ', '.join(['?' for _ in row])
        values = tuple(row.values())
        
        query = f"INSERT INTO {self.table} ({columns}) VALUES ({placeholders})"
        
        try:
            with self.connection:
                self.connection.execute(query, values)
            print(f"The row has been added to {self.table}")
        except Exception as e:
            print(f"Error {e}")
            raise


    def get(self, condition:str=None):
        """
        Obtiene todas las columnas de la tabla con una condición dada
        
        Args:
            condition (str)(optional): Condición en formato SQL para realizar la búsqueda
        
        Returns:
            dict: Diccionario con las filas de datos obtenidas de la tabla con la condicion dada
        
        Raises:
            Exception: Propaga cualquier excepción que ocurra al ejecutar la query
        
        """
        query=f"SELECT * FROM {self.table}"
        if condition:
            query+=f"WHERE {condition}"
        try:
            with self.connection:
                cursor=self.connection.execute(query)
            rows = []
            for row in cursor:
                print(dict(row))
                rows.append(row)
            return dict(rows)
        except Exception as e:
            print(f"Error {e}")
            raise
    
    def delete_byId(self, id):
        """
        Se elimina el elemento seleccionado dado un id único
        
        Args:
            id (int): Id del objeto a eliminar
        
        Raises:
            Exception: Propaga cualquier excepción que ocurra al ejecutar la query
        
        """
        query=f"DELETE FROM {self.table} WHERE id = ?"

        try:
            with self.connection:
                self.connection.execute(query,(id))
            print(f"The row with id {id} been deleted from {self.table}")

        except Exception as e:
            print(f"Error {e}")
            raise