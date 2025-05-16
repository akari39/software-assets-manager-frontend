'use client';

import { DashboardLayout } from "@toolpad/core";
import SAMPageContainer from "../components/SamPageContainer";
import AuthGuard from "../components/AuthGuard";

export default function FormLayout({ children }) {
    return (
        <AuthGuard>
            <DashboardLayout>
                <SAMPageContainer>
                    {children}
                </SAMPageContainer>
            </DashboardLayout>
        </AuthGuard>
    );
}