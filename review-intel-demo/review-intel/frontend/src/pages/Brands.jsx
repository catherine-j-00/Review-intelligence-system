import FilterBar from '../components/FilterBar';
import Panel from '../components/Panel';
import { BrandBars } from '../components/Charts';
import { useFilters } from '../context/FilterContext';
import { useData } from '../hooks/useData';
import { getBrandStats } from '../services/api';

export default function Brands() {
  const { params } = useFilters();
  const key = JSON.stringify(params);
  const brands = useData(() => getBrandStats(params), [key]);
  const rows = brands.data || [];
  return (
    <>
      <h1>Brands</h1>
      <FilterBar />
      <p className='note'>Tip: choose a Category (for example Lipstick) to compare brands fairly.</p>
      <Panel title='Positive and negative % by brand'><BrandBars data={rows} /></Panel>
      <Panel title='Brand comparison'>
        <div className='table-wrap'><table>
          <thead><tr><th>Brand</th><th>Reviews</th><th>Positive</th><th>Negative</th><th>Neutral</th><th>Top emotions</th></tr></thead>
          <tbody>{rows.map((b) => (
            <tr key={b.brand}><td>{b.brand}</td><td>{b.total_reviews}</td><td>{b.positive_pct}%</td>
              <td>{b.negative_pct}%</td><td>{b.neutral_pct}%</td>
              <td>{Object.entries(b.emotions).sort((x, y) => y[1] - x[1]).slice(0, 3)
                .map(([e, n]) => e + ' ' + n).join(', ')}</td></tr>
          ))}</tbody>
        </table></div>
      </Panel>
    </>
  );
}
