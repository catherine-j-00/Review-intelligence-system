import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, Legend, LineChart, Line,
  XAxis, YAxis, CartesianGrid, BarChart, Bar } from 'recharts';

const COLORS = { positive: '#2e9d6b', negative: '#d64545', neutral: '#8a94a6' };
const Empty = () => <p className='note'>No data for these filters.</p>;
const H = 260;

export function SentimentDonut({ data }) {
  if (!data || !data.length) return <Empty />;
  return (
    <ResponsiveContainer width='100%' height={H}>
      <PieChart>
        <Pie data={data} dataKey='count' nameKey='label' innerRadius={60} outerRadius={90}>
          {data.map((d) => <Cell key={d.label} fill={COLORS[d.label] || '#999'} />)}
        </Pie>
        <Tooltip /><Legend />
      </PieChart>
    </ResponsiveContainer>
  );
}

export function EmotionBars({ data }) {
  if (!data || !data.length) return <Empty />;
  return (
    <ResponsiveContainer width='100%' height={H}>
      <BarChart data={data} layout='vertical' margin={{ left: 30 }}>
        <CartesianGrid strokeDasharray='3 3' />
        <XAxis type='number' /><YAxis type='category' dataKey='label' width={90} />
        <Tooltip /><Bar dataKey='count' fill='#3566d6' />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function MonthlyReviews({ data }) {
  if (!data || !data.length) return <Empty />;
  return (
    <ResponsiveContainer width='100%' height={H}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray='3 3' /><XAxis dataKey='month' /><YAxis />
        <Tooltip /><Bar dataKey='total_reviews' name='Reviews' fill='#3566d6' />
      </BarChart>
    </ResponsiveContainer>
  );
}

export function MonthlySentiment({ data }) {
  if (!data || !data.length) return <Empty />;
  return (
    <ResponsiveContainer width='100%' height={H}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray='3 3' /><XAxis dataKey='month' />
        <YAxis unit='%' domain={[0, 100]} /><Tooltip /><Legend />
        <Line dataKey='positive_pct' name='Positive %' stroke={COLORS.positive} />
        <Line dataKey='negative_pct' name='Negative %' stroke={COLORS.negative} />
      </LineChart>
    </ResponsiveContainer>
  );
}

export function BrandBars({ data }) {
  if (!data || !data.length) return <Empty />;
  return (
    <ResponsiveContainer width='100%' height={H}>
      <BarChart data={data}>
        <CartesianGrid strokeDasharray='3 3' /><XAxis dataKey='brand' />
        <YAxis unit='%' domain={[0, 100]} /><Tooltip /><Legend />
        <Bar dataKey='positive_pct' name='Positive %' fill={COLORS.positive} />
        <Bar dataKey='negative_pct' name='Negative %' fill={COLORS.negative} />
      </BarChart>
    </ResponsiveContainer>
  );
}
