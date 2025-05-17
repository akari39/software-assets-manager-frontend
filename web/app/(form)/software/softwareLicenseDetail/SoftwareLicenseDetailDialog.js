import { Button, CircularProgress, Dialog, DialogContent, DialogTitle, IconButton, Stack, Typography } from "@mui/material";
import CloseIcon from '@mui/icons-material/Close';
import { useEffect, useState } from "react";
import axiosInstance from "@/app/service/axiosConfig";
import SoftwareLicense from "@/app/model/SoftwareLicense";
import ConfirmAlertDialog from "@/app/components/ConfirmAlertDialog";

export default function SoftwareLicenseDetailDialog({ open, onClose, licenseId }) {
    const [softwareDetail, setSoftwareDetail] = useState(null);
    const [confirmAlertDialogOpen, setConfirmAlertDialogOpen] = useState(false);

    useEffect(() => {
        fetchData();
    }, []);

    async function fetchData() {
        const detail = await axiosInstance.get(`/licenses_with_info/${licenseId}`);
        setSoftwareDetail(new SoftwareLicense(detail.data));
    }

    async function renewLicense() {
        const detail = await axiosInstance.post(`/licenses_usage_records/${licenseId}/renew`, {
            RecordID: licenseId,
            Duration_Days: 60,
        });
        setSoftwareDetail(new SoftwareLicense(detail.data));
    }

    async function receive() {
        await axiosInstance.post('/licenses_usage_records/apply', {
            LicenseID: licenseId,
            Duration_Days: 60,
        });
        fetchData();
    }

    return <Dialog
        open={open}
        onClose={onClose}
        slotProps={{
            paper: {
                sx: {
                    minWidth: "400px",
                },
            },
        }}>
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
                softwareDetail === null ? <Stack direction="row" sx={{ gap: "20px", alignItems: "center" }}>
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
                        <Stack direction="row">
                            <Button variant="contained"
                                disableElevation
                                fullWidth
                                onClick={softwareDetail.licenseStatus === 1 ? () => setConfirmAlertDialogOpen(true) : receive}
                                sx={{ marginRight: "8px" }}>
                                {
                                    softwareDetail.licenseStatus === 1 ? "续租" : "领用"
                                }
                            </Button>
                        </Stack>
                        <ConfirmAlertDialog
                                title="要续租吗？"
                                content="续租将延长60天资产使用权。"
                                open={confirmAlertDialogOpen}
                                setOpen={setConfirmAlertDialogOpen}
                                onConfirm={renewLicense} />
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