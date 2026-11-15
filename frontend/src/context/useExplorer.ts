import { useContext } from 'react';
import { ExplorerContext, type ExplorerContextValue } from './store';

export function useExplorer(): ExplorerContextValue {
  const context = useContext(ExplorerContext);
  if (!context) throw new Error('useExplorer must be used within ExplorerProvider.');
  return context;
}
