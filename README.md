This is a [Next.js](https://nextjs.org) project bootstrapped with [`create-next-app`](https://nextjs.org/docs/app/api-reference/cli/create-next-app).

## Getting Started

First, run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
# or
bun dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

You can start editing the page by modifying `app/page.js`. The page auto-updates as you edit the file.

This project uses [`next/font`](https://nextjs.org/docs/app/building-your-application/optimizing/fonts) to automatically optimize and load [Geist](https://vercel.com/font), a new font family for Vercel.

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

You can check out [the Next.js GitHub repository](https://github.com/vercel/next.js) - your feedback and contributions are welcome!

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.

Check out our [Next.js deployment documentation](https://nextjs.org/docs/app/building-your-application/deploying) for more details.

```
software-assets-manager-frontend
├─ .envrc
├─ LICENSE
├─ README.md
├─ api
│  ├─ dependencies.py
│  ├─ main.py
│  ├─ models
│  │  ├─ __int__.py
│  │  ├─ softwareinfo.py
│  │  └─ softwarelicense.py
│  ├─ requirements.txt
│  ├─ routers
│  │  ├─ SoftwareLicenseList_With_SoftwareInfo.py
│  │  ├─ softwareinfo.py
│  │  └─ softwarelicense.py
│  └─ schemas
│     ├─ SoftwareLicenseList_With_SoftwareInfo.py
│     ├─ __int__.py
│     ├─ softwareinfo.py
│     └─ softwarelicense.py
├─ shell.nix
└─ web
   ├─ .env.local
   ├─ .next
   │  ├─ cache
   │  │  ├─ .rscinfo
   │  │  ├─ eslint
   │  │  │  └─ .cache_eu4ljy
   │  │  ├─ swc
   │  │  │  └─ plugins
   │  │  │     └─ v7_macos_aarch64_8.0.0
   │  │  └─ webpack
   │  │     ├─ client-development
   │  │     │  ├─ 0.pack.gz
   │  │     │  ├─ 1.pack.gz
   │  │     │  ├─ 2.pack.gz
   │  │     │  ├─ 3.pack.gz
   │  │     │  ├─ 4.pack.gz
   │  │     │  ├─ index.pack.gz
   │  │     │  └─ index.pack.gz.old
   │  │     ├─ client-production
   │  │     │  ├─ 0.pack
   │  │     │  └─ index.pack
   │  │     ├─ edge-server-production
   │  │     │  ├─ 0.pack
   │  │     │  └─ index.pack
   │  │     ├─ server-development
   │  │     │  ├─ 0.pack.gz
   │  │     │  ├─ 1.pack.gz
   │  │     │  ├─ 2.pack.gz
   │  │     │  ├─ 3.pack.gz
   │  │     │  ├─ 4.pack.gz
   │  │     │  ├─ 5.pack.gz
   │  │     │  ├─ index.pack.gz
   │  │     │  └─ index.pack.gz.old
   │  │     └─ server-production
   │  │        ├─ 0.pack
   │  │        ├─ 1.pack
   │  │        ├─ 2.pack
   │  │        ├─ 3.pack
   │  │        ├─ 4.pack
   │  │        ├─ index.pack
   │  │        └─ index.pack.old
   │  ├─ diagnostics
   │  │  ├─ build-diagnostics.json
   │  │  └─ framework.json
   │  └─ package.json
   ├─ app
   │  ├─ (form)
   │  │  ├─ (dashboard)
   │  │  │  └─ page.js
   │  │  ├─ layout.js
   │  │  └─ software
   │  │     └─ page.js
   │  ├─ auth
   │  │  ├─ layout.js
   │  │  └─ signin
   │  │     └─ page.js
   │  ├─ auth.js
   │  ├─ components
   │  │  ├─ FilterSearchBar.js
   │  │  ├─ GlobalSnackbar.js
   │  │  ├─ SamPageContainer.js
   │  │  └─ SingleChoiceChipFilter.js
   │  ├─ context
   │  │  └─ ErrorProvider.js
   │  ├─ favicon.ico
   │  ├─ model
   │  │  └─ SoftwareLicense.js
   │  ├─ service
   │  │  └─ axiosConfig.js
   │  └─ styles
   │     └─ theme.js
   ├─ eslint.config.mjs
   ├─ jsconfig.json
   ├─ next.config.mjs
   ├─ package-lock.json
   ├─ package.json
   └─ public
      ├─ file.svg
      ├─ globe.svg
      ├─ next.svg
      ├─ vercel.svg
      └─ window.svg

```