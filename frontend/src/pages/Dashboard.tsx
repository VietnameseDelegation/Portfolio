import styles from '../common.module.css';

export function Dashboard() {
    return (
        <div className={styles.pageContainer}>
            <div className={styles.header}>
                <h1 className={styles.title}>Dashboard</h1>
            </div>
            <div style={{ display: 'grid', gap: '1rem', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))' }}>
                <div className={styles.tableContainer} style={{ padding: '2rem' }}>
                    <h2>Welcome to OrderSystem</h2>
                    <p style={{ color: 'var(--text-secondary)' }}>
                        Select a module from the sidebar to manage your data.
                    </p>
                </div>
            </div>
        </div>
    );
}
