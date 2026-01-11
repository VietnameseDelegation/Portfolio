import { useState, useEffect } from 'react';
import styles from '../common.module.css';

export function ETLPage() {
    const [logs, setLogs] = useState('');
    const [loading, setLoading] = useState(false);

    const fetchLogs = async () => {
        try {
            const res = await fetch('http://localhost:8000/api/etl/logs');
            const data = await res.json();
            setLogs(data.logs);
        } catch (e) {
            console.error("Failed to fetch logs", e);
        }
    };

    useEffect(() => {
        fetchLogs();
        const interval = setInterval(fetchLogs, 5000); // Poll logs
        return () => clearInterval(interval);
    }, []);

    const runImport = async () => {
        setLoading(true);
        await fetch('http://localhost:8000/api/etl/import', { method: 'POST' });
        setLoading(false);
        fetchLogs();
    };

    const runExport = async () => {
        setLoading(true);
        await fetch('http://localhost:8000/api/etl/export', { method: 'POST' });
        setLoading(false);
        fetchLogs();
    };

    return (
        <div className={styles.pageContainer}>
            <div className={styles.header}>
                <h1 className={styles.title}>ETL Control</h1>
                <div style={{ display: 'flex', gap: '1rem' }}>
                    <button className={styles.button} onClick={runImport} disabled={loading}>
                        {loading ? 'Running...' : 'Run Import'}
                    </button>
                    <button className={styles.button} onClick={runExport} disabled={loading} style={{ backgroundColor: '#03dac6' }}>
                        Run Export
                    </button>
                </div>
            </div>

            <div className={styles.tableContainer} style={{ padding: '1rem' }}>
                <h3>Process Logs</h3>
                <div style={{
                    backgroundColor: '#000',
                    color: '#0f0',
                    fontFamily: 'monospace',
                    padding: '1rem',
                    height: '400px',
                    overflowY: 'auto',
                    borderRadius: '4px',
                    whiteSpace: 'pre-wrap'
                }}>
                    {logs || 'No logs available.'}
                </div>
            </div>
        </div>
    );
}
