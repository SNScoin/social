'use client';

import { useState, useEffect, useRef } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import styles from './TopBar.module.css';
import ThemeToggle from '@/components/ui/ThemeToggle/ThemeToggle';
import {
    HiOutlineMagnifyingGlass,
    HiOutlineCog6Tooth,
    HiOutlineBellAlert,
    HiOutlineChevronDown,
    HiOutlineUser,
    HiOutlineArrowLeftOnRectangle,
    HiMiniHome,
    HiBars3,
} from 'react-icons/hi2';

/**
 * TopBar — Aniq UI-style full-width top navigation bar.
 * Logo + hamburger on left, search + actions on right.
 */
export default function TopBar({ user, collapsed, onToggleSidebar }) {
    const pathname = usePathname();
    const router = useRouter();
    const [dropdownOpen, setDropdownOpen] = useState(false);
    const dropdownRef = useRef(null);

    // Derive page title from pathname
    const pageTitle = (() => {
        const seg = pathname.split('/').filter(Boolean);
        if (seg.length === 0) return 'Dashboard';
        return seg[seg.length - 1].replace(/-/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    })();

    // Close dropdown on outside click
    useEffect(() => {
        function handleClick(e) {
            if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
                setDropdownOpen(false);
            }
        }
        document.addEventListener('mousedown', handleClick);
        return () => document.removeEventListener('mousedown', handleClick);
    }, []);

    const getInitials = (name) => {
        if (!name) return '?';
        return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
    };

    const handleLogout = () => {
        localStorage.removeItem('access_token');
        router.push('/login');
    };

    return (
        <header className={styles.topbar}>
            {/* Left: Logo + Hamburger + Breadcrumb */}
            <div className={styles.left}>
                <div className={styles.logoArea}>
                    <button className={styles.hamburger} onClick={onToggleSidebar} title="Toggle sidebar">
                        <HiBars3 />
                    </button>
                    <Image src="/assets/images/login/login.png" alt="Logo" width={26} height={26} className={styles.logoImg} />
                    {!collapsed && <span className={styles.logoText}>Social Stats</span>}
                </div>
                <div className={styles.breadcrumbArea}>
                    <nav className={styles.breadcrumb}>
                        <span className={styles.breadcrumbHome}><HiMiniHome /></span>
                        <span className={styles.breadcrumbSep}>›</span>
                        <span className={styles.breadcrumbCurrent}>{pageTitle}</span>
                    </nav>
                </div>
            </div>

            {/* Right: Search + Lang + Settings + Notifications + User */}
            <div className={styles.right}>
                {/* Search */}
                <button className={styles.searchBtn} title="Search">
                    <HiOutlineMagnifyingGlass className={styles.searchIcon} />
                    <span className={styles.searchLabel}>Search...</span>
                    <kbd className={styles.searchShortcut}>Ctrl+L</kbd>
                </button>

                {/* Language */}
                <button className={styles.langBadge} title="Language">
                    EN ▾
                </button>

                {/* Settings */}
                <button className={styles.iconBtn} title="Settings">
                    <HiOutlineCog6Tooth />
                </button>

                {/* Notifications */}
                <button className={styles.iconBtn} title="Notifications">
                    <HiOutlineBellAlert />
                    <span className={styles.notifBadge}></span>
                </button>

                {/* Theme Toggle */}
                <ThemeToggle />

                {/* User Dropdown */}
                <div className={styles.userDropdown} ref={dropdownRef}>
                    <button
                        className={styles.userTrigger}
                        onClick={() => setDropdownOpen(!dropdownOpen)}
                    >
                        {user?.profile_picture ? (
                            <img src={user.profile_picture} alt="" className={styles.userAvatarImg} />
                        ) : (
                            <div className={styles.userAvatar}>
                                {getInitials(user?.display_name || user?.username)}
                            </div>
                        )}
                        <span className={styles.userName}>
                            {user?.display_name || user?.username || 'User'}
                        </span>
                        <HiOutlineChevronDown className={styles.userChevron} />
                    </button>

                    {dropdownOpen && (
                        <div className={styles.dropdownMenu}>
                            <Link href="/settings" className={styles.dropdownItem} onClick={() => setDropdownOpen(false)}>
                                <span className={styles.dropdownItemIcon}><HiOutlineUser /></span>
                                Profile
                            </Link>
                            <Link href="/settings" className={styles.dropdownItem} onClick={() => setDropdownOpen(false)}>
                                <span className={styles.dropdownItemIcon}><HiOutlineCog6Tooth /></span>
                                Settings
                            </Link>
                            <div className={styles.dropdownDivider}></div>
                            <button className={styles.dropdownLogout} onClick={handleLogout}>
                                <span className={styles.dropdownItemIcon}><HiOutlineArrowLeftOnRectangle /></span>
                                Logout
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </header>
    );
}
