'use client';

import { useState, useEffect, useCallback, Fragment } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { toast } from 'react-toastify';
import api from '@/lib/api';
import { connectSocket, disconnectSocket } from '@/lib/socket';
import { Button, Input, Badge, Spinner } from '@/components/ui';
import styles from './page.module.css';
import {
    HiOutlineArrowLeft,
    HiOutlineArrowPath,
    HiOutlineTrash,
    HiOutlineLink,
    HiOutlineEye,
    HiOutlineHeart,
    HiOutlineChatBubbleLeft,
    HiOutlinePlusCircle,
    HiOutlineInformationCircle,
    HiOutlineExclamationTriangle,
} from 'react-icons/hi2';

const PLATFORMS = [
    { key: 'youtube', label: 'YouTube', color: '#ff0000' },
    { key: 'tiktok', label: 'TikTok', color: '#000' },
    { key: 'instagram', label: 'Instagram', color: '#e4405f' },
    { key: 'facebook', label: 'Facebook', color: '#1877f2' },
];

export default function CompanyStatsPage() {
    const { id } = useParams();
    const router = useRouter();

    const [company, setCompany] = useState(null);
    const [companies, setCompanies] = useState([]);
    const [stats, setStats] = useState({ total_links: 0, total_views: 0, total_likes: 0, total_comments: 0 });
    const [links, setLinks] = useState([]);
    const [loading, setLoading] = useState(true);

    // Add link form state
    const [selectedPlatform, setSelectedPlatform] = useState('');
    const [linkUrl, setLinkUrl] = useState('');
    const [addingLink, setAddingLink] = useState(false);

    // Sync
    const [syncing, setSyncing] = useState(false);
    const [syncProgress, setSyncProgress] = useState(null);

    // Refresh per-link
    const [refreshingLinks, setRefreshingLinks] = useState(new Set());

    // Expandable parent items
    const [expandedItems, setExpandedItems] = useState(new Set());

    // Fetch data
    const fetchData = useCallback(async () => {
        try {
            const [companiesRes, companyRes, statsRes, linksRes] = await Promise.all([
                api.get('/companies'),
                api.get(`/companies/${id}`),
                api.get(`/companies/${id}/stats`),
                api.get(`/links?companyId=${id}`),
            ]);
            setCompanies(companiesRes.data);
            setCompany(companyRes.data);
            setStats(statsRes.data);
            setLinks(linksRes.data);
        } catch (err) {
            toast.error('Failed to load data');
        } finally {
            setLoading(false);
        }
    }, [id]);

    useEffect(() => {
        fetchData();
    }, [fetchData]);

    // Socket.IO for live updates
    useEffect(() => {
        const socket = connectSocket();

        socket.on('metrics:updated', (data) => {
            setLinks(prev => prev.map(link =>
                link.id === data.linkId
                    ? { ...link, metrics: { views: data.views, likes: data.likes, comments: data.comments }, last_error: null }
                    : link
            ));
            api.get(`/companies/${id}/stats`).then(r => setStats(r.data)).catch(() => { });
            api.get(`/links?companyId=${id}`).then(r => setLinks(r.data)).catch(() => { });
            setRefreshingLinks(prev => {
                const next = new Set(prev);
                next.delete(data.linkId);
                return next;
            });
        });

        socket.on('link:error', (data) => {
            setLinks(prev => prev.map(link =>
                link.id === data.linkId
                    ? { ...link, last_error: data.error }
                    : link
            ));
            setRefreshingLinks(prev => {
                const next = new Set(prev);
                next.delete(data.linkId);
                return next;
            });
            toast.error(`Parse failed: ${data.error}`);
        });

        socket.on('sync:progress', (data) => {
            if (String(data.companyId) === String(id)) {
                setSyncProgress(data);
            }
        });

        socket.on('sync:complete', (data) => {
            if (String(data.companyId) === String(id)) {
                setSyncing(false);
                setSyncProgress(null);
                fetchData();
                toast.success(`Sync complete: ${data.linksAdded} added, ${data.linksRemoved} removed`);
            }
        });

        return () => {
            socket.off('metrics:updated');
            socket.off('sync:progress');
            socket.off('sync:complete');
            disconnectSocket();
        };
    }, [id, fetchData]);

    // Add link (manual only)
    const handleAddLink = async (e) => {
        e.preventDefault();
        if (!linkUrl.trim()) return;
        setAddingLink(true);
        try {
            const res = await api.post('/links', {
                url: linkUrl.trim(),
                company_id: id,
                platform: selectedPlatform || undefined,
            });
            setLinks(prev => [res.data, ...prev]);
            setLinkUrl('');
            setSelectedPlatform('');

            // If metrics came back immediately (direct parse), show them
            if (res.data.metrics && (res.data.metrics.views > 0 || res.data.metrics.likes > 0 || res.data.title)) {
                toast.success('Link added with metrics!');
            } else {
                toast.success('Link added — parsing in background...');
                setRefreshingLinks(prev => new Set([...prev, res.data.id]));
            }
            api.get(`/companies/${id}/stats`).then(r => setStats(r.data)).catch(() => { });
        } catch (err) {
            toast.error(err.response?.data?.message || 'Failed to add link');
        } finally {
            setAddingLink(false);
        }
    };

    // Refresh single link
    const handleRefreshLink = async (linkId) => {
        setRefreshingLinks(prev => new Set([...prev, linkId]));
        try {
            const res = await api.post(`/links/${linkId}/refresh`);

            // If metrics came back immediately (direct parse), update the link in place
            if (res.data.metrics) {
                setLinks(prev => prev.map(link =>
                    link.id === linkId
                        ? {
                            ...link,
                            title: res.data.title || link.title,
                            metrics: res.data.metrics,
                        }
                        : link
                ));
                toast.success('Refresh complete!');
                // Re-fetch stats totals + links (to get updated monday_data)
                api.get(`/companies/${id}/stats`).then(r => setStats(r.data)).catch(() => { });
                api.get(`/links?companyId=${id}`).then(r => setLinks(r.data)).catch(() => { });
            } else {
                toast.success('Refresh started');
            }
        } catch (err) {
            toast.error('Failed to refresh');
        } finally {
            setTimeout(() => {
                setRefreshingLinks(prev => {
                    const next = new Set(prev);
                    next.delete(linkId);
                    return next;
                });
            }, 2000);
        }
    };

    // Delete link (manual only)
    const handleDeleteLink = async (linkId) => {
        try {
            await api.delete(`/links/${linkId}`);
            setLinks(prev => prev.filter(l => l.id !== linkId));
            toast.success('Link deleted');
            api.get(`/companies/${id}/stats`).then(r => setStats(r.data)).catch(() => { });
        } catch (err) {
            toast.error('Failed to delete link');
        }
    };

    // Sync from Monday
    const handleSync = async () => {
        setSyncing(true);
        try {
            await api.post(`/companies/${id}/sync`);
            toast.info('Sync started...');
        } catch (err) {
            toast.error('Failed to start sync');
            setSyncing(false);
        }
    };

    const formatNumber = (n) => (n ?? 0).toLocaleString();

    if (loading) return <Spinner label="Loading stats..." />;

    const isMonday = company?.type === 'monday';

    return (
        <div>
            {/* Header */}
            <div className={styles.header}>
                <div className={styles.titleGroup}>
                    <Button variant="ghost" onClick={() => router.push('/companies')} style={{ padding: '8px', color: 'var(--color-text-muted)' }} title="Go back to Companies">
                        <HiOutlineArrowLeft size={18} />
                    </Button>
                    <h1 className={styles.title}>{company?.name || 'Company'}</h1>
                    <Badge variant={isMonday ? 'purple' : 'info'}>
                        {isMonday ? 'Monday.com' : 'Manual'}
                    </Badge>
                </div>
                <div className={styles.switcher}>
                    {isMonday && (
                        <Button onClick={handleSync} loading={syncing}>
                            <HiOutlineArrowPath /> Sync Now
                        </Button>
                    )}
                    <select
                        className={styles.switcherSelect}
                        value={id}
                        onChange={(e) => router.push(`/companies/${e.target.value}/stats`)}
                    >
                        {companies.map(c => (
                            <option key={c.id} value={c.id}>{c.name}</option>
                        ))}
                    </select>
                </div>
            </div>

            {/* Sync Progress */}
            {syncProgress && (
                <div className={styles.syncProgress}>
                    <HiOutlineArrowPath style={{ animation: 'spin 1s linear infinite' }} />
                    <span>Syncing: {syncProgress.processed}/{syncProgress.total}</span>
                    <div className={styles.progressBar}>
                        <div className={styles.progressFill} style={{ width: `${(syncProgress.processed / syncProgress.total) * 100}%` }} />
                    </div>
                </div>
            )}

            {/* Stats Cards */}
            <div className={styles.statsGrid}>
                <div className={styles.statCard}>
                    <div className={styles.statIcon}><HiOutlineLink /></div>
                    <div className={styles.statValue}>{formatNumber(stats.total_links)}</div>
                    <div className={styles.statLabel}>Total Links</div>
                </div>
                <div className={styles.statCard}>
                    <div className={styles.statIcon}><HiOutlineEye /></div>
                    <div className={styles.statValue}>{formatNumber(stats.total_views)}</div>
                    <div className={styles.statLabel}>Total Views</div>
                </div>
                <div className={styles.statCard}>
                    <div className={styles.statIcon}><HiOutlineHeart /></div>
                    <div className={styles.statValue}>{formatNumber(stats.total_likes)}</div>
                    <div className={styles.statLabel}>Total Likes</div>
                </div>
                <div className={styles.statCard}>
                    <div className={styles.statIcon}><HiOutlineChatBubbleLeft /></div>
                    <div className={styles.statValue}>{formatNumber(stats.total_comments)}</div>
                    <div className={styles.statLabel}>Total Comments</div>
                </div>
            </div>

            {/* Add Link / Info Banner */}
            {isMonday ? (
                <div className={styles.infoBanner}>
                    <HiOutlineInformationCircle style={{ fontSize: '1.2rem', flexShrink: 0 }} />
                    Links are imported from your Monday.com board. Click &quot;Sync Now&quot; to re-import.
                </div>
            ) : (
                <div className={styles.panelCard}>
                    <div className={styles.panelHeader}>
                        <span className={styles.panelTitle}>
                            <HiOutlinePlusCircle /> Add New Link
                        </span>
                    </div>
                    <div className={styles.panelBody}>
                        <div className={styles.platformSelector}>
                            {PLATFORMS.map(p => (
                                <button
                                    key={p.key}
                                    className={`${styles.platformBtn} ${selectedPlatform === p.key ? styles.platformBtnActive : ''}`}
                                    onClick={() => setSelectedPlatform(selectedPlatform === p.key ? '' : p.key)}
                                    type="button"
                                >
                                    {p.label}
                                </button>
                            ))}
                        </div>
                        <form onSubmit={handleAddLink} className={styles.addLinkForm}>
                            <Input
                                placeholder="Paste a social media link..."
                                value={linkUrl}
                                onChange={(e) => setLinkUrl(e.target.value)}
                                disabled={addingLink}
                            />
                            <Button type="submit" loading={addingLink} disabled={!linkUrl.trim()}>
                                Add Link
                            </Button>
                        </form>
                    </div>
                </div>
            )}

            {/* Links Table */}
            <div className={styles.panelCard}>
                <div className={styles.panelHeader}>
                    <span className={styles.panelTitle}>
                        <HiOutlineLink /> Links
                    </span>
                    <span className={styles.panelCount}>{links.length} total</span>
                </div>
                {links.length === 0 ? (
                    <div className={styles.emptyState}>
                        <div className={styles.emptyIcon}><HiOutlineLink /></div>
                        <div className={styles.emptyText}>No links yet</div>
                        <div className={styles.emptyHint}>
                            {isMonday ? 'Click "Sync Now" to import from Monday.com' : 'Add one above to start tracking metrics'}
                        </div>
                    </div>
                ) : isMonday && company?.board_columns?.length > 0 ? (
                    /* ── Dynamic Monday.com Table with Hierarchy ── */
                    (() => {
                        const HIDDEN_TYPES = ['subtasks', 'button', 'file'];
                        const displayCols = company.board_columns.filter(col =>
                            col.id !== 'name' && !HIDDEN_TYPES.includes(col.type)
                        );
                        const isNumCol = (col) => col.type === 'numbers' || col.type === 'numeric';

                        // Separate parent items and sub-items
                        const parentItems = links.filter(l => !l.is_subitem);
                        const subItemMap = {};
                        for (const link of links) {
                            if (link.is_subitem && link.parent_monday_item_id) {
                                if (!subItemMap[link.parent_monday_item_id]) {
                                    subItemMap[link.parent_monday_item_id] = [];
                                }
                                subItemMap[link.parent_monday_item_id].push(link);
                            }
                        }

                        const toggleExpand = (mondayItemId) => {
                            setExpandedItems(prev => {
                                const next = new Set(prev);
                                if (next.has(mondayItemId)) {
                                    next.delete(mondayItemId);
                                } else {
                                    next.add(mondayItemId);
                                }
                                return next;
                            });
                        };

                        const renderCell = (col, val) => {
                            if (col.type === 'status' || col.type === 'color') {
                                return val ? (
                                    <span className={`${styles.platformBadge} ${styles[val.toLowerCase()] || ''}`}>{val}</span>
                                ) : '—';
                            }
                            if (col.type === 'link') {
                                return val ? (
                                    <a href={val} target="_blank" rel="noopener" className={styles.linkUrl}>
                                        {val.replace(/^https?:\/\/(www\.)?/, '').slice(0, 30)}
                                    </a>
                                ) : '—';
                            }
                            if (isNumCol(col)) {
                                return <span className={styles.metric}>{val ? formatNumber(Number(val)) : '0'}</span>;
                            }
                            if (col.type === 'date') {
                                return val || '—';
                            }
                            return val || '—';
                        };

                        return (
                            <table className={styles.linksTable}>
                                <thead>
                                    <tr>
                                        <th>Item</th>
                                        {displayCols.map(col => (
                                            <th key={col.id} className={isNumCol(col) ? styles.metricHeader : undefined}>
                                                {col.title}
                                            </th>
                                        ))}
                                        <th style={{ width: '80px' }}></th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {parentItems.map(link => {
                                        const mondayData = link.monday_data || {};
                                        const subs = subItemMap[link.monday_item_id] || [];
                                        const isExpanded = expandedItems.has(link.monday_item_id);
                                        const hasChildren = subs.length > 0;

                                        return (
                                            <Fragment key={link.id}>
                                                {/* Parent row */}
                                                <tr className={`${styles.parentRow} ${isExpanded ? styles.parentExpanded : ''}`}>
                                                    <td>
                                                        <div className={styles.parentItemCell} onClick={hasChildren ? () => toggleExpand(link.monday_item_id) : undefined} style={{ cursor: hasChildren ? 'pointer' : 'default' }}>
                                                            {hasChildren && (
                                                                <span className={`${styles.expandChevron} ${isExpanded ? styles.chevronOpen : ''}`}>▸</span>
                                                            )}
                                                            <span className={styles.itemName}>
                                                                {link.title || `Item #${link.id}`}
                                                            </span>
                                                            {link.last_error && (
                                                                <span style={{ color: 'var(--color-danger)', fontSize: '0.8rem', marginLeft: '6px', display: 'inline-flex', alignItems: 'center', gap: '2px', verticalAlign: 'middle' }} title={link.last_error}>
                                                                    <HiOutlineExclamationTriangle /> Restricted
                                                                </span>
                                                            )}
                                                            {hasChildren && (
                                                                <span className={styles.subItemCount}>{subs.length}</span>
                                                            )}
                                                        </div>
                                                    </td>
                                                    {displayCols.map(col => (
                                                        <td key={col.id} className={isNumCol(col) ? styles.metricCell : undefined}>
                                                            {renderCell(col, mondayData[col.id] || '')}
                                                        </td>
                                                    ))}
                                                    <td>
                                                        <div className={styles.actions}>
                                                            <Button variant="ghost" size="sm" onClick={() => handleRefreshLink(link.id)} loading={refreshingLinks.has(link.id)}>
                                                                <HiOutlineArrowPath />
                                                            </Button>
                                                        </div>
                                                    </td>
                                                </tr>

                                                {/* Sub-items (expanded) */}
                                                {isExpanded && subs.length > 0 && (
                                                    <tr className={styles.subItemsRow}>
                                                        <td colSpan={displayCols.length + 2} style={{ padding: 0 }}>
                                                            <div className={styles.subItemsContainer}>
                                                                <table className={styles.subItemsTable}>
                                                                    <thead>
                                                                        <tr>
                                                                            <th>Subitem</th>
                                                                            {displayCols.filter(c => c.type !== 'status').map(col => (
                                                                                <th key={col.id} className={isNumCol(col) ? styles.metricHeader : undefined}>
                                                                                    {col.title === 'Link' ? 'Link' : col.title}
                                                                                </th>
                                                                            ))}
                                                                            <th style={{ width: '60px' }}></th>
                                                                        </tr>
                                                                    </thead>
                                                                    <tbody>
                                                                        {subs.map(sub => {
                                                                            const subData = sub.monday_data || {};
                                                                            return (
                                                                                <tr key={sub.id}>
                                                                                    <td>
                                                                                        <span className={styles.subItemName}>{sub.title || `Subitem #${sub.id}`}</span>
                                                                                        {sub.last_error && (
                                                                                            <span style={{ color: 'var(--color-danger)', fontSize: '0.8rem', marginLeft: '6px', display: 'inline-flex', alignItems: 'center', gap: '2px', verticalAlign: 'middle' }} title={sub.last_error}>
                                                                                                <HiOutlineExclamationTriangle />
                                                                                            </span>
                                                                                        )}
                                                                                    </td>
                                                                                    {displayCols.filter(c => c.type !== 'status').map(col => (
                                                                                        <td key={col.id} className={isNumCol(col) ? styles.metricCell : undefined}>
                                                                                            {renderCell(col, subData[col.id] || '')}
                                                                                        </td>
                                                                                    ))}
                                                                                    <td>
                                                                                        <div className={styles.actions}>
                                                                                            <Button variant="ghost" size="sm" onClick={() => handleRefreshLink(sub.id)} loading={refreshingLinks.has(sub.id)}>
                                                                                                <HiOutlineArrowPath />
                                                                                            </Button>
                                                                                        </div>
                                                                                    </td>
                                                                                </tr>
                                                                            );
                                                                        })}
                                                                    </tbody>
                                                                </table>
                                                            </div>
                                                        </td>
                                                    </tr>
                                                )}
                                            </Fragment>
                                        );
                                    })}
                                </tbody>
                            </table>
                        );
                    })()
                ) : (
                    /* ── Static Table for Manual Companies ── */
                    <table className={styles.linksTable}>
                        <thead>
                            <tr>
                                <th>Item</th>
                                <th>Platform</th>
                                <th>Link</th>
                                <th className={styles.metricHeader}>Views</th>
                                <th className={styles.metricHeader}>Likes</th>
                                <th className={styles.metricHeader}>Comments</th>
                                <th style={{ width: '80px' }}></th>
                            </tr>
                        </thead>
                        <tbody>
                            {links.map(link => {
                                const p = PLATFORMS.find(p => p.key === link.platform);
                                const shortUrl = link.url.replace(/^https?:\/\/(www\.)?/, '').slice(0, 35);
                                return (
                                    <tr key={link.id}>
                                        <td>
                                            <span className={styles.itemName}>
                                                {link.title || (refreshingLinks.has(link.id) ? 'Parsing link...' : `Item #${link.id}`)}
                                            </span>
                                            {link.last_error && (
                                                <span style={{ color: 'var(--color-danger)', fontSize: '0.8rem', marginLeft: '6px', display: 'inline-flex', alignItems: 'center', gap: '2px', verticalAlign: 'middle' }} title={link.last_error}>
                                                    <HiOutlineExclamationTriangle /> Restricted
                                                </span>
                                            )}
                                        </td>
                                        <td>
                                            <span className={`${styles.platformBadge} ${styles[link.platform] || ''}`}>
                                                {p?.label || link.platform}
                                            </span>
                                        </td>
                                        <td>
                                            <a href={link.url} target="_blank" rel="noopener" className={styles.linkUrl}>
                                                {shortUrl}
                                            </a>
                                        </td>
                                        <td className={styles.metricCell}>
                                            <span className={styles.metric}>
                                                {refreshingLinks.has(link.id) && !link.title && link.metrics?.views === 0 ? '...' : formatNumber(link.metrics?.views)}
                                            </span>
                                        </td>
                                        <td className={styles.metricCell}>
                                            <span className={styles.metric}>
                                                {refreshingLinks.has(link.id) && !link.title && link.metrics?.likes === 0 ? '...' : formatNumber(link.metrics?.likes)}
                                            </span>
                                        </td>
                                        <td className={styles.metricCell}>
                                            <span className={styles.metric}>
                                                {refreshingLinks.has(link.id) && !link.title && link.metrics?.comments === 0 ? '...' : formatNumber(link.metrics?.comments)}
                                            </span>
                                        </td>
                                        <td>
                                            <div className={styles.actions}>
                                                <Button variant="ghost" size="sm" onClick={() => handleRefreshLink(link.id)} loading={refreshingLinks.has(link.id)}>
                                                    <HiOutlineArrowPath />
                                                </Button>
                                                <Button variant="ghost" size="sm" onClick={() => handleDeleteLink(link.id)}>
                                                    <HiOutlineTrash />
                                                </Button>
                                            </div>
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                )}
            </div>
        </div>
    );
}
