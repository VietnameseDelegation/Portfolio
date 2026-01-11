from typing import List
from database.db_connector import DBConnector
from models.category import CategoryDTO

class CategoryDAO:
    def __init__(self, connector: DBConnector):
        self.connector = connector

    def get_all(self) -> List[CategoryDTO]:
        query = "SELECT id, name FROM categories"
        result = self.connector.execute_query(query)
        categories = []
        if not result.empty:
            for _, row in result.iterrows():
                categories.append(CategoryDTO(
                    id=int(row['id']),
                    name=row['name']
                ))
        return categories
