'use client';

import SingleChoiceChipFilter from "@/app/components/SingleChoiceChipFilter";
import { useEffect, useState } from "react";

const SOFTWARE_USING = '正在使用';
const SOFTWARE_ALL = '全部';

export default function Software() {
    const [softwareUsageChoices, setSoftwareUsageChoices] = useState({
        [`${SOFTWARE_USING}`]: { selected: true }, // default choice
        [`${SOFTWARE_ALL}`]: { selected: false }
    });

    return (
        <>
            <SingleChoiceChipFilter choices={softwareUsageChoices} />
        </>
    );
}