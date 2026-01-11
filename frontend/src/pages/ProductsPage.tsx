import { useEffect, useState } from 'react';
import type { Product, Category } from '../types';
import styles from '../common.module.css';
import { Modal } from '../components/Modal';

export function ProductsPage() {
    const [products, setProducts] = useState<Product[]>([]);
    const [categories, setCategories] = useState<Category[]>([]);
    const [loading, setLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [newProduct, setNewProduct] = useState({ name: '', price: 0, category_id: 1, active: true });

    const fetchData = () => {
        setLoading(true);
        Promise.all([
            fetch('http://localhost:8000/api/products/').then(res => res.json()),
            fetch('http://localhost:8000/api/products/categories').then(res => res.json())
        ]).then(([productsData, categoriesData]) => {
            setProducts(productsData);
            setCategories(categoriesData);
            setLoading(false);
            // Default category ID to first one if available
            if (categoriesData.length > 0) {
                setNewProduct(prev => ({ ...prev, category_id: categoriesData[0].id }));
            }
        }).catch(err => {
            console.error(err);
            setLoading(false);
        });
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleCreateProduct = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            const res = await fetch('http://localhost:8000/api/products/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(newProduct)
            });
            if (res.ok) {
                setIsModalOpen(false);
                // Reset form but keep last selected category or default
                setNewProduct(prev => ({ name: '', price: 0, category_id: prev.category_id, active: true }));
                // Re-fetch only products
                fetch('http://localhost:8000/api/products/')
                    .then(r => r.json())
                    .then(d => setProducts(d));
            } else {
                alert('Failed to create product');
            }
        } catch (error) {
            console.error(error);
            alert('Error creating product');
        }
    };

    const getCategoryName = (id: number) => {
        const cat = categories.find(c => c.id === id);
        return cat ? cat.name : id;
    };

    return (
        <div className={styles.pageContainer}>
            <div className={styles.header}>
                <h1 className={styles.title}>Products</h1>
                <button className={styles.button} onClick={() => setIsModalOpen(true)}>Add Product</button>
            </div>

            <div className={styles.tableContainer}>
                <table className={styles.table}>
                    <thead>
                        <tr>
                            <th>Name</th>
                            <th>Price</th>
                            <th>Category</th>
                            <th>Active</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr><td colSpan={4}>Loading...</td></tr>
                        ) : products.map(product => (
                            <tr key={product.id}>
                                <td>{product.name}</td>
                                <td>${product.price.toFixed(2)}</td>
                                <td>{getCategoryName(product.category_id)}</td>
                                <td>{product.active ? 'Yes' : 'No'}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} title="Add Product">
                <form onSubmit={handleCreateProduct} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem' }}>Name</label>
                        <input
                            type="text"
                            value={newProduct.name}
                            onChange={e => setNewProduct({ ...newProduct, name: e.target.value })}
                            required
                            style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #333', backgroundColor: '#333', color: '#fff' }}
                        />
                    </div>
                    <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem' }}>Price</label>
                        <input
                            type="number"
                            step="0.01"
                            value={newProduct.price}
                            onChange={e => setNewProduct({ ...newProduct, price: parseFloat(e.target.value) })}
                            required
                            style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #333', backgroundColor: '#333', color: '#fff' }}
                        />
                    </div>
                    <div>
                        <label style={{ display: 'block', marginBottom: '0.5rem' }}>Category</label>
                        <select
                            value={newProduct.category_id}
                            onChange={e => setNewProduct({ ...newProduct, category_id: parseInt(e.target.value) })}
                            style={{ width: '100%', padding: '0.5rem', borderRadius: '4px', border: '1px solid #333', backgroundColor: '#333', color: '#fff' }}
                        >
                            {categories.map(cat => (
                                <option key={cat.id} value={cat.id}>{cat.name}</option>
                            ))}
                        </select>
                    </div>
                    <div>
                        <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                            <input
                                type="checkbox"
                                checked={newProduct.active}
                                onChange={e => setNewProduct({ ...newProduct, active: e.target.checked })}
                            />
                            Active
                        </label>
                    </div>
                    <button type="submit" className={styles.button} style={{ marginTop: '1rem' }}>Create Product</button>
                </form>
            </Modal>
        </div>
    );
}
