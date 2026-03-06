import styles from './Table.module.css';

export default function Table({ columns, data, onSort, emptyMessage = 'No data', className = '' }) {
    if (!data || data.length === 0) {
        return (
            <div className={styles.wrapper}>
                <div className={styles.empty}>{emptyMessage}</div>
            </div>
        );
    }

    return (
        <div className={`${styles.wrapper} ${className}`}>
            <table className={styles.table}>
                <thead>
                    <tr>
                        {columns.map((col) => (
                            <th
                                key={col.key}
                                className={col.sortable ? styles.sortable : ''}
                                onClick={() => col.sortable && onSort?.(col.key)}
                                style={col.width ? { width: col.width } : undefined}
                            >
                                {col.label}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {data.map((row, i) => (
                        <tr key={row.id || i}>
                            {columns.map((col) => (
                                <td key={col.key}>
                                    {col.render ? col.render(row) : row[col.key]}
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
