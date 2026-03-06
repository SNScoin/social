'use client';

import { useState, useEffect, useRef, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { useRouter } from 'next/navigation';
import { toast } from 'react-toastify';
import api from '@/lib/api';
import { Button, Input, Badge } from '@/components/ui';
import styles from './page.module.css';
import {
    HiOutlineTrash,
    HiOutlineEye,
    HiOutlineBuildingOffice2,
    HiOutlinePencilSquare,
    HiOutlineClipboardDocumentList,
    HiOutlinePlusCircle,
    HiOutlineMagnifyingGlass,
    HiOutlineFunnel,
    HiOutlineArrowPath,
    HiOutlineEllipsisVertical,
} from 'react-icons/hi2';

export default function CompaniesPage() {
    const router = useRouter();
    const [companies, setCompanies] = useState([]);
    const [loading, setLoading] = useState(true);

    // Filters
    const [search, setSearch] = useState('');
    const [statusFilter, setStatusFilter] = useState('');
    const [typeFilter, setTypeFilter] = useState('');

    // Mode: null, 'create', 'manual', 'monday'
    const [mode, setMode] = useState(null);

    // Manual state
    const [companyName, setCompanyName] = useState('');
    const [creating, setCreating] = useState(false);

    // Monday wizard state
    const [wizardStep, setWizardStep] = useState(1);
    const [mondayToken, setMondayToken] = useState('');
    const [workspaces, setWorkspaces] = useState([]);
    const [selectedWorkspace, setSelectedWorkspace] = useState('');
    const [boards, setBoards] = useState([]);
    const [selectedBoard, setSelectedBoard] = useState('');
    const [selectedBoardName, setSelectedBoardName] = useState('');
    const [columns, setColumns] = useState([]);
    const [sourceColumn, setSourceColumn] = useState('');
    const [viewsColumn, setViewsColumn] = useState('');
    const [likesColumn, setLikesColumn] = useState('');
    const [commentsColumn, setCommentsColumn] = useState('');
    const [wizardLoading, setWizardLoading] = useState(false);

    // Dropdown menu
    const [openMenu, setOpenMenu] = useState(null);
    const [menuPos, setMenuPos] = useState({ top: 0, left: 0 });
    const menuRef = useRef(null);

    useEffect(() => {
        fetchCompanies();
    }, []);

    // Close dropdown on outside click
    useEffect(() => {
        const handleClick = (e) => {
            if (menuRef.current && !menuRef.current.contains(e.target)) {
                setOpenMenu(null);
            }
        };
        const handleScroll = () => setOpenMenu(null);
        document.addEventListener('mousedown', handleClick);
        window.addEventListener('scroll', handleScroll, true);
        return () => {
            document.removeEventListener('mousedown', handleClick);
            window.removeEventListener('scroll', handleScroll, true);
        };
    }, []);

    const fetchCompanies = async () => {
        try {
            const res = await api.get('/companies');
            setCompanies(res.data);
        } catch (err) {
            toast.error('Failed to load companies');
        } finally {
            setLoading(false);
        }
    };

    // Manual create
    const handleManualCreate = async (e) => {
        e.preventDefault();
        if (!companyName.trim()) return;
        setCreating(true);
        try {
            const res = await api.post('/companies', { name: companyName.trim() });
            toast.success('Company created!');
            setCompanyName('');
            setMode(null);
            router.push(`/companies/${res.data.id}/stats`);
        } catch (err) {
            toast.error(err.response?.data?.message || 'Failed to create company');
        } finally {
            setCreating(false);
        }
    };

    // Monday wizard handlers
    const handleTokenSubmit = async () => {
        if (!mondayToken.trim()) return;
        setWizardLoading(true);
        try {
            const res = await api.post('/monday/workspaces', { api_token: mondayToken });
            setWorkspaces(res.data.workspaces || []);
            setWizardStep(2);
        } catch (err) {
            toast.error('Invalid API token or Monday.com error');
        } finally {
            setWizardLoading(false);
        }
    };

    const handleWorkspaceSelect = async (wsId) => {
        setSelectedWorkspace(wsId);
        setWizardLoading(true);
        try {
            const res = await api.post('/monday/boards', { api_token: mondayToken, workspace_id: wsId });
            setBoards(res.data.boards || []);
            setWizardStep(3);
        } catch (err) {
            toast.error('Failed to fetch boards');
        } finally {
            setWizardLoading(false);
        }
    };

    const handleBoardSelect = async (boardId) => {
        setSelectedBoard(boardId);
        const board = boards.find(b => String(b.id) === String(boardId));
        setSelectedBoardName(board?.name || '');
        setWizardLoading(true);
        try {
            const res = await api.post('/monday/columns', { api_token: mondayToken, board_id: boardId });
            const cols = res.data.columns || [];
            setColumns(cols);

            // Auto-map columns by title (case-insensitive match)
            const findCol = (keywords) => {
                const col = cols.find(c => keywords.some(kw => c.title.toLowerCase() === kw));
                return col?.id || '';
            };
            setSourceColumn(findCol(['link', 'url', 'source', 'link url']));
            setViewsColumn(findCol(['views', 'view', 'צפיות']));
            setLikesColumn(findCol(['likes', 'like', 'לייקים']));
            setCommentsColumn(findCol(['comments', 'comment', 'תגובות']));

            setWizardStep(4);
        } catch (err) {
            toast.error('Failed to fetch columns');
        } finally {
            setWizardLoading(false);
        }
    };

    const handleMondayCreate = async () => {
        if (!sourceColumn || !viewsColumn || !likesColumn || !commentsColumn) {
            toast.error('Please select all column mappings');
            return;
        }
        setCreating(true);
        try {
            const ws = workspaces.find(w => String(w.id) === String(selectedWorkspace));
            const res = await api.post('/companies/from-monday', {
                api_token: mondayToken,
                workspace_id: selectedWorkspace,
                workspace_name: ws?.name || '',
                board_id: selectedBoard,
                board_name: selectedBoardName,
                source_column_id: sourceColumn,
                views_column_id: viewsColumn,
                likes_column_id: likesColumn,
                comments_column_id: commentsColumn,
            });
            toast.success('Monday.com company created! Syncing links...');
            resetWizard();
            router.push(`/companies/${res.data.id}/stats`);
        } catch (err) {
            toast.error(err.response?.data?.message || 'Failed to create Monday company');
        } finally {
            setCreating(false);
        }
    };

    const resetWizard = () => {
        setMode(null);
        setWizardStep(1);
        setMondayToken('');
        setWorkspaces([]);
        setSelectedWorkspace('');
        setBoards([]);
        setSelectedBoard('');
        setSelectedBoardName('');
        setColumns([]);
        setSourceColumn('');
        setViewsColumn('');
        setLikesColumn('');
        setCommentsColumn('');
    };

    // Delete
    const handleDelete = async (id) => {
        if (!confirm('Delete this company and all its links?')) return;
        setOpenMenu(null);
        try {
            await api.delete(`/companies/${id}`);
            setCompanies(prev => prev.filter(c => c.id !== id));
            toast.success('Company deleted');
        } catch (err) {
            toast.error('Failed to delete company');
        }
    };

    // Filter companies
    const filtered = companies.filter(c => {
        if (search && !c.name.toLowerCase().includes(search.toLowerCase())) return false;
        if (typeFilter && c.type !== typeFilter) return false;
        return true;
    });

    const resetFilters = () => {
        setSearch('');
        setStatusFilter('');
        setTypeFilter('');
    };

    // ── Render ──
    // If in create mode, show create UI
    if (mode === 'create' || mode === 'manual' || mode === 'monday') {
        return (
            <div className={styles.page}>
                {/* Mode Selector */}
                {mode === 'create' && (
                    <div className={styles.panelCard}>
                        <div className={styles.panelHeader}>
                            <span className={styles.panelTitle}>Create New Company</span>
                            <button className={styles.backBtn} onClick={() => setMode(null)}>← Back</button>
                        </div>
                        <div className={styles.panelBody}>
                            <div className={styles.modeSelector}>
                                <div className={styles.modeCard} onClick={() => setMode('manual')}>
                                    <div className={styles.modeIcon}><HiOutlinePencilSquare /></div>
                                    <div className={styles.modeTitle}>Manual Company</div>
                                    <div className={styles.modeDesc}>Create a company, then add social links yourself</div>
                                </div>
                                <div className={styles.modeCard} onClick={() => setMode('monday')}>
                                    <div className={styles.modeIcon}><HiOutlineClipboardDocumentList /></div>
                                    <div className={styles.modeTitle}>From Monday.com</div>
                                    <div className={styles.modeDesc}>Import links from a Monday.com board and sync metrics automatically</div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Manual Create Form */}
                {mode === 'manual' && (
                    <div className={styles.panelCard}>
                        <div className={styles.panelHeader}>
                            <span className={styles.panelTitle}><HiOutlinePencilSquare /> Create Manual Company</span>
                            <button className={styles.backBtn} onClick={() => setMode('create')}>← Back</button>
                        </div>
                        <div className={styles.panelBody}>
                            <form onSubmit={handleManualCreate} className={styles.createForm}>
                                <Input
                                    label="Company Name"
                                    placeholder="Enter company name"
                                    value={companyName}
                                    onChange={(e) => setCompanyName(e.target.value)}
                                    disabled={creating}
                                />
                                <Button type="submit" loading={creating} disabled={!companyName.trim()}>
                                    Create Company
                                </Button>
                            </form>
                        </div>
                    </div>
                )}

                {/* Monday Wizard */}
                {mode === 'monday' && (
                    <div className={styles.panelCard}>
                        <div className={styles.panelHeader}>
                            <span className={styles.panelTitle}><HiOutlineClipboardDocumentList /> Create from Monday.com</span>
                            <button className={styles.backBtn} onClick={() => setMode('create')}>← Back</button>
                        </div>
                        <div className={styles.panelBody}>
                            <div className={styles.wizardSteps}>
                                {/* Step 1: API Token */}
                                <div className={`${styles.wizardStep} ${wizardStep > 1 ? styles.wizardStepCompleted : ''}`}>
                                    <div className={styles.wizardStepLabel}>Step 1 — API Token</div>
                                    {wizardStep === 1 ? (
                                        <>
                                            <Input type="password" placeholder="Paste your Monday.com API token" value={mondayToken} onChange={(e) => setMondayToken(e.target.value)} disabled={wizardLoading} />
                                            <div className={styles.wizardActions}>
                                                <Button onClick={handleTokenSubmit} loading={wizardLoading} disabled={!mondayToken.trim()}>Connect</Button>
                                            </div>
                                        </>
                                    ) : (
                                        <Badge variant="success">Connected</Badge>
                                    )}
                                </div>

                                {/* Step 2: Workspace */}
                                {wizardStep >= 2 && (
                                    <div className={`${styles.wizardStep} ${wizardStep > 2 ? styles.wizardStepCompleted : ''}`}>
                                        <div className={styles.wizardStepLabel}>Step 2 — Select Workspace</div>
                                        {wizardStep === 2 ? (
                                            <Input type="select" value={selectedWorkspace} onChange={(e) => handleWorkspaceSelect(e.target.value)} disabled={wizardLoading}>
                                                <option value="">Select a workspace...</option>
                                                {workspaces.map(ws => <option key={ws.id} value={ws.id}>{ws.name}</option>)}
                                            </Input>
                                        ) : (
                                            <Badge variant="success">{workspaces.find(w => String(w.id) === String(selectedWorkspace))?.name}</Badge>
                                        )}
                                    </div>
                                )}

                                {/* Step 3: Board */}
                                {wizardStep >= 3 && (
                                    <div className={`${styles.wizardStep} ${wizardStep > 3 ? styles.wizardStepCompleted : ''}`}>
                                        <div className={styles.wizardStepLabel}>Step 3 — Select Board</div>
                                        {wizardStep === 3 ? (
                                            <Input type="select" value={selectedBoard} onChange={(e) => handleBoardSelect(e.target.value)} disabled={wizardLoading}>
                                                <option value="">Select a board...</option>
                                                {boards.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
                                            </Input>
                                        ) : (
                                            <Badge variant="success">{selectedBoardName}</Badge>
                                        )}
                                    </div>
                                )}

                                {/* Step 4: Column Mappings */}
                                {wizardStep >= 4 && (
                                    <div className={styles.wizardStep}>
                                        <div className={styles.wizardStepLabel}>Step 4 — Map Columns</div>
                                        <div style={{ marginBottom: 'var(--space-4)' }}>
                                            <Input type="select" label="Source Column (social media links)" value={sourceColumn} onChange={(e) => setSourceColumn(e.target.value)}>
                                                <option value="">Select column...</option>
                                                {columns.map(c => <option key={c.id} value={c.id}>{c.title} ({c.type})</option>)}
                                            </Input>
                                        </div>
                                        <div className={styles.columnGrid}>
                                            <Input type="select" label="Views → Column" value={viewsColumn} onChange={(e) => setViewsColumn(e.target.value)}>
                                                <option value="">Select...</option>
                                                {columns.map(c => <option key={c.id} value={c.id}>{c.title}</option>)}
                                            </Input>
                                            <Input type="select" label="Likes → Column" value={likesColumn} onChange={(e) => setLikesColumn(e.target.value)}>
                                                <option value="">Select...</option>
                                                {columns.map(c => <option key={c.id} value={c.id}>{c.title}</option>)}
                                            </Input>
                                            <Input type="select" label="Comments → Column" value={commentsColumn} onChange={(e) => setCommentsColumn(e.target.value)}>
                                                <option value="">Select...</option>
                                                {columns.map(c => <option key={c.id} value={c.id}>{c.title}</option>)}
                                            </Input>
                                        </div>
                                        <div className={styles.wizardActions}>
                                            <Button onClick={handleMondayCreate} loading={creating} disabled={!sourceColumn || !viewsColumn || !likesColumn || !commentsColumn}>
                                                Create & Sync
                                            </Button>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        );
    }

    // ── Default: List View ──
    return (
        <div className={styles.page}>
            {/* Filter Bar */}
            <div className={styles.filterBar}>
                <input
                    className={styles.filterInput}
                    placeholder="Search companies..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                />
                <select className={styles.filterSelect} value={typeFilter} onChange={(e) => setTypeFilter(e.target.value)}>
                    <option value="">All types</option>
                    <option value="manual">Manual</option>
                    <option value="monday">Monday.com</option>
                </select>
                <div className={styles.filterActions}>
                    <button className={`${styles.filterBtn} ${styles.filterBtnGhost}`} onClick={resetFilters}>
                        <HiOutlineArrowPath /> Reset
                    </button>
                    <button className={`${styles.filterBtn} ${styles.createBtn}`} onClick={() => setMode('create')}>
                        <HiOutlinePlusCircle /> New Company
                    </button>
                </div>
            </div>

            {/* Table */}
            <div className={styles.tablePanel}>
                {loading ? (
                    <div className={styles.emptyState}>
                        <div className={styles.emptyText}>Loading...</div>
                    </div>
                ) : filtered.length === 0 ? (
                    <div className={styles.emptyState}>
                        <div className={styles.emptyIcon}><HiOutlineBuildingOffice2 /></div>
                        <div className={styles.emptyText}>
                            {companies.length === 0 ? 'No companies yet' : 'No companies match your filters'}
                        </div>
                        <div className={styles.emptyHint}>
                            {companies.length === 0 ? 'Create your first company to start tracking social metrics' : 'Try adjusting your search or filters'}
                        </div>
                        {companies.length === 0 && (
                            <button className={styles.createBtn} onClick={() => setMode('create')}>
                                <HiOutlinePlusCircle /> Create Company
                            </button>
                        )}
                    </div>
                ) : (
                    <table className={styles.table}>
                        <thead>
                            <tr>
                                <th>Name</th>
                                <th>Type</th>
                                <th>Created</th>
                                <th style={{ textAlign: 'right' }}>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filtered.map(company => (
                                <tr key={company.id}>
                                    <td>
                                        <div className={styles.nameCell}>
                                            <div className={styles.companyAvatar}>
                                                <HiOutlineBuildingOffice2 />
                                            </div>
                                            <div className={styles.companyInfo}>
                                                <div className={styles.companyName} onClick={() => router.push(`/companies/${company.id}/stats`)}>
                                                    {company.name}
                                                </div>
                                                <div className={styles.companyDesc}>
                                                    {company.type === 'monday' ? 'Synced from Monday.com board' : 'Manually managed company'}
                                                    {company.description ? ` — ${company.description}` : ''}
                                                </div>
                                            </div>
                                        </div>
                                    </td>
                                    <td>
                                        <Badge variant={company.type === 'monday' ? 'purple' : 'success'}>
                                            {company.type === 'monday' ? 'Monday.com' : 'Manual'}
                                        </Badge>
                                    </td>
                                    <td style={{ color: 'var(--color-text-muted)', fontSize: 'var(--text-sm)' }}>
                                        {new Date(company.created_at).toLocaleDateString()}
                                    </td>
                                    <td>
                                        <div className={styles.actionsCell}>
                                            <button className={styles.viewBtn} onClick={() => router.push(`/companies/${company.id}/stats`)}>
                                                <HiOutlineEye /> View
                                            </button>
                                            <div>
                                                <button className={styles.menuBtn} onClick={(e) => {
                                                    if (openMenu === company.id) {
                                                        setOpenMenu(null);
                                                    } else {
                                                        const rect = e.currentTarget.getBoundingClientRect();
                                                        setMenuPos({ top: rect.bottom + 4, left: rect.right - 160 });
                                                        setOpenMenu(company.id);
                                                    }
                                                }}>
                                                    <HiOutlineEllipsisVertical />
                                                </button>
                                            </div>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                )}
            </div>
            {/* Portal Dropdown */}
            {openMenu && typeof document !== 'undefined' && createPortal(
                <div ref={menuRef} className={styles.dropdown} style={{ position: 'fixed', top: menuPos.top, left: menuPos.left }}>
                    <button className={styles.dropdownItem} onClick={() => { router.push(`/companies/${openMenu}/stats`); setOpenMenu(null); }}>
                        <HiOutlineEye /> View Stats
                    </button>
                    <button className={`${styles.dropdownItem} ${styles.dropdownItemDanger}`} onClick={() => handleDelete(openMenu)}>
                        <HiOutlineTrash /> Delete
                    </button>
                </div>,
                document.body
            )}
        </div>
    );
}
