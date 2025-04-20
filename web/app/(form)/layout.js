'use client';

import { DashboardLayout } from "@toolpad/core";
import SAMPageContainer from "../components/SamPageContainer";

export default function FormLayout({ children }) {
    return (
        <DashboardLayout>
            <SAMPageContainer>
                {children}
            </SAMPageContainer>
        </DashboardLayout>
    );
}