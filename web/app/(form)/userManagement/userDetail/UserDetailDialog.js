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
    Typography,
    MenuItem,
    Select,
    FormControl,
    InputLabel
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { useEffect, useState } from 'react';
import axiosInstance from '@/app/service/axiosConfig';
import ConfirmAlertDialog from '@/app/components/ConfirmAlertDialog';
import User from '@/app/model/User';

/**
 * props:
 *  open: boolean
 *  onClose: () => void
 *  userId?: string | null  如果未传则为创建模式
 */
export default function UserDetailDialog({ open, onClose, userId }) {
    const isCreate = !userId;
    const [userDetail, setUserDetail] = useState(null);
    const [loading, setLoading] = useState(false);
    // top-level
    const [employeeId, setEmployeeId] = useState('');
    const [permissions, setPermissions] = useState(0);
    const [status, setStatus] = useState(0);
    const [password, setPassword] = useState('');
    // nested employee
    const [name, setName] = useState('');
    const [gender, setGender] = useState(0);
    const [department, setDepartment] = useState('');
    const [level, setLevel] = useState(1);
    const [empStatus, setEmpStatus] = useState(0);

    const [confirmOpen, setConfirmOpen] = useState(false);

    useEffect(() => {
        if (!open) return;
        if (isCreate) {
            // reset fields
            setUserDetail(null);
            setEmployeeId('');
            setPermissions(0);
            setStatus(0);
            setPassword('');
            setName('');
            setGender(0);
            setDepartment('');
            setLevel(1);
            setEmpStatus(0);
        } else if (userId) {
            fetchUser();
        }
    }, [open, userId]);

    async function fetchUser() {
        setLoading(true);
        try {
            const { data } = await axiosInstance.get(`/users/${userId}`);
            const user = new User(data);
            setUserDetail(user);
            setEmployeeId(user.employee_id);
            setPermissions(user.permissions);
            setStatus(user.status);
            setName(user.employee?.name || '');
            setGender(user.employee?.gender || 0);
            setDepartment(user.employee?.department || '');
            setLevel(user.employee?.level || 1);
            setEmpStatus(user.employee?.status || 0);
        } catch (err) {
            console.error('Fetch user failed', err);
        } finally {
            setLoading(false);
        }
    }

    async function handleSave() {
        try {
            const payload = {
                employee_id: employeeId,
                permissions,
                status,
                ...(isCreate ? { password } : { user_id: Number(userId) }),
                employee: {
                    name,
                    gender,
                    department,
                    level,
                    status: empStatus,
                    employee_id: employeeId,
                },
            };
            if (isCreate) {
                await axiosInstance.post('/users', payload);
            } else {
                await axiosInstance.put(`/users/${userId}`, payload);
            }
            onClose();
        } catch (err) {
            console.error('Save user failed', err);
        }
    }

    return (
        <>
            <Dialog open={open} onClose={onClose} fullWidth maxWidth="sm">
                <DialogTitle>
                    {isCreate ? '创建用户' : '编辑用户'}
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
                                label="工号"
                                value={employeeId}
                                onChange={(e) => setEmployeeId(e.target.value)}
                                fullWidth
                            />
                            {isCreate && (
                                <TextField
                                    label="密码"
                                    type="password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    fullWidth
                                />
                            )}
                            <TextField
                                label="权限 (数字)"
                                type="number"
                                value={permissions}
                                onChange={(e) => setPermissions(Number(e.target.value))}
                                fullWidth
                            />
                            <FormControl fullWidth>
                                <InputLabel>用户状态</InputLabel>
                                <Select
                                    label="用户状态"
                                    value={status}
                                    onChange={(e) => setStatus(Number(e.target.value))}
                                >
                                    <MenuItem value={0}>激活</MenuItem>
                                    <MenuItem value={1}>禁用</MenuItem>
                                </Select>
                            </FormControl>

                            <Typography variant="subtitle1">员工信息</Typography>
                            <TextField
                                label="姓名"
                                value={name}
                                onChange={(e) => setName(e.target.value)}
                                fullWidth
                            />
                            <FormControl fullWidth>
                                <InputLabel>性别</InputLabel>
                                <Select
                                    label="性别"
                                    value={gender}
                                    onChange={(e) => setGender(Number(e.target.value))}
                                >
                                    <MenuItem value={0}>未知</MenuItem>
                                    <MenuItem value={1}>男</MenuItem>
                                    <MenuItem value={2}>女</MenuItem>
                                </Select>
                            </FormControl>
                            <TextField
                                label="部门"
                                value={department}
                                onChange={(e) => setDepartment(e.target.value)}
                                fullWidth
                            />
                            <TextField
                                label="职级 (数字)"
                                type="number"
                                value={level}
                                onChange={(e) => setLevel(Number(e.target.value))}
                                fullWidth
                            />
                            <FormControl fullWidth>
                                <InputLabel>员工状态</InputLabel>
                                <Select
                                    label="员工状态"
                                    value={empStatus}
                                    onChange={(e) => setEmpStatus(Number(e.target.value))}
                                >
                                    <MenuItem value={0}>在职</MenuItem>
                                    <MenuItem value={1}>离职</MenuItem>
                                </Select>
                            </FormControl>
                        </Stack>
                    )}
                </DialogContent>

                <DialogActions>
                    <Button onClick={onClose}>取消</Button>
                    <Button
                        variant="contained"
                        onClick={() => setConfirmOpen(true)}
                        disabled={
                            loading || !employeeId || !name || !department || (isCreate && !password)
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
                content={isCreate ? '确定创建该用户？' : '确定保存修改？'}
                onConfirm={handleSave}
            />
        </>
    );
}
