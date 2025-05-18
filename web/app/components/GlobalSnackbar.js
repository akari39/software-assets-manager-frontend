'use client';

import { useEffect, useState } from "react";
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';
import { useSnackbar } from "../context/SnackbarProvider";

export let globalSnackbarHandler = null;
export function setGlobalSnackbarHandler(handler) {
  globalSnackbarHandler = handler;
}

export default function GlobalSnackbar() {
  const { snackbarTip, clearSnackbar } = useSnackbar();
  const [open, setOpen] = useState(false);

  // Open the snackbar whenever an error is set
  useEffect(() => {
    if (snackbarTip) {
      setOpen(true);
    }
  }, [snackbarTip]);

  // Close handler for the Snackbar
  const handleClose = (event, reason) => {
    // Prevent closing on clickaway if needed
    if (reason === 'clickaway') {
      return;
    }
    setOpen(false);
    clearSnackbar();
  };

  return (
    snackbarTip &&
    <Snackbar
      open={open}
      autoHideDuration={6000}
      onClose={handleClose}
      anchorOrigin={{ vertical: 'top', horizontal: 'center' }}>
      <Alert onClose={handleClose} severity={snackbarTip?.type} sx={{ width: '100%' }}>
        {(typeof snackbarTip?.tip === 'string') ? snackbarTip?.tip : JSON.stringify(snackbarTip?.tip)}
      </Alert>
    </Snackbar>
  );
}