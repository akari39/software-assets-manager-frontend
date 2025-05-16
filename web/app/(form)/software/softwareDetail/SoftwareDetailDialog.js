import { Button, Dialog, DialogContent, DialogTitle, IconButton, Stack, Typography } from "@mui/material";
import CloseIcon from '@mui/icons-material/Close';

export default function SoftwareDetailDialog({ open, onClose, softwareDetail }) {

    return softwareDetail == null ? <></> : <Dialog
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
            <Stack
                direction="column"
                sx={{
                    gap: "8px",
                    marginBottom: "16px",
                }}>
                <Typography variant="h4">{softwareDetail.softwareInfo.softwareInfoName}</Typography>
                <Typography variant="body1"><b>软件ID：</b>{softwareDetail.softwareInfoID}</Typography>
                <Button variant="contained" disableElevation>
                    领用
                </Button>
            </Stack>
            <Typography variant="h6">授权信息</Typography>
            <Typography variant="body1"><b>授权ID: </b>{softwareDetail.licenseID}</Typography>
            <Typography variant="body1"><b>到期时间: </b>{softwareDetail.formattedLicenseExpiredDate}</Typography>
            <Typography variant="body1"><b>状态: </b>{softwareDetail.displayLicenseStatus}</Typography>
        </DialogContent>
    </Dialog>;
}