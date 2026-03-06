import styles from './Input.module.css';

export default function Input({
    label,
    error,
    icon,
    type = 'text',
    className = '',
    ...props
}) {
    const isTextarea = type === 'textarea';
    const isSelect = type === 'select';
    const Tag = isTextarea ? 'textarea' : isSelect ? 'select' : 'input';

    return (
        <div className={`${styles.wrapper} ${className}`}>
            {label && <label className={styles.label}>{label}</label>}
            <div className={styles.inputWrapper}>
                {icon && <span className={styles.icon}>{icon}</span>}
                <Tag
                    className={`${isSelect ? styles.select : isTextarea ? styles.textarea : styles.input} ${icon ? styles.hasIcon : ''} ${error ? styles.error : ''}`}
                    type={!isTextarea && !isSelect ? type : undefined}
                    {...props}
                />
            </div>
            {error && <span className={styles.errorText}>{error}</span>}
        </div>
    );
}
