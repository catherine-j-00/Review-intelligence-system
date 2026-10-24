import FilterBar from '../components/FilterBar';
import Panel from '../components/Panel';
import { MonthlyReviews, MonthlySentiment } from '../components/Charts';
import { useFilters } from '../context/FilterContext';
import { useData } from '../hooks/useData';
import { getMonthly, getSeasonal } from '../services/api';

export default function Trends() {
  const { params } = useFilters();
  const key = JSON.stringify(params);
  const monthly = useData(() => getMonthly(params), [key]);
  const seasonal = useData(() => getSeasonal(params), [key]);
  const sd = seasonal.data;
  return (
    <>
      <h1>Trends</h1>
      <FilterBar />
      <div className='grid'>
        <Panel title='Reviews per month'><MonthlyReviews data={monthly.data} /></Panel>
        <Panel title='Positive vs negative % per month'><MonthlySentiment data={monthly.data} /></Panel>
      </div>
      <Panel title='Seasonal review activity (feedback trends, not sales)'>
        {sd && !sd.enough_history && (
          <p className='note'>Only {sd.months_of_history} month(s) of data. Seasonal patterns need about 12 months to mean anything.</p>
        )}
        <div className='table-wrap'><table>
          <thead><tr><th>Season</th><th>Category</th><th>Reviews</th><th>Positive</th><th>Negative</th></tr></thead>
          <tbody>{(sd ? sd.rows : []).map((r) => (
            <tr key={r.season + r.category}><td>{r.season}</td><td>{r.category}</td>
              <td>{r.total_reviews}</td><td>{r.positive_pct}%</td><td>{r.negative_pct}%</td></tr>))}</tbody>
        </table></div>
      </Panel>
    </>
  );
}
