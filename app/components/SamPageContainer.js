import { usePathname } from "next/navigation";
import { getTitleByPath } from "../(form)/layout";
import { useEffect } from "react";
import { Box, Typography } from "@mui/material";

export default function SAMPageContainer({ children }) {
    const pathname = usePathname();

    useEffect(() => {
        console.log(pathname);
    }, [pathname]);

    return (<>
        <Box sx={{
            margin: "32px",
        }}>
            <Typography variant="h4">{getTitleByPath(pathname)}</Typography>
        </Box>
        {children}
    </>);
}