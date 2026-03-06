import styles from './Card.module.css';

export default function Card({ title, actions, children, padding = true, className = '' }) {
    return (
        <div className={`${styles.card} ${className}`}>
            {(title || actions) && (
                <div className={styles.header}>
                    {title && <h3 className={styles.headerTitle}>{title}</h3>}
                    {actions && <div>{actions}</div>}
                </div>
            )}
            <div className={`${styles.body} ${!padding ? styles.noPadding : ''}`}>
                {children}
            </div>
        </div>
    );
}
