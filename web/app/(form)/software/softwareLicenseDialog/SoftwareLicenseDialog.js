'use client';

import {
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    TextField,
    Button,
    IconButton,
    Stack,
    CircularProgress,
    MenuItem,
    Select,
    FormControl,
    InputLabel
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { useEffect, useState } from 'react';
import axiosInstance from '@/app/service/axiosConfig';
import ConfirmAlertDialog from '@/app/components/ConfirmAlertDialog';
import SoftwareLicense from '@/app/model/SoftwareLicense';

/**
 * props:
 *  open: boolean
 *  onClose: () => void
 *  licenseId?: string | null 如果未传则为创建模式
 */
export default function SoftwareLicenseDialog({ open, onClose, licenseId }) {
    const isCreate = !licenseId;
    const [licenseDetail, setLicenseDetail] = useState(null);
    const [loading, setLoading] = useState(false);
    // fields
    const [softwareInfoID, setSoftwareInfoID] = useState(0);
    const [licenseType, setLicenseType] = useState(0);
    const [licenseStatus, setLicenseStatus] = useState(0);
    const [licenseKey, setLicenseKey] = useState('');
    const [licenseExpiredDate, setLicenseExpiredDate] = useState('');
    const [lvLimit, setLvLimit] = useState(0);
    const [remark, setRemark] = useState('');

    const [confirmOpen, setConfirmOpen] = useState(false);

    useEffect(() => {
        if (!open) return;
        if (isCreate) {
            setLicenseDetail(null);
            setSoftwareInfoID(0);
            setLicenseType(0);
            setLicenseStatus(0);
            setLicenseKey('');
            setLicenseExpiredDate('');
            setLvLimit(0);
            setRemark('');
        } else {
            fetchLicense();
        }
    }, [open, licenseId]);

    async function fetchLicense() {
        setLoading(true);
        try {
            const { data } = await axiosInstance.get(`/softwarelicense/${licenseId}`);
            const lic = new SoftwareLicense(data);
            setLicenseDetail(lic);
            setSoftwareInfoID(lic.softwareInfoID);
            setLicenseType(lic.licenseType);
            setLicenseStatus(lic.licenseStatus);
            setLicenseKey(lic.licenseKey ?? '');
            setLicenseExpiredDate(
                lic.licenseExpiredDate?.slice(0, 16) ?? ''
            ); // for datetime-local
            setLvLimit(lic.lvLimit);
            setRemark(lic.remark ?? '');
        } catch (err) {
            console.log('Fetch license failed', err);
        } finally {
            setLoading(false);
        }
    }

    async function handleSave() {
        const payload = {
            SoftwareInfoID: Number(softwareInfoID),
            LicenseType: Number(licenseType),
            LicenseStatus: Number(licenseStatus),
            LicenseKey: licenseKey,
            LicenseExpiredDate: new Date(licenseExpiredDate).toISOString(),
            LvLimit: Number(lvLimit),
            Remark: remark,
        };
        try {
            if (isCreate) {
                await axiosInstance.post('/softwarelicense', payload);
            } else {
                await axiosInstance.put(`/softwarelicense/${licenseId}`, payload);
            }
            onClose();
        } catch (err) {
            console.log('Save license failed', err);
        }
    }

    return (
        <>
            <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
                <DialogTitle>
                    {isCreate ? '创建授权' : '编辑授权'}
                    <IconButton
                        aria-label="close"
                        onClick={onClose}
                        sx={{ position: 'absolute', right: 8, top: 8 }}
                    >
                        <CloseIcon />
                    </IconButton>
                </DialogTitle>

                <DialogContent dividers>
                    {loading ? (
                        <Stack alignItems="center" p={2}>
                            <CircularProgress />
                        </Stack>
                    ) : (
                        <Stack spacing={2}>
                            <TextField
                                label="软件信息ID"
                                type="number"
                                value={softwareInfoID}
                                onChange={e => setSoftwareInfoID(Number(e.target.value))}
                                fullWidth
                            />
                            <FormControl fullWidth>
                                <InputLabel>软件类型</InputLabel>
                                <Select
                                    label="软件类型"
                                    value={licenseType}
                                    onChange={(e) => setStatus(Number(e.target.value))}
                                >
                                    <MenuItem value={0}>操作系统授权</MenuItem>
                                    <MenuItem value={1}>办公类软件</MenuItem>
                                    <MenuItem value={2}>开发类软件</MenuItem>
                                    <MenuItem value={3}>设计类软件</MenuItem>
                                    <MenuItem value={4}>流媒体访问许可</MenuItem>
                                    <MenuItem value={5}>其他</MenuItem>
                                </Select>
                            </FormControl>
                            <FormControl fullWidth>
                                <InputLabel>授权状态</InputLabel>
                                <Select
                                    label="授权状态"
                                    value={licenseStatus}
                                    onChange={(e) => setStatus(Number(e.target.value))}
                                >
                                    <MenuItem value={0}>可用</MenuItem>
                                    <MenuItem value={1}>已领用</MenuItem>
                                    <MenuItem value={2}>已过期</MenuItem>
                                </Select>
                            </FormControl>
                            <TextField
                                label="授权密钥"
                                value={licenseKey}
                                onChange={e => setLicenseKey(e.target.value)}
                                fullWidth
                            />
                            <TextField
                                label="到期时间"
                                type="datetime-local"
                                value={licenseExpiredDate}
                                onChange={e => setLicenseExpiredDate(e.target.value)}
                                InputLabelProps={{ shrink: true }}
                                fullWidth
                            />
                            <TextField
                                label="级别限制 (数字)"
                                type="number"
                                value={lvLimit}
                                onChange={e => setLvLimit(Number(e.target.value))}
                                fullWidth
                            />
                            <TextField
                                label="备注"
                                value={remark}
                                onChange={e => setRemark(e.target.value)}
                                multiline
                                rows={3}
                                fullWidth
                            />
                        </Stack>
                    )}
                </DialogContent>

                <DialogActions>
                    <Button onClick={onClose}>取消</Button>
                    <Button
                        variant="contained"
                        onClick={() => setConfirmOpen(true)}
                        disabled={
                            loading || !softwareInfoID || !licenseKey
                        }
                    >
                        {isCreate ? '创建' : '保存'}
                    </Button>
                </DialogActions>
            </Dialog>

            <ConfirmAlertDialog
                open={confirmOpen}
                setOpen={setConfirmOpen}
                title={isCreate ? '创建确认' : '保存确认'}
                content={
                    isCreate ? '确定创建该授权记录？' : '确定保存修改？'
                }
                onConfirm={handleSave}
            />
        </>
    );
}
