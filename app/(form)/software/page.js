'use client';

import SingleChoiceChipFilter from "@/app/components/SingleChoiceChipFilter";
import { useEffect, useState } from "react";

const SOFTWARE_USING = '正在使用';
const SOFTWARE_ALL = '全部';
const DEFAULT_SOFTWARE_USAGE = SOFTWARE_USING;

function useSoftwareUsageChoices() {
    const [softwareUsageChoices, setSoftwareUsageChoices] = useState({
        [`${SOFTWARE_USING}`]: { selected: false, onClick: () => setSelected(SOFTWARE_USING) },
        [`${SOFTWARE_ALL}`]: { selected: false, onClick: () => setSelected(SOFTWARE_ALL) }
    });

    useEffect(() => {
        setSelected(DEFAULT_SOFTWARE_USAGE);
    }, []);

    function setSelected(choiceName) {
        setSoftwareUsageChoices((prevState) => Object.fromEntries(
            Object.entries(prevState).map(([key, value]) => [
                key,
                { ...value, selected: key === choiceName }
            ])
        ));
    }

    return softwareUsageChoices;
}

export default function Software() {
    const softwareUsageChoices = useSoftwareUsageChoices();

    return (
        <>
            <SingleChoiceChipFilter choices={softwareUsageChoices} />
        </>
    );
}