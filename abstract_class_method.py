from abc import ABC, abstractmethod


class DatabaseConnector(ABC):
    @classmethod
    @abstractmethod
    def create_connection(cls, host, port):
        pass

    @abstractmethod
    def execute_query(self, query):
        pass


class PostgreSQLConnector(DatabaseConnector):
    @classmethod
    def create_connection(cls, host, port):
        print(f"Connecting to PostgreSql at {host}:{port}")
        return cls

    def execute_query(self, query):
        return f"postgreSQL running on query:{query}"


class MongoDBConnector(DatabaseConnector):
    @classmethod
    def create_connection(cls, host, port):
        print(f"Connecting to MongoDB at {host}:{port}")
        return cls

    def execute_query(self, query):
        return f"MongoDB running on query:{query}"


c = PostgreSQLConnector.create_connection("local host", 8001)
d = MongoDBConnector.create_connection("local host", 5000)
print(c.create_connection("Global Host", 5678))
print(d.execute_query("Select name from the table of database"))
print(c.execute_query("select age from 3rd row"))
