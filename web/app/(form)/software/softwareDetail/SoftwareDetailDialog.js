import { Dialog, Typography } from "@mui/material";

export default function SoftwareDetailDialog({ open, onClose, softwareDetail }) {
    return <Dialog
        open={open}
        onClose={onClose}>
        {
            softwareDetail == null ? <></> : <div>
                <Typography variant="h4">{softwareDetail.softwareInfo.softwareInfoName}</Typography>
                <p>授权ID: {softwareDetail.licenseID}</p>
                <p>到期时间: {softwareDetail.formattedLicenseExpiredDate}</p>
                <p>状态: {softwareDetail.displayLicenseStatus}</p>
            </div>
        }
    </Dialog>;
}