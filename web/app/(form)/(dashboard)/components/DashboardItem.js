import { Box, Card, colors, Link, Stack, Typography } from "@mui/material";

export default function DashboardItem({ number, title, href, tintColor }) {
    return (
        <Card sx={{ borderRadius: "16px", flexGrow: 1, padding: "12px" }}>
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
                        <Typography variant="h4">{number}</Typography>
                        <Typography variant="body1">{title}</Typography>
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