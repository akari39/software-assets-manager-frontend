'use client';

import { useEffect, useState } from "react";
import Snackbar from '@mui/material/Snackbar';
import Alert from '@mui/material/Alert';
import { useError } from "../context/ErrorProvider";

export default function GlobalSnackbar() {
  const { error, clearError } = useError();
  const [open, setOpen] = useState(false);

  // Open the snackbar whenever an error is set
  useEffect(() => {
    if (error) {
      setOpen(true);
    }
  }, [error]);

  // Close handler for the Snackbar
  const handleClose = (event, reason) => {
    // Prevent closing on clickaway if needed
    if (reason === 'clickaway') {
      return;
    }
    setOpen(false);
    clearError(); // Clear the error in global state
  };

  return (
    <Snackbar
      open={open}
      autoHideDuration={6000}
      onClose={handleClose}
      anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
    >
      <Alert onClose={handleClose} severity="error" sx={{ width: '100%' }}>
        {(typeof(error) == String) ? error : JSON.stringify(error)}
      </Alert>
    </Snackbar>
  );
}
