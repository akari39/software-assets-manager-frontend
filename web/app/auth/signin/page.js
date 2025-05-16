'use client';

import * as React from 'react';
import { SignInPage } from '@toolpad/core/SignInPage';
import { signInAction } from './actions';

export default function SignIn() {
    return (
        <SignInPage
            providers={[
                {
                    id: 'credentials',
                    name: 'Email and Password',
                },
            ]}
            localeText={{
                signInTitle: '登录',
                signInSubtitle: '请输入邮箱和密码继续',
                oauthSignInTitle: '使用第三方账号登录',
                magicLinkSignInTitle: 'Magic Link 登录',
                passkeySignInTitle: 'Passkey 登录',
                signInRememberMe: '记住我',
                email: '工号',
                password: '密码',
                or: '或',
                with: '使用',
                cancel: '取消',
                ok: '确定',
                save: '保存',
                close: '关闭',
                to: '到',
            }}
            slotProps={{
                emailField: {
                    placeholder: '请输入工号',
                    type: 'text',
                },
            }}
            signIn={signInAction}
        />
    );
}