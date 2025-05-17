'use client';

import FilterSearchBar from "@/app/components/FilterSearchBar";
import SingleChoiceChipFilter from "@/app/components/SingleChoiceChipFilter";
import SoftwareLicense from "@/app/model/SoftwareLicense";
import axiosInstance from "@/app/service/axiosConfig";
import { Box, CircularProgress, Link, Stack } from "@mui/material";
import { DataGrid, GridActionsCellItem } from '@mui/x-data-grid';
import { useEffect, useMemo, useState } from "react";
import SoftwareLicenseDetailDialog from "./softwareLicenseDetail/SoftwareLicenseDetailDialog";
import { usePathname, useSearchParams } from "next/navigation";


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
    const [status, setStatus] = useState(SOFTWARE_CHOICES.find((choice) => choice.isDefault) ?? null);
    const [searchFilter, setSearchFilter] = useState(SOFTWARE_DEFALUT_SEARCH_OPTIONS.value);
    const [searchKeywords, setSearchKeywords] = useState('');
    const [paginationModel, setPaginationModel] = useState({
        page: 0,
        pageSize: 25,
    });
    const licenseId = pathname.endsWith('/softwareLicenseDetail')
        ? searchParams.get('id')
        : null;

    useEffect(() => {
        fetchData();
    }, [status]);

    async function fetchData() {
        let api = status.value === 1 ? '/licenses_with_info/used_license' : '/licenses_with_info/';
        let params = {
            page: paginationModel.page + 1,
            limit: paginationModel.pageSize,
        };
        if (status?.value) {
            params = {
                ...params,
            }
        }
        if (searchFilter && searchKeywords && searchKeywords.length > 0) {
            api = `${api}/search`;
            params = {
                ...params,
                search_category: searchFilter,
                search_value: searchKeywords,
            }
        }
        try {
            const response = await axiosInstance.get(api, {
                params: params,
            });
            const data = response.data;
            setLicenseData(SoftwareLicense.fromArray(data));
        } catch (error) {
        }
    }

    // 点击「详情」时调用，给当前 URL 加上 ?softwareLicenseDetail=xxx
    const openDetail = (id) => {
        window.history.pushState(
            null,
            '',
            `${window.location.pathname}/softwareLicenseDetail?id=${id}`
        );
    };

    const closeDetail = () => {
        window.history.pushState(null, '', '/software');
    };

    const columns = useMemo(() => [
        {
            field: 'licenseID',
            headerName: '授权ID',
            flex: 1,
        },
        {
            field: 'name',
            headerName: '软件名称',
            flex: 2,
            valueGetter: (value, row) => row.softwareInfo?.softwareInfoName
        },
        {
            field: 'licenseStatus',
            headerName: '授权状态',
            valueGetter: (value, row) => row.displayLicenseStatus,
            flex: 1,
        },
        {
            field: 'licenseExpiredDate',
            headerName: '过期时间',
            valueGetter: (value, row) => row.formattedLicenseExpiwredDate,
            flex: 2,
        },
        {
            field: 'action',
            type: 'actions',
            headerName: '操作',
            flex: 1,
            getActions: (params) => [
                <GridActionsCellItem
                    icon={<Link>详情</Link>}
                    label="详情"
                    onClick={() => openDetail(params.row.licenseID)}
                    showInMenu={false}
                    disableRipple
                />
            ],
        },
    ]);


    return (
        <Stack direction="column" >
            <SingleChoiceChipFilter
                choices={SOFTWARE_CHOICES}
                onClick={(choice) => setStatus(choice)}
                selectedChoice={status} />
            <FilterSearchBar
                options={SOFTWARE_SEARCH_OPTIONS}
                default={SOFTWARE_DEFALUT_SEARCH_OPTIONS}
                onFilterChange={(event) => { setSearchFilter(event.value) }}
                onSearchChange={(event) => { setSearchKeywords(event.target.value) }}
                onSearch={fetchData}
                placeholder="搜索软件" />
            {licenseData !== null ?
                <DataGrid
                    columns={columns}
                    paginationModel={paginationModel}
                    onPaginationModelChange={setPaginationModel}
                    getRowId={(row) => row.licenseID}
                    rowCount={licenseData.length}
                    paginationMode="server"
                    rows={licenseData}
                    sx={{
                        marginLeft: "32px",
                        marginRight: "32px",
                        marginTop: "8px",
                        marginBottom: "8px",
                    }} /> :
                <Box
                    sx={{
                        display: 'flex',
                        justifyContent: 'center',
                        alignItems: 'center',
                        height: 400,
                    }}
                >
                    <CircularProgress />
                </Box>
            }
            {licenseId &&
                <SoftwareLicenseDetailDialog
                    open={!!licenseId}
                    onClose={closeDetail}
                    licenseId={licenseId}
                />
            }
        </Stack>
    );
}