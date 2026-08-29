import React, { Suspense } from 'react';
import LoadingSpinner from './components/ui/LoadingSpinner';
import { AppRoutes } from './routes';

const App: React.FC = () => {
  return (
    <Suspense fallback={<LoadingSpinner fullscreen />}>
      <AppRoutes />
    </Suspense>
  );
};

export default App;
