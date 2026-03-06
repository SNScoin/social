import styles from './Spinner.module.css';

export default function Spinner({ size = 'md', label }) {
    return (
        <div className={styles.container}>
            <span className={`${styles.spinner} ${styles[size]}`} />
            {label && <span>{label}</span>}
        </div>
    );
}
