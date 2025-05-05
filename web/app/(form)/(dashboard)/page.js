'use client';

import { colors, Stack, useTheme } from "@mui/material";
import DashboardItem from "./components/DashboardItem";

export default function Dashboard() {
  const theme = useTheme();

  return (
    <Stack direction="column">
      <Stack 
        direction={{ sm: "column", md: "row" }}
        spacing={{ xs: 2, sm: 2, md: 4 }}
        padding="32px">
        <DashboardItem number={2} title="正在使用" href={"software"} tintColor={colors.green[500]}/>
        <DashboardItem number={2} title="即将过期" href={"software"} tintColor={colors.red[500]}/>
        <DashboardItem number={2} title="可领用" href={"software"} tintColor={colors.blue[500]}/>
      </Stack>
    </Stack>
  );
}