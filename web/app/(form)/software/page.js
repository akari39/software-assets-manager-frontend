'use client';

import FilterSearchBar from "@/app/components/FilterSearchBar";
import SingleChoiceChipFilter from "@/app/components/SingleChoiceChipFilter";
import SoftwareLicense from "@/app/model/SoftwareLicense";
import axiosInstance from "@/app/service/axiosConfig";
import { Link, Stack } from "@mui/material";
import { DataGrid, GridActionsCellItem, GridToolbar } from '@mui/x-data-grid';
import { useEffect, useMemo, useState } from "react";


const SOFTWARE_SEARCH_OPTIONS = [
    { value: "all", name: "全部" },
    { value: "b", name: "丰川祥子" },
];

const SOFTWARE_DEFALUT_SEARCH_OPTIONS = SOFTWARE_SEARCH_OPTIONS[0];

const SOFTWARE_CHOICES = [
    { name: '已领用', value: 0, isDefault: true },
    { name: '全部', value: 1 },
];

export default function Software() {
    const [licenseData, setLicenseData] = useState(null);
    const [status, setStatus] = useState(SOFTWARE_CHOICES.find((choice) => choice.isDefault) ?? null);
    const [paginationModel, setPaginationModel] = useState({
        page: 0,
        pageSize: 25,
    });

    useEffect(() => {
        fetchData();
    }, [status]);

    async function fetchData() {
        const response = await axiosInstance.get('/licenses_with_info/', {
            params: {
                page: paginationModel.page + 1,
                limit: paginationModel.pageSize,
                status: status.value,
            },
        });
        const data = response.data;
        setLicenseData(SoftwareLicense.fromArray(data));
    }

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
                    icon={<Link>查看详情</Link>}
                    label="查看详情"
                    onClick={() => { }}
                    showInMenu={false}
                    disableRipple
                />
            ],
        },
    ]);

    function SoftwareAssetsGridToolbar() {
        return (
            <GridToolbar
                csvOptions={{
                    utf8WithBom: true,
                }}
            />
        );
    }

    return (
        <Stack direction="column" >
            <SingleChoiceChipFilter
                choices={SOFTWARE_CHOICES}
                onClick={(choice) => setStatus(choice)}
                selectedChoice={status} />
            <FilterSearchBar
                options={SOFTWARE_SEARCH_OPTIONS}
                default={SOFTWARE_DEFALUT_SEARCH_OPTIONS}
                placeholder="搜索软件" />
            <DataGrid
                columns={columns}
                slots={{ toolbar: SoftwareAssetsGridToolbar }}
                paginationModel={paginationModel}
                onPaginationModelChange={(model) => setPaginationModel(model)}
                getRowId={(row) => row.licenseID}
                rowCount={(licenseData ?? []).length}
                paginationMode="server"
                rows={licenseData}
                sx={{
                    marginLeft: "32px",
                    marginRight: "32px",
                    marginTop: "8px",
                    marginBottom: "8px",
                }} />
        </Stack>
    );
}
