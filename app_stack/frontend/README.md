# RPGer Frontend

This is the React frontend for the RPGer application, built with Vite.

## Project Overview

This project uses:
- React 18
- TypeScript 5.x
- Vite as the build tool
- Socket.IO for real-time communication
- Styled Components for styling

## Available Scripts

In the project directory, you can run:

### `npm start`

Runs the app in the development mode.\
Open [http://localhost:3000](http://localhost:3000) to view it in the browser.

### `npm test`

Launches the Vitest test runner in the interactive watch mode.

### `npm run build`

Builds the app for production to the `build` folder.

### `npm run preview`

Locally preview the production build.

## Environment Variables

The following environment variables can be set in a `.env` file:

- `VITE_API_URL`: URL for the backend API (default: http://localhost:5001)
- `VITE_SOCKET_URL`: URL for the Socket.IO server (default: http://localhost:5002)

## Learn More

- [Vite Documentation](https://vitejs.dev/)
- [React Documentation](https://reactjs.org/)
