'use client';

import { usePathname } from "next/navigation";
import { getTitleByPath } from "../layout";
import { Box, Typography } from "@mui/material";

export default function SAMPageContainer({ children }) {
    const pathname = usePathname();

    return (<>
        <Box sx={{
            margin: "32px",
        }}>
            <Typography variant="h4">{getTitleByPath(pathname)}</Typography>
        </Box>
        {children}
    </>);
}