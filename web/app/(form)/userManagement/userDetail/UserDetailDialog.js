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
  Typography
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
  const [name, setName] = useState('');
  const [department, setDepartment] = useState('');
  const [confirmOpen, setConfirmOpen] = useState(false);

  useEffect(() => {
    if (!open) return;
    if (isCreate) {
      // reset fields
      setUserDetail(null);
      setName('');
      setDepartment('');
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
      setName(user.employee?.name || '');
      setDepartment(user.employee?.department || '');
    } catch (err) {
      console.error('Fetch user failed', err);
    } finally {
      setLoading(false);
    }
  }

  async function handleSave() {
    try {
      const payload = {
        employee_id: isCreate ? undefined : userDetail.employee_id,
        employee: {
          name,
          department
        }
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
                label="姓名"
                value={name}
                onChange={(e) => setName(e.target.value)}
                fullWidth
              />
              <TextField
                label="部门"
                value={department}
                onChange={(e) => setDepartment(e.target.value)}
                fullWidth
              />
              {!isCreate && userDetail && (
                <Typography variant="body2" color="text.secondary">
                  工号: {userDetail.employee_id}
                </Typography>
              )}
            </Stack>
          )}
        </DialogContent>

        <DialogActions>
          <Button onClick={onClose}>取消</Button>
          <Button
            variant="contained"
            onClick={() => setConfirmOpen(true)}
            disabled={loading || !name || !department}
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
