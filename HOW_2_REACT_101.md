# How to setup React EZ STYLE

## Installing NPM
```bash
sudo apt install npm
```

## Installing Node
```bash
sudo npm -g install n
sudo n latest
```

## Installing Vite
```bash
npm create vite@latest
# React with Typescript + SWC
```

## Installing Tailwind + DaisyUI
```bash
npm install -D tailwindcss
npx tailwindcss init
npm i -D daisyui@latest
```

## tailwind.config.js with daisyui
```js
/** @type {import('tailwindcss').Config} */
export default {
  content: ["./src/**/*.{html,js,jsx,ts,tsx}"],
  theme: {
    extend: {
      spacing: {
        '128': '32rem',
        '144': '36rem',
      },
      width: {
        '96': '24rem',
        '128': '32rem',
        'almost-full': 'calc(100vw - 2rem)',
        'screen-80': '80vw',
        'screen-70': '70vw'
      },
      height: {
        'almost-full': 'calc(100vh - 2rem)',
        'screen-80': '80vh',
        'screen-70': '70vh'
      },
      minHeight: {
        'almost-full': 'calc(100vh - 2rem)',
        'screen-80': '80vh',
        'screen-70': '70vh',
        'screen-60': '60vh'
      },
    }
  },
  daisyui: {
    themes: ['corporate'], // only one theme
  },
  plugins: [
    require('daisyui'),
  ],
}
```

## Create NPM build script for EZ testing/deploy
build.sh:
```bash
#!/bin/bash

#compile tailwind
npx tailwindcss -i ../static/input.css -o ./src/output.css

# Build the frontend
tsc && vite build

find ./dist/assets/ -type f -name 'index*.js' -exec mv {} ./dist/assets/index.js \;
find ./dist/assets/ -type f -name 'index*.css' -exec mv {} ./dist/assets/index.css \;

# Copy the compiled frontend to be rendered by the backend
mv ./dist/assets/index.js ../static/index.js
mv ./dist/assets/index.css ../static/index.css
cp -p ./src/output.css ../static/output.css
```
inside package.json, change build line to:
```
"build": "./build.sh",
```
! MAKE SURE ITS EXECUTABLE !

## Install QOL things (optional):
```bash
npm i -D classnames
npm i -D tailwind-merge
npm i --save-dev sass
npm i --save-dev react-bootstrap
npm i -D react-router-dom
```

## Basic main.tsx with react-router-dom
```ts
import { createRoot } from 'react-dom/client'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

// components are held in components folder in src folder
import IndexPage from './components/IndexPage'
import About from './components/About'
import Contact from './components/Contact'

import './output.css' // output of tailwind css render

const domNode = document.getElementById('root');
if (!domNode) {
  throw new Error('No root element found');
}
const root = createRoot(domNode);
root.render(
  <BrowserRouter>
    <Routes>
      <Route index element={<IndexPage />} />
      <Route path="/" element={<IndexPage />} />
      <Route path="/about" element={<About />} />
      <Route path="/contact" element={<Contact />} />
    </Routes>
  </BrowserRouter>
);

```

## Basic index.html with react-bootstrap
```html
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/webp" href="static/favicon.webp" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>My app 2012!</title>
    <script type="module" crossorigin src="static/index.js"></script>
    <link rel="stylesheet" crossorigin href="static/index.css">
    <link rel="stylesheet" crossorigin href="static/output.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
  </head>
  <body>
    <div id="root"></div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js" integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz" crossorigin="anonymous"></script>
  </body>
</html>

```
