import { Button, CircularProgress, Dialog, DialogContent, DialogTitle, IconButton, LinearProgress, Stack, Typography } from "@mui/material";
import CloseIcon from '@mui/icons-material/Close';
import { useEffect, useState } from "react";
import axiosInstance from "@/app/service/axiosConfig";
import SoftwareLicense from "@/app/model/SoftwareLicense";

export default function SoftwareLicenseDetailDialog({ open, onClose, licenseId }) {
    const [softwareDetail, setSoftwareDetail] = useState(null);

    useEffect(() => {
        fetchData();
    }, []);

    async function fetchData() {
        console.log("licenseId", licenseId);
        const detail = await axiosInstance.get(`/licenses_with_info/${licenseId}`);
        setSoftwareDetail(new SoftwareLicense(detail.data));
    }

    async function receive() {
        await axiosInstance.post('/licenses_usage_records/apply', {
            LicenseID: licenseId,
            Duration_Days: 180,
        });
        fetchData();
    }

    return <Dialog
        open={open}
        onClose={onClose}>
        <DialogTitle>
            软件详情
        </DialogTitle>
        <IconButton
            aria-label="close"
            onClick={onClose}
            sx={(theme) => ({
                position: 'absolute',
                right: 8,
                top: 8,
                color: theme.palette.grey[500],
            })}>
            <CloseIcon />
        </IconButton>
        <DialogContent>
            {
                softwareDetail === null ? <Stack direction="row" sx={{ gap: "16px", alignItems: "center" }}>
                    <CircularProgress />
                    <Typography variant="body1">加载中...</Typography>
                </Stack> : <>
                    <Stack
                        direction="column"
                        sx={{
                            gap: "8px",
                            marginBottom: "16px",
                        }}>
                        <Typography variant="h4">{softwareDetail.softwareInfo.softwareInfoName}</Typography>
                        <Typography variant="body1"><b>软件ID：</b>{softwareDetail.softwareInfoID}</Typography>
                        <Button variant="contained" disableElevation onClick={receive}>
                            领用
                        </Button>
                    </Stack>
                    <Typography variant="h6">授权信息</Typography>
                    <Typography variant="body1"><b>授权ID: </b>{softwareDetail.licenseID}</Typography>
                    <Typography variant="body1"><b>到期时间: </b>{softwareDetail.formattedLicenseExpiredDate}</Typography>
                    <Typography variant="body1"><b>状态: </b>{softwareDetail.displayLicenseStatus}</Typography>
                </>
            }
        </DialogContent>
    </Dialog>;
}