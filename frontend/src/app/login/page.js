'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { toast } from 'react-toastify';
import Image from 'next/image';
import api from '@/lib/api';
import styles from './page.module.css';
import {
    HiOutlineEnvelope,
    HiOutlineLockClosed,
    HiOutlineEye,
    HiOutlineEyeSlash,
    HiOutlineArrowRightOnRectangle,
    HiOutlineSun,
    HiOutlineMoon,
} from 'react-icons/hi2';

export default function LoginPage() {
    const router = useRouter();
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [showPassword, setShowPassword] = useState(false);
    const [rememberMe, setRememberMe] = useState(false);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [theme, setTheme] = useState('light');

    useEffect(() => {
        const saved = localStorage.getItem('theme');
        if (saved) {
            setTheme(saved);
            document.documentElement.setAttribute('data-theme', saved);
        } else if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
            setTheme('dark');
            document.documentElement.setAttribute('data-theme', 'dark');
        }
    }, []);

    const toggleTheme = () => {
        const next = theme === 'light' ? 'dark' : 'light';
        setTheme(next);
        document.documentElement.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!email.trim() || !password.trim()) {
            setError('Please fill in all fields');
            return;
        }
        setError('');
        setLoading(true);
        try {
            const res = await api.post('/auth/login', { email: email.trim(), password });
            localStorage.setItem('access_token', res.data.token);
            if (rememberMe) {
                localStorage.setItem('remember_me', 'true');
            }
            router.push('/companies');
        } catch (err) {
            setError(err.response?.data?.message || 'Invalid credentials');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className={styles.page}>
            {/* ── Top Navbar ── */}
            <header className={styles.topbar}>
                <div className={styles.topbarLogo}>
                    <span className={styles.topbarLogoIcon}>📊</span>
                    Social Stats
                </div>
                <div className={styles.topbarRight}>
                    <button className={styles.langBadge}>
                        🇺🇸 EN <span style={{ fontSize: '10px' }}>▾</span>
                    </button>
                    <button className={styles.themeBtn} onClick={toggleTheme} title="Toggle theme">
                        {theme === 'light' ? <HiOutlineMoon /> : <HiOutlineSun />}
                    </button>
                </div>
            </header>

            {/* ── Card ── */}
            <main className={styles.main}>
                <div className={styles.card}>
                    {/* Logo / Icon */}
                    <div className={styles.logo}>
                        <div className={styles.logoIcon}>
                            <Image src="/assets/images/login/login.png" alt="Login" width={48} height={48} priority />
                        </div>
                        <h1 className={styles.title}>Welcome Back</h1>
                        <p className={styles.subtitle}>Please sign in to continue</p>
                    </div>

                    {/* Error */}
                    {error && <div className={styles.error}>{error}</div>}

                    {/* Form */}
                    <form className={styles.form} onSubmit={handleSubmit}>
                        {/* Email */}
                        <div className={styles.field}>
                            <label className={styles.label}>Email Address</label>
                            <div className={styles.inputWrapper}>
                                <span className={styles.inputIcon}><HiOutlineEnvelope /></span>
                                <input
                                    className={styles.input}
                                    type="email"
                                    placeholder="admin@example.com"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    disabled={loading}
                                    autoComplete="email"
                                />
                                <div className={styles.inputActions}>
                                    {email && (
                                        <button type="button" className={styles.clearBtn} onClick={() => setEmail('')} title="Clear">
                                            ✕
                                        </button>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* Password */}
                        <div className={styles.field}>
                            <label className={styles.label}>Password</label>
                            <div className={styles.inputWrapper}>
                                <span className={styles.inputIcon}><HiOutlineLockClosed /></span>
                                <input
                                    className={styles.input}
                                    type={showPassword ? 'text' : 'password'}
                                    placeholder="••••••••••"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    disabled={loading}
                                    autoComplete="current-password"
                                />
                                <div className={styles.inputActions}>
                                    {password && (
                                        <button type="button" className={styles.clearBtn} onClick={() => setPassword('')} title="Clear">
                                            ✕
                                        </button>
                                    )}
                                    <button
                                        type="button"
                                        className={styles.inputActionBtn}
                                        onClick={() => setShowPassword(!showPassword)}
                                        title={showPassword ? 'Hide password' : 'Show password'}
                                    >
                                        {showPassword ? <HiOutlineEyeSlash /> : <HiOutlineEye />}
                                    </button>
                                </div>
                            </div>
                        </div>

                        {/* Options row */}
                        <div className={styles.options}>
                            <label className={styles.remember}>
                                <input
                                    type="checkbox"
                                    className={styles.checkbox}
                                    checked={rememberMe}
                                    onChange={(e) => setRememberMe(e.target.checked)}
                                />
                                Remember me
                            </label>
                            <button type="button" className={styles.forgot}>Forgot your password?</button>
                        </div>

                        {/* Sign In */}
                        <button type="submit" className={styles.signInBtn} disabled={loading}>
                            <span className={styles.signInBtnIcon}><HiOutlineArrowRightOnRectangle /></span>
                            {loading ? 'Signing in...' : 'Sign In'}
                        </button>
                    </form>

                    {/* Divider */}
                    <div className={styles.divider}>
                        <div className={styles.dividerLine} />
                        <span className={styles.dividerText}>Or continue with</span>
                        <div className={styles.dividerLine} />
                    </div>

                    {/* Social */}
                    <div className={styles.socialRow}>
                        <button type="button" className={styles.socialBtn}>
                            <span className={styles.socialIcon}>
                                <svg width="18" height="18" viewBox="0 0 24 24"><path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z" /><path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" /><path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" /><path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" /></svg>
                            </span>
                            Google
                        </button>
                        <button type="button" className={styles.socialBtn}>
                            <span className={styles.socialIcon}>
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.8-.91.65.03 2.47.26 3.64 1.98-.09.06-2.17 1.28-2.15 3.81.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.83M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z" /></svg>
                            </span>
                            Apple
                        </button>
                    </div>
                </div>
            </main>

            {/* ── Footer ── */}
            <footer className={styles.footer}>
                © 2026 <a href="#" className={styles.footerLink}>Social Stats</a>. All rights reserved.
            </footer>
        </div>
    );
}
