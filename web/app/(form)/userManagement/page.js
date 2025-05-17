'use client';

import FilterSearchBar from "@/app/components/FilterSearchBar";
import SingleChoiceChipFilter from "@/app/components/SingleChoiceChipFilter";
import UserDetailDialog from './userDetail/UserDetailDialog';
import User from "@/app/model/User";
import axiosInstance from "@/app/service/axiosConfig";
import { Box, Button, CircularProgress, Link, Stack } from "@mui/material";
import { DataGrid, GridActionsCellItem } from '@mui/x-data-grid';
import { useEffect, useMemo, useState } from "react";
import { usePathname, useSearchParams } from "next/navigation";

// 搜索选项
const USER_SEARCH_OPTIONS = [
    { value: 'employee_id', name: '工号' },
    { value: 'name', name: '姓名' },
];

const DEFAULT_SEARCH_OPTION = USER_SEARCH_OPTIONS[0];

export default function UserManagement() {
    const pathname = usePathname();
    const searchParams = useSearchParams();

    const [userData, setUserData] = useState(null);
    const [searchFilter, setSearchFilter] = useState(DEFAULT_SEARCH_OPTION.value);
    const [searchKeywords, setSearchKeywords] = useState('');
    const [paginationModel, setPaginationModel] = useState({ page: 0, pageSize: 25 });

    const [createOpen, setCreateOpen] = useState(false);

    // 详情 ID（可选）
    const detailId = pathname.endsWith('/userManagement')
        ? searchParams.get('id')
        : null;

    useEffect(() => {
        fetchData();
    }, []);

    async function fetchData() {
        let api = '/users';
        let params = { page: paginationModel.page + 1, limit: paginationModel.pageSize };
        if (searchFilter && searchKeywords) {
            api = `${api}/search`;
            params = { ...params, search_category: searchFilter, search_value: searchKeywords };
        }
        try {
            const response = await axiosInstance.get(api, { params });
            setUserData(User.fromArray(response.data));
        } catch (err) {
            console.error(err);
        }
    }

    const openDetail = (id) => {
        window.history.pushState(null, '', `${window.location.pathname}/userManagement?id=${id}`);
    };
    const closeDetail = () => {
        window.history.pushState(null, '', '/userManagement');
    };

    const columns = useMemo(() => [
        { field: 'employee_id', headerName: '工号', flex: 1 },
        { field: 'name', headerName: '姓名', flex: 2, valueGetter: (value, row) => row.employee?.name || '--' },
        { field: 'department', headerName: '部门', flex: 2, valueGetter: (value, row) => row.employee?.department || '--' },
        { field: 'status', headerName: '状态', flex: 1, valueGetter: (value, row) => row.status === 1 ? '在职' : '离职' },
        {
            field: 'action', type: 'actions', headerName: '操作', flex: 1,
            getActions: (params) => [
                <GridActionsCellItem
                    icon={<Link>详情</Link>}
                    label="详情"
                    onClick={() => openDetail(params.row.user_id)}
                    disableRipple
                />
            ]
        }
    ], []);

    return (
        <Stack direction="column" spacing={2} sx={{ p: 2 }}>
            {/* 将新建按钮和搜索栏放在同一行 */}
            <Stack direction="row" spacing={2} alignItems="center">
                <FilterSearchBar
                    options={USER_SEARCH_OPTIONS}
                    default={DEFAULT_SEARCH_OPTION}
                    onFilterChange={(e) => setSearchFilter(e.value)}
                    onSearchChange={(e) => setSearchKeywords(e.target.value)}
                    onSearch={fetchData}
                    placeholder="搜索用户"
                />
                <Box>
                    <Button
                        variant="contained"
                        disableElevation
                        sx={{
                            marginTop: "8px",
                        }}
                        onClick={() => setCreateOpen(true)}>
                        新建用户
                    </Button>
                </Box>
            </Stack>

            {userData === null ? (
                <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: 400 }}>
                    <CircularProgress />
                </Box>
            ) : (
                <DataGrid
                    columns={columns}
                    rows={userData}
                    getRowId={(row) => row.user_id}
                    rowCount={userData.length}
                    paginationMode="server"
                    paginationModel={paginationModel}
                    onPaginationModelChange={setPaginationModel}
                    sx={{
                        marginLeft: "32px",
                        marginRight: "32px",
                        marginTop: "8px",
                        marginBottom: "8px",
                    }}
                />
            )}

            {/* 详情对话框 */}
            {detailId && <UserDetailDialog open onClose={closeDetail} userId={detailId} />}
            {/* 新建对话框 */}
            <UserDetailDialog open={createOpen} onClose={() => setCreateOpen(false)} />
        </Stack>
    );
}
