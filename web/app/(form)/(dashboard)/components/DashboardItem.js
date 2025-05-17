import { Box, Card, Link, Stack, Typography, useTheme } from "@mui/material";

export default function DashboardItem({ number, title, href, tintColor }) {
    const theme = useTheme();

    return (
        <Card
            sx={{
                borderRadius: "12px",
                flexGrow: 1, padding: "12px",
                border: `1px solid ${theme.palette.divider}`,
                boxShadow: 'none'
            }}>
            <Stack direction="column">
                <Stack direction="row">
                    <Box style={{
                        width: "12px",
                        borderRadius: "16px",
                        backgroundColor: tintColor,
                    }} />
                    <Stack direction="column" sx={{
                        marginLeft: "16px",
                    }}>
                        <Typography variant="h3" sx={{ fontWeight: 700 }}>{number}</Typography>
                        <Typography variant="h6" color={theme.palette.text.secondary} >{title}</Typography>
                    </Stack>
                </Stack>
                <Box sx={{ height: "32px" }} />
                {href != null && href != undefined ?
                    <Link href={href}>详情</Link>
                    : <></>}
            </Stack>
        </Card>
    );
}