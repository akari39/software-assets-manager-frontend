import NextAuth from 'next-auth';
import CredentialsProvider from 'next-auth/providers/credentials';

const providers = [
    CredentialsProvider({
        id: 'credentials',
        name: 'Email and Password',
        credentials: {
            email: { label: 'Email', type: 'text', placeholder: 'you@example.com' },
            password: { label: 'Password', type: 'password' },
        },
        async authorize(credentials) {
            // 1) call your backend login API
            const res = await fetch(`${process.env.BACKEND_URL}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: credentials?.email,
                    password: credentials?.password,
                }),
            });
            const user = await res.json();

            // 2) if successful, NextAuth will store this object in the JWT
            if (res.ok && user?.token) {
                return {
                    id: user.id,
                    name: user.name,
                    email: user.email,
                    accessToken: user.token,
                };
            }
            // on failure, return null → signIn() will return an error
            return null;
        },
    }),
];

export const providerMap = providers.map((p) => ({
    id: p.id,
    name: p.name,
}));

export const { handlers, auth, signIn, signOut } = NextAuth({
    providers,
    secret: process.env.AUTH_SECRET,
    session: { strategy: 'jwt' },
    callbacks: {
        // write accessToken into the JWT on first sign in
        async jwt({ token, user }) {
            if (user) {
                token.accessToken = user.accessToken;
            }
            return token;
        },
        // expose it on the session object
        async session({ session, token }) {
            session.user = {
                ...session.user,
                accessToken: token.accessToken,
            };
            return session;
        },
    },
    pages: {
        signIn: '/auth/signin',
    },
});