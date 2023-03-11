from pymongo import MongoClient
import urllib.parse


"""
This class has the methods which handle the database operations.
connect_to_database method is used to connect to the database,create a database and create a collection.
If the database and collection already exists, it will connect to the database and collection.
close_database method is used to close the connection to the database.

"""

class DatabaseHandlers:
    def __init__(self) -> None:

        """
        This function is used to initialize the class variables.

        Args:
            An instance of the class.

        Returns:
            None
        """
        # reading the username and password from the file and storing it in the class variables
        with open("credential.txt", "r") as f:
            self.username = urllib.parse.quote_plus(f.readline().strip())
            self.password = urllib.parse.quote_plus(f.readline().strip())

        # Creating a client object to connect to the database
        self.client = MongoClient(
            "your_mongo_client_url"
            % (self.username, self.password)
        )

    def connect_database(self):

        """
        This function is used to connect to the database, create a database and create a collection.

        Args:
            An instance of the class.

        Returns:
            A string which indicates whether the connection to the database was successful or not.
        """
        # Connecting to the database
        try:
            self.db = self.client["DatabaseName"]
            self.collection = self.db["CollectionName"]
            return f"Connected to database {self.db.name} successfully!"

        except:
            return "Error connecting to database!"

    def close_database(self):

        """
        This function is used to close the connection to the database.

        Args:
            An instance of the class.

        Returns:
            A string which indicates whether the connection to the database was closed successfully or not.
        """
        # Closing the connection to the database
        try:
            self.client.close()
            return "Connection closed successfully!"

        except:
            return "Error closing connection!" 
        
