import { Button, CircularProgress, Dialog, DialogContent, DialogTitle, IconButton, Stack, Typography, MenuItem } from "@mui/material";
import CloseIcon from '@mui/icons-material/Close';
import { useEffect, useState } from "react";
import axiosInstance from "@/app/service/axiosConfig";
import SoftwareLicense from "@/app/model/SoftwareLicense";
import ConfirmAlertDialog from "@/app/components/ConfirmAlertDialog";
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown';
import StyledMenu from '@/app/components/StyledMenu';

export default function SoftwareLicenseDetailDialog({ open, onClose, licenseId }) {
    const [softwareDetail, setSoftwareDetail] = useState(null);
    const [confirmRenewOpen, setConfirmRenewOpen] = useState(false);
    const [confirmReturnOpen, setConfirmReturnOpen] = useState(false);
    const [anchorEl, setAnchorEl] = useState(null);
    const [confirmApplyOpen, setConfirmApplyOpen] = useState(false);
    const [loading, setLoading] = useState(false);

    const menuOpen = Boolean(anchorEl);

    const handleMenuOpen = (event) => setAnchorEl(event.currentTarget);
    const handleMenuClose = () => setAnchorEl(null);

    useEffect(() => {
        if (open && licenseId) fetchData();
    }, [open, licenseId]);

    async function fetchData() {
        setLoading(true);
        try {
            const { data } = await axiosInstance.get(
                `/licenses_with_info/${licenseId}`
            );
            setSoftwareDetail(new SoftwareLicense(data));
        } catch (error) {
            console.error("Error fetching software license detail:", error);
        } finally {
            setLoading(false);
        }
    }

    async function handleApply() {
        setLoading(true);
        try {
            await axiosInstance.post(
                `/licenses_usage_records/apply`,
                { LicenseID: licenseId, Duration_Days: 60 }
            );
            fetchData();
        } catch (error) {
            console.error("Error applying for software license:", error);
            setLoading(false);
        }
    }

    async function handleRenew() {
        setLoading(true);
        try {
            const result = await axiosInstance.post(
                `/licenses_usage_records/renew`,
                { RecordID: licenseId, Renew_Days: 60 }
            );
            fetchData();
        } catch (error) {
            console.error("Error renewing software license:", error);
            setLoading(false);
        }
    }

    async function handleReturn() {
        setLoading(true);
        try {
            const result = await axiosInstance.post(
                `/licenses_usage_records/return`,
                { LicenseID: licenseId }
            );
            fetchData();
        } catch (error) {
            console.error("Error returning software license:", error);
            setLoading(false);
        }
    }

    return (
        <Dialog
            open={open}
            onClose={onClose}
            slotProps={{
                paper: { sx: { minWidth: '400px' } },
            }}
        >
            <DialogTitle>
                软件详情
                <IconButton
                    aria-label="close"
                    onClick={onClose}
                    sx={(theme) => ({ position: 'absolute', right: 8, top: 8, color: theme.palette.grey[500] })}>
                    <CloseIcon />
                </IconButton>
            </DialogTitle>
            <DialogContent>
                {softwareDetail === null || !softwareDetail.softwareInfo ? (
                    <Stack direction="row" alignItems="center" spacing={2}>
                        <CircularProgress />
                        <Typography>加载中...</Typography>
                    </Stack>
                ) : (
                    <>
                        <Stack direction="column" spacing={1.5} mb={2}>
                            <Typography variant="h4">
                                {softwareDetail.softwareInfo.softwareInfoName}
                            </Typography>
                            <Typography>
                                <b>软件ID：</b>{softwareDetail.softwareInfoID}
                            </Typography>


                            {softwareDetail.licenseStatus === 0 ? (
                                <Button
                                    startIcon={loading ? <CircularProgress size={"16px"} /> : null}
                                    disabled={loading}
                                    variant="contained"
                                    onClick={loading ? null : () => setConfirmApplyOpen(true)}>
                                    领用
                                </Button>
                            ) : (
                                <>
                                    {/* 已领用时显示续租/退还菜单 */}
                                    <Stack direction="row" alignItems="start">
                                        <Button
                                            startIcon={loading ? <CircularProgress size={"16px"} /> : null}
                                            disabled={loading}
                                            endIcon={<KeyboardArrowDownIcon />}
                                            onClick={loading ? null : handleMenuOpen} fullWidth>
                                            操作
                                        </Button>
                                        <StyledMenu anchorEl={anchorEl} open={menuOpen} onClose={handleMenuClose}>
                                            <MenuItem onClick={() => setConfirmRenewOpen(true)}>
                                                续租
                                            </MenuItem>
                                            <MenuItem onClick={() => setConfirmReturnOpen(true)} sx={{ color: 'red' }}>
                                                退还
                                            </MenuItem>
                                        </StyledMenu>
                                    </Stack>

                                    <ConfirmAlertDialog
                                        title="续租确认"
                                        content="续租将延长60天资产使用权，确定要续租吗？"
                                        open={confirmRenewOpen}
                                        setOpen={setConfirmRenewOpen}
                                        onConfirm={handleRenew}
                                    />

                                    <ConfirmAlertDialog
                                        title="退还确认"
                                        content="退还后将收回该软件授权，确定要退还吗？"
                                        open={confirmReturnOpen}
                                        setOpen={setConfirmReturnOpen}
                                        onConfirm={handleReturn}
                                    />
                                </>
                            )}

                            {/* 应用确认弹窗 */}
                            <ConfirmAlertDialog
                                title="领用确认"
                                content="领用将获取该软件授权，使用期 60 天，确定要领用吗？"
                                open={confirmApplyOpen}
                                setOpen={setConfirmApplyOpen}
                                onConfirm={handleApply}
                            />
                        </Stack>

                        <Typography><b>授权ID: </b>{softwareDetail.licenseID}</Typography>
                        <Typography><b>到期时间: </b>{softwareDetail.formattedLicenseExpiredDate}</Typography>
                        <Typography><b>状态: </b>{softwareDetail.displayLicenseStatus}</Typography>
                    </>
                )}
            </DialogContent>
        </Dialog>
    );
}
