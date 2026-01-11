import { useEffect, useState } from 'react';
import type { Order } from '../types';
import styles from '../common.module.css';

export function OrdersPage() {
    const [orders, setOrders] = useState<Order[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch('http://localhost:8000/api/orders/')
            .then(res => res.json())
            .then(data => {
                setOrders(data);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    }, []);

    return (
        <div className={styles.pageContainer}>
            <div className={styles.header}>
                <h1 className={styles.title}>Orders</h1>
            </div>

            <div className={styles.tableContainer}>
                <table className={styles.table}>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Status</th>
                            <th>Paid</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr><td colSpan={3}>Loading...</td></tr>
                        ) : orders.map(order => (
                            <tr key={order.id}>
                                <td>{new Date(order.order_date).toLocaleDateString()}</td>
                                <td>
                                    <span style={{
                                        padding: '0.25rem 0.5rem',
                                        borderRadius: '4px',
                                        backgroundColor: order.status === 'paid' ? '#03dac6' : '#cf6679',
                                        color: '#000',
                                        fontSize: '0.8rem',
                                        fontWeight: 'bold'
                                    }}>
                                        {order.status}
                                    </span>
                                </td>
                                <td>{order.paid ? 'Yes' : 'No'}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
