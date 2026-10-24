import { createContext, useContext, useMemo, useState } from 'react';

const FilterContext = createContext(null);
export const useFilters = () => useContext(FilterContext);

const EMPTY = { category: '', brand: '', product: '', year: '', month: '',
  sentiment: '', emotion: '', date_from: '', date_to: '', data: 'real' };

export function FilterProvider({ children }) {
  const [filters, setFilters] = useState(EMPTY);
  // params = only the filters that are filled in. This is what we send to the API.
  const params = useMemo(
    () => Object.fromEntries(Object.entries(filters).filter(([, v]) => v !== '')), [filters]);
  const value = { filters, setFilters, params, reset: () => setFilters(EMPTY) };
  return <FilterContext.Provider value={value}>{children}</FilterContext.Provider>;
}
