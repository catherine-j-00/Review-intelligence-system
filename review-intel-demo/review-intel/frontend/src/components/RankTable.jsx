import { Link } from 'react-router-dom';

// Shows the review count next to every percentage.
export default function RankTable({ rows }) {
  if (!rows || !rows.length) return <p className='note'>No data for these filters.</p>;
  return (
    <div className='table-wrap'>
      <table>
        <thead><tr><th>Product</th><th>Brand</th><th>Reviews</th><th>Positive</th><th>Negative</th></tr></thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.product_id}>
              <td><Link to={'/products/' + r.product_id}>{r.product}</Link></td>
              <td>{r.brand || '-'}</td><td>{r.total_reviews}</td>
              <td>{r.positive_pct}%</td><td>{r.negative_pct}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
