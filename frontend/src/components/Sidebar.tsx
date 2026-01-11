import { NavLink } from 'react-router-dom';
import styles from './Sidebar.module.css';

export function Sidebar() {
    return (
        <aside className={styles.sidebar}>
            <div className={styles.logo}>OrderSystem</div>
            <nav className={styles.nav}>
                <NavLink
                    to="/"
                    className={({ isActive }) => `${styles.link} ${isActive ? styles.active : ''}`}
                >
                    Dashboard
                </NavLink>
                <NavLink
                    to="/products"
                    className={({ isActive }) => `${styles.link} ${isActive ? styles.active : ''}`}
                >
                    Products
                </NavLink>
                <NavLink
                    to="/orders"
                    className={({ isActive }) => `${styles.link} ${isActive ? styles.active : ''}`}
                >
                    Orders
                </NavLink>
                <NavLink
                    to="/users"
                    className={({ isActive }) => `${styles.link} ${isActive ? styles.active : ''}`}
                >
                    Users
                </NavLink>
                <NavLink
                    to="/etl"
                    className={({ isActive }) => `${styles.link} ${isActive ? styles.active : ''}`}
                >
                    ETL Control
                </NavLink>
            </nav>
        </aside>
    );
}
