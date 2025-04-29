import * as React from 'react';
import { SignInPage } from '@toolpad/core/SignInPage';
import { AuthError } from 'next-auth';
import { providerMap, signIn } from '@/app/auth';

export default function SignIn() {
    return (
        <SignInPage
            providers={providerMap}
            signIn={async (
                provider,
                formData,
                callbackUrl,
            ) => {
                'use server';
                // pull out email & password from the form
                const email = formData.get('email')?.toString();
                const password = formData.get('password')?.toString();

                try {
                    // server-side call into your NextAuth route
                    return await signIn(provider.id, {
                        email,
                        password,
                        callbackUrl: callbackUrl ?? '/',
                    });
                } catch (error) {
                    // NEXT_REDIRECT is how NextAuth signals a redirect
                    if (error instanceof Error && error.message === 'NEXT_REDIRECT') {
                        throw error;
                    }
                    if (error instanceof AuthError) {
                        return { error: error.message, type: error.type };
                    }
                    return { error: 'Something went wrong.', type: 'UnknownError' };
                }
            }}
        />
    );
}
