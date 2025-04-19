'use client';

import FilterSearchBar from "@/app/components/FilterSearchBar";
import SingleChoiceChipFilter from "@/app/components/SingleChoiceChipFilter";
import { Link, Stack } from "@mui/material";
import { DataGrid, GridActionsCellItem, GridToolbar, GridToolbarExport } from '@mui/x-data-grid';
import { useMemo, useState } from "react";

const SOFTWARE_USING = '正在使用';
const SOFTWARE_ALL = '全部';

const SOFTWARE_SEARCH_OPTIONS = [
    { value: "all", name: "全部" },
    { value: "b", name: "丰川祥子" },
];

const SOFTWARE_DEFALUT_SEARCH_OPTIONS = SOFTWARE_SEARCH_OPTIONS[0];

export default function Software() {
    const [softwareUsageChoices, setSoftwareUsageChoices] = useState({
        [`${SOFTWARE_USING}`]: { selected: true }, // default choice
        [`${SOFTWARE_ALL}`]: { selected: false }
    });
    const [paginationModel, setPaginationModel] = useState({
        page: 0,
        pageSize: 25,
    });

    const columns = useMemo(() => [
        { field: 'license_id', headerName: '授权ID', flex: 1 },
        { field: 'name', headerName: '软件名称', flex: 2 },
        { field: 'status', headerName: '授权状态', flex: 1 },
        { field: 'expiration_time', headerName: '过期时间', flex: 2 },
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

    const rows = [
        {
            id: 1,
            license_id: 1,
            name: 'windows',
            status: '已领取',
            expiration_time: '2025-10-24 12:00',
            action: 1,
        },
    ];

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
            <SingleChoiceChipFilter choices={softwareUsageChoices} />
            <FilterSearchBar
                options={SOFTWARE_SEARCH_OPTIONS}
                default={SOFTWARE_DEFALUT_SEARCH_OPTIONS}
                placeholder="搜索软件" />
            <DataGrid
                columns={columns}
                slots={{ toolbar: SoftwareAssetsGridToolbar }}
                paginationModel={paginationModel}
                onPaginationModelChange={(model) => setPaginationModel(model)}
                rowCount={rows.length}
                paginationMode="server"
                rows={rows}
                sx={{
                    marginLeft: "32px",
                    marginRight: "32px",
                    marginTop: "8px",
                    marginBottom: "8px",
                }}
            />
        </Stack>
    );
}
