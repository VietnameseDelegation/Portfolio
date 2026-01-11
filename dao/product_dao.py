from typing import Optional, List
from database.db_connector import DBConnector
from models.product import ProductDTO

class ProductDAO:
    def __init__(self, connector: DBConnector):
        self.connector = connector

    def create(self, product: ProductDTO) -> int:
        # Assuming category_id matches an existing category. 
        # For simplicity, we might default active to 1.
        query = "INSERT INTO products (name, price, category_id, active) VALUES (?, ?, ?, ?); SELECT SCOPE_IDENTITY() AS id;"
        result = self.connector.execute_query(query, (product.name, product.price, product.category_id, product.active))
        return int(result.iloc[0]['id'])

    def get_by_id(self, product_id: int) -> Optional[ProductDTO]:
        query = "SELECT id, name, price, category_id, active FROM products WHERE id = ?"
        result = self.connector.execute_query(query, (product_id,))
        
        if result.empty:
            return None
            
        row = result.iloc[0]
        return ProductDTO(
            id=int(row['id']),
            name=row['name'],
            price=float(row['price']),
            category_id=int(row['category_id']),
            active=bool(row['active'])
        )

    def get_by_ids(self, product_ids: List[int]) -> List[ProductDTO]:
        if not product_ids:
            return []
            
        placeholders = ','.join(['?'] * len(product_ids))
        query = f"SELECT id, name, price, category_id, active FROM products WHERE id IN ({placeholders})"
        result = self.connector.execute_query(query, tuple(product_ids))
        
        products = []
        if not result.empty:
            for _, row in result.iterrows():
                products.append(ProductDTO(
                    id=int(row['id']),
                    name=row['name'],
                    price=float(row['price']),
                    category_id=int(row['category_id']),
                    active=bool(row['active'])
                ))
        return products

    def get_all(self) -> List[ProductDTO]:
        query = "SELECT id, name, price, category_id, active FROM products"
        result = self.connector.execute_query(query)
        products = []
        if not result.empty:
            for _, row in result.iterrows():
                products.append(ProductDTO(
                    id=int(row['id']),
                    name=row['name'],
                    price=float(row['price']),
                    category_id=int(row['category_id']),
                    active=bool(row['active'])
                ))
        return products
