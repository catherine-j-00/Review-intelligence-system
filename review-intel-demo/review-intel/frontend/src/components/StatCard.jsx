export default function StatCard({ label, value, sub }) {
  return <div className='card'><small>{label}</small><b>{value}</b>{sub && <small>{sub}</small>}</div>;
}
