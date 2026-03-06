'use client';

import { usePathname } from 'next/navigation';
import Link from 'next/link';
import styles from './Sidebar.module.css';
import {
    HiOutlineBuildingOffice,
    HiOutlineChartBar,
    HiOutlineDocumentChartBar,
    HiOutlineCog6Tooth,
    HiOutlineArrowLeftOnRectangle,
    HiOutlineChevronDoubleLeft,
    HiOutlineChevronDoubleRight,
    HiOutlineSquares2X2,
} from 'react-icons/hi2';

const NAV_ITEMS = [
    { label: 'Companies', href: '/companies', icon: HiOutlineBuildingOffice },
    { label: 'Statistics', href: '/statistics', icon: HiOutlineChartBar },
    { label: 'Reports', href: '/reports', icon: HiOutlineDocumentChartBar },
    { label: 'Monday.com', href: '/monday', icon: HiOutlineSquares2X2 },
    { label: 'Settings', href: '/settings', icon: HiOutlineCog6Tooth },
];

/**
 * Sidebar — Aniq UI-style left navigation.
 * Logo is in the TopBar, sidebar has only nav + bottom actions.
 */
export default function Sidebar({ collapsed, onToggle, onLogout }) {
    const pathname = usePathname();

    return (
        <aside className={`${styles.sidebar} ${collapsed ? styles.collapsed : ''}`}>
            {/* Navigation */}
            <nav className={styles.nav}>
                {!collapsed && <div className={styles.sectionLabel}>MAIN</div>}
                {NAV_ITEMS.map((item) => {
                    const Icon = item.icon;
                    const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={`${styles.navLink} ${isActive ? styles.active : ''}`}
                            title={collapsed ? item.label : undefined}
                        >
                            <span className={styles.navIcon}><Icon /></span>
                            {!collapsed && item.label}
                        </Link>
                    );
                })}
            </nav>

            {/* Bottom: collapse + logout */}
            <div className={styles.bottom}>
                <button className={styles.collapseBtn} onClick={onToggle}>
                    <span className={styles.navIcon}>
                        {collapsed ? <HiOutlineChevronDoubleRight /> : <HiOutlineChevronDoubleLeft />}
                    </span>
                    {!collapsed && 'Collapse'}
                </button>
                <button className={styles.logoutBtn} onClick={onLogout}>
                    <span className={styles.navIcon}><HiOutlineArrowLeftOnRectangle /></span>
                    {!collapsed && 'Logout'}
                </button>
            </div>
        </aside>
    );
}
