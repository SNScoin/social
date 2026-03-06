'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Sidebar from '@/components/layout/Sidebar/Sidebar';
import TopBar from '@/components/layout/TopBar/TopBar';
import api from '@/lib/api';
import styles from './DashboardLayout.module.css';

/**
 * Dashboard layout — wraps authenticated pages with Sidebar + TopBar.
 * Redirects to /login if no token found.
 */
export default function DashboardLayout({ children }) {
    const router = useRouter();
    const [collapsed, setCollapsed] = useState(false);
    const [user, setUser] = useState(null);

    useEffect(() => {
        const token = localStorage.getItem('access_token');
        if (!token) {
            router.replace('/login');
            return;
        }

        // Load sidebar collapsed state
        const saved = localStorage.getItem('sidebar_collapsed');
        if (saved === 'true') setCollapsed(true);

        // Fetch user
        api.get('/auth/me')
            .then((res) => setUser(res.data))
            .catch(() => { });
    }, [router]);

    const toggleSidebar = () => {
        const next = !collapsed;
        setCollapsed(next);
        localStorage.setItem('sidebar_collapsed', String(next));
    };

    const handleLogout = () => {
        localStorage.removeItem('access_token');
        router.push('/login');
    };

    return (
        <div className={styles.layout}>
            <Sidebar collapsed={collapsed} onToggle={toggleSidebar} onLogout={handleLogout} />
            <TopBar user={user} collapsed={collapsed} onToggleSidebar={toggleSidebar} />
            <main className={`${styles.content} ${collapsed ? styles.contentCollapsed : ''}`}>
                {children}
            </main>
        </div>
    );
}
