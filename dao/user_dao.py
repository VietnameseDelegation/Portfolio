from typing import Optional
from database.db_connector import DBConnector
from models.user import UserDTO

class UserDAO:
    def __init__(self, connector: DBConnector):
        self.connector = connector

    def create(self, user: UserDTO) -> int:
        query = "INSERT INTO users (name, email, registered_at) VALUES (?, ?, ?); SELECT SCOPE_IDENTITY() AS id;"
        result = self.connector.execute_query(query, (user.name, user.email, user.registered_at))
        return int(result.iloc[0]['id'])

    def get_by_email(self, email: str) -> Optional[UserDTO]:
        query = "SELECT id, name, email, registered_at FROM users WHERE email = ?"
        result = self.connector.execute_query(query, (email,))
        
        if result.empty:
            return None
            
        row = result.iloc[0]
        return UserDTO(
            id=int(row['id']),
            name=row['name'],
            email=row['email'],
            registered_at=row['registered_at']
        )

    def get_by_id(self, user_id: int) -> Optional[UserDTO]:
        query = "SELECT id, name, email, registered_at FROM users WHERE id = ?"
        result = self.connector.execute_query(query, (user_id,))
        
        if result.empty:
            return None
            
        row = result.iloc[0]
        return UserDTO(
            id=int(row['id']),
            name=row['name'],
            email=row['email'],
            registered_at=row['registered_at']
        )
