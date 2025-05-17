'user client';

import { Button, Dialog, DialogActions, DialogContent, DialogTitle, IconButton, Stack } from "@mui/material";
import CloseIcon from '@mui/icons-material/Close';
import { Fragment, useState } from "react";

export default function EditFormDialog({ open, onClose, title, children }) {
    const [editMode, setEditMode] = useState(false);

    function exitEditMode() {
        setEditMode(false);
    }

    function finishEditing() {
        exitEditMode();
    }

    return (
        <Fragment>
            <Dialog
                open={open}
                onClose={onClose}
                aria-labelledby="alert-dialog-title"
                aria-describedby="alert-dialog-description"
                slotProps={{
                    paper: {
                        sx: {
                            minWidth: "400px",
                        },
                    },
                }}>
                <DialogTitle id="alert-dialog-title">
                    <Stack direction="row" alignItems="center" sx={{ gap: "8px" }}>
                        {title}
                        <Button onClick={onClose} color="primary" size="small">编辑</Button>
                    </Stack>
                </DialogTitle>
                <IconButton
                    aria-label="close"
                    onClick={onClose}
                    sx={(theme) => ({
                        position: 'absolute',
                        right: 10,
                        top: 10,
                        color: theme.palette.grey[500],
                    })}>
                    <CloseIcon />
                </IconButton>
                <DialogContent>

                </DialogContent>
                <DialogActions>
                    {
                        editMode ? <>
                            <Button onClick={exitEditMode}>取消</Button>
                            <Button onClick={finishEditing}>
                                确定
                            </Button>
                        </> : <Button onClick={onClose}>
                            关闭
                        </Button>
                    }
                </DialogActions>
            </Dialog>
        </Fragment>
    );
}