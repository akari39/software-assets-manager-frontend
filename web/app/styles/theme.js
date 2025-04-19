'use client';
import { createTheme } from '@mui/material/styles';

const theme = createTheme({
    primary: {
        main: '#4478d8',
        light: '#4478d8',
        dark: '#2f5fc3',
        contrastText: '#ffffff',
    },
    secondary: {
        main: '#FFCA4F',
        light: '#FFCA4F',
        dark: '#B37800',
        contrastText: '#000000',
    }, 
    colorSchemes: {
        light: true, 
        dark: true
    },
    breakpoints: {
        values: {
            xs: 0,
            sm: 600,
            md: 600,
            lg: 1200,
            xl: 1536,
        },
    },
});

export default theme;
