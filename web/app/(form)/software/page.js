'use client';

import FilterSearchBar from "@/app/components/FilterSearchBar";
import SingleChoiceChipFilter from "@/app/components/SingleChoiceChipFilter";
import SoftwareLicense from "@/app/model/SoftwareLicense";
import axiosInstance from "@/app/service/axiosConfig";
import { Box, Button, CircularProgress, Link, Stack } from "@mui/material";
import { DataGrid, GridActionsCellItem } from '@mui/x-data-grid';
import { useEffect, useMemo, useState } from "react";
import { usePathname, useSearchParams } from "next/navigation";
import SoftwareLicenseDetailDialog from "./softwareLicenseDetail/SoftwareLicenseDetailDialog";
import SoftwareLicenseDialog from "./softwareLicenseDialog/SoftwareLicenseDialog";

const SOFTWARE_SEARCH_OPTIONS = [
    { value: "software_name", name: "软件名称" },
    { value: "software_info_id", name: "软件ID" },
];
const SOFTWARE_DEFALUT_SEARCH_OPTIONS = SOFTWARE_SEARCH_OPTIONS[0];
const SOFTWARE_CHOICES = [
    { name: '已领用', value: 1, isDefault: true },
    { name: '全部', value: null },
];

export default function Software() {
    const pathname = usePathname();
    const searchParams = useSearchParams();
    const [licenseData, setLicenseData] = useState(null);
    const [status, setStatus] = useState(SOFTWARE_CHOICES.find(c => c.isDefault) ?? null);
    const [searchFilter, setSearchFilter] = useState(SOFTWARE_DEFALUT_SEARCH_OPTIONS.value);
    const [searchKeywords, setSearchKeywords] = useState('');
    const [paginationModel, setPaginationModel] = useState({ page: 0, pageSize: 25 });

    const licenseId = pathname.endsWith('/softwareLicenseDetail')
        ? searchParams.get('id')
        : null;
    const detailId = pathname.endsWith('/softwareLicenseDetail')
        ? licenseId
        : null;

    const [createOpen, setCreateOpen] = useState(false);

    const editId = pathname.endsWith('/softwareLicenseEdit') ? searchParams.get('id') : null;


    useEffect(() => { fetchData(); }, [status, paginationModel.page, paginationModel.pageSize]);

    async function fetchData() {
        let api = status.value === 1 ? '/licenses_with_info/used_license' : '/licenses_with_info';
        let params = { page: paginationModel.page + 1, limit: paginationModel.pageSize };
        let search_value = searchKeywords;
        if (searchFilter && searchKeywords) {
            if (searchFilter === 'software_info_id'){
                const num = parseInt(searchKeywords);
                if (!isNaN(num)){
                    search_value  = num;
                }else{
                    alert('请输入数字');
                    return;
                }
            }
            api += '/search';
            params.search_category = searchFilter;
            params.search_value = search_value;
        }
        try {
            const res = await axiosInstance.get(api, { params });
            setLicenseData(SoftwareLicense.fromArray(res.data));
        } catch (err) {
            console.error(err);
        }
    }
    const openDetail = (id) => {
        setCreateOpen(false); //确保非新建状态
        window.history.pushState(null, '', `${window.location.pathname}/softwareLicenseDetail?id=${id}`);
    };
    const closeDetail = () => {
        window.history.pushState(null, '', '/software');
        fetchData();
    };

    const openEdit = (id) => {
        setCreateOpen(false); //确保非新建状态
        window.history.pushState(null, '', `${window.location.pathname}/softwareLicenseEdit?id=${id}`);
    };
    const closeEdit = () => {
        window.history.pushState(null, '', '/software');
        setCreateOpen(false)
        fetchData();
    };

    const handleOpenCreateDialog = () => {
        setCreateOpen(true);
    };
    
    const closeSoftwareLicenseDialog = () => {
        setCreateOpen(false);
        window.history.pushState(null, '', '/software');
        fetchData(); // 刷新数据
    };

    const columns = useMemo(() => [
        { field: 'licenseID', headerName: '授权ID', flex: 1 },
        { field: 'name', headerName: '软件名称', flex: 2, valueGetter: (_, row) => row.softwareInfo?.softwareInfoName },
        { field: 'licenseStatus', headerName: '授权状态', flex: 1, valueGetter: (_, row) => row.displayLicenseStatus },
        { field: 'licenseExpiredDate', headerName: '过期时间', flex: 2, valueGetter: (_, row) => row.formattedLicenseExpiredDate },
        {
            field: 'action', type: 'actions', headerName: '操作', flex: 1,
            getActions: (params) => [
                <GridActionsCellItem icon={<Link>详情</Link>} label="详情" onClick={() => openDetail(params.row.licenseID)} disableRipple />,
                <GridActionsCellItem icon={<Link>编辑</Link>} label="编辑" onClick={() => openEdit(params.row.licenseID)} disableRipple />
            ]
        }
    ], [status, paginationModel]);

    return (
        <Stack direction="column" spacing={2} sx={{ p: 2 }}>
            <SingleChoiceChipFilter choices={SOFTWARE_CHOICES} selectedChoice={status} onClick={setStatus} />
            <Stack direction="row" spacing={2} alignItems="center">
                <FilterSearchBar
                    options={SOFTWARE_SEARCH_OPTIONS}
                    default={SOFTWARE_DEFALUT_SEARCH_OPTIONS}
                    onFilterChange={e => setSearchFilter(e.target.value)}
                    onSearchChange={e => setSearchKeywords(e.target.value)}
                    onSearch={fetchData}
                    placeholder="搜索软件"
                />
                <Box>
                    <Button variant="contained" disableElevation sx={{ mt: 1 }} onClick={handleOpenCreateDialog}>
                        新建授权
                    </Button>
                </Box>
            </Stack>

            {licenseData === null ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
                    <CircularProgress />
                </Box>
            ) : (
                <DataGrid
                    columns={columns}
                    rows={licenseData}
                    getRowId={row => row.licenseID}
                    rowCount={licenseData.length}
                    paginationMode="server"
                    paginationModel={paginationModel}
                    onPaginationModelChange={setPaginationModel}
                    autoHeight
                />
            )}

            {/* 详情对话框 */}
            {detailId && <SoftwareLicenseDetailDialog open onClose={closeDetail} licenseId={detailId} />}
            {/* 编辑/创建对话框 */}
            <SoftwareLicenseDialog open={createOpen || !!editId} onClose={closeSoftwareLicenseDialog} licenseId={editId} />
        </Stack>
    );
}