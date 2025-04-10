'use client';

import FilterSearchBar from "@/app/components/FilterSearchBar";
import SingleChoiceChipFilter from "@/app/components/SingleChoiceChipFilter";
import { Stack } from "@mui/material";
import { useState } from "react";

const SOFTWARE_USING = '正在使用';
const SOFTWARE_ALL = '全部';

const SOFTWARE_SEARCH_OPTIONS = [
    { value: "all", name: "全部" },
    { value: "b", name: "丰川祥子" },
];

const SOFTWARE_DEFALUT_SEARCH_OPTIONS = SOFTWARE_SEARCH_OPTIONS[0];

export default function Software() {
    const [softwareUsageChoices, setSoftwareUsageChoices] = useState({
        [`${SOFTWARE_USING}`]: { selected: true }, // default choice
        [`${SOFTWARE_ALL}`]: { selected: false }
    });

    return (
        <Stack direction="column" >
            <SingleChoiceChipFilter choices={softwareUsageChoices} />
            <FilterSearchBar
                options={SOFTWARE_SEARCH_OPTIONS}
                default={SOFTWARE_DEFALUT_SEARCH_OPTIONS}
                placeholder="搜索软件" />
        </Stack>
    );
}