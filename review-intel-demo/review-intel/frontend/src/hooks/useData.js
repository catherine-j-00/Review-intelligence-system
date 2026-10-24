import { useEffect, useState } from 'react';

export function useData(fetcher, deps) {
  const [state, setState] = useState({ data: null, loading: true, error: null });
  useEffect(() => {
    let cancelled = false;
    setState((s) => ({ ...s, loading: true, error: null }));
    fetcher()
      .then((data) => { if (!cancelled) setState({ data, loading: false, error: null }); })
      .catch((e) => {
        if (!cancelled) setState({ data: null, loading: false,
          error: (e.response && e.response.data && e.response.data.error) || e.message });
      });
    return () => { cancelled = true; }; // ignore answers from outdated requests
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);
  return state;
}
