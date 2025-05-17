'use client';

import FilterSearchBar from "@/app/components/FilterSearchBar";
import SingleChoiceChipFilter from "@/app/components/SingleChoiceChipFilter";
import SoftwareInfo from "@/app/model/SoftwareInfo";
import SoftwareType from "@/app/model/SoftwareType";
import axiosInstance from "@/app/service/axiosConfig";
import { Link, Stack, Box, Paper } from "@mui/material";
import { DataGrid, GridActionsCellItem } from '@mui/x-data-grid';
import { useEffect, useMemo, useState } from "react";
import { usePathname, useSearchParams } from "next/navigation";

export default function SoftwareDetail() {
    const [softwareInfoData, setSoftwareInfoData] = useState(null);
    const [paginationModel, setPaginationModel] = useState({
        page: 0,
        pageSize: 25,
    });

    useEffect(() => {
        fetchData();
    }, []);

    async function fetchData() {
        let api = '/softwareinfo';
        let params = {
            page: paginationModel.page + 1,
            limit: paginationModel.pageSize,
        };
        try {
            const response = await axiosInstance.get(api, {
                params: params,
            });
            const data = response.data;
            setSoftwareInfoData(SoftwareInfo.fromArray(data));
        } catch (error) {
        }
    }

    const columns = useMemo(() => [
        {
            field: 'softwareInfoID',
            headerName: '软件ID',
            flex: 1,
        },
        {
            field: 'softwareInfoName',
            headerName: '软件名称',
            flex: 2,
        },
        {
            field: 'softwareInfoType',
            headerName: '软件类型',
            flex: 2,
            valueGetter: (value, row) => SoftwareType.getName(row.softwareInfoType),
        },
    ]);


    return (
        <Stack direction="column" >
            {softwareInfoData !== null &&
                <DataGrid
                    columns={columns}
                    paginationModel={paginationModel}
                    onPaginationModelChange={setPaginationModel}
                    getRowId={(row) => row.softwareInfoID}
                    rowCount={softwareInfoData.length}
                    paginationMode="server"
                    rows={softwareInfoData}
                    sx={{
                        marginLeft: "32px",
                        marginRight: "32px",
                        marginTop: "8px",
                        marginBottom: "8px",
                    }} />
            }
        </Stack>
    );
}