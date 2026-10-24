import { useParams } from 'react-router-dom';
import Panel from '../components/Panel';
import StatCard from '../components/StatCard';
import { SentimentDonut, EmotionBars, MonthlyReviews, MonthlySentiment } from '../components/Charts';
import { useData } from '../hooks/useData';
import { useFilters } from '../context/FilterContext';
import { getProductDetail } from '../services/api';

export default function ProductDetail() {
  const { id } = useParams();
  const { params } = useFilters();
  const d = useData(() => getProductDetail(id, { data: params.data }), [id, params.data]);
  if (d.error) return <p className='note'>{d.error}</p>;
  if (!d.data) return <p className='note'>Loading...</p>;
  const p = d.data;
  const s = p.summary;
  const split = [
    { label: 'positive', count: s.positive }, { label: 'negative', count: s.negative },
    { label: 'neutral', count: s.neutral }];
  const list = (items) => (items.length
    ? <ul>{items.map((i) => <li key={i.aspect}>{i.aspect} ({i.mentions})</li>)}</ul>
    : <p className='note'>Not enough data.</p>);
  return (
    <>
      <h1>{p.product}</h1>
      <p className='note'>Brand: {p.brand || '-'} | Category: {p.category || '-'}</p>
      <div className='cards'>
        <StatCard label='Total reviews' value={s.total_reviews} />
        <StatCard label='Positive' value={s.positive_pct + '%'} sub={s.positive + ' reviews'} />
        <StatCard label='Negative' value={s.negative_pct + '%'} sub={s.negative + ' reviews'} />
        <StatCard label='Neutral' value={s.neutral_pct + '%'} sub={s.neutral + ' reviews'} />
      </div>
      <div className='grid'>
        <Panel title='Sentiment'><SentimentDonut data={split} /></Panel>
        <Panel title='Emotions'><EmotionBars data={p.emotions} /></Panel>
        <Panel title='Reviews per month'><MonthlyReviews data={p.monthly} /></Panel>
        <Panel title='Positive vs negative %'><MonthlySentiment data={p.monthly} /></Panel>
        <Panel title='Common positive feedback'>{list(p.common_positive_feedback)}</Panel>
        <Panel title='Common complaints'>{list(p.common_complaints)}</Panel>
      </div>
      <Panel title='Recent reviews'>
        {p.recent_reviews.map((r) => (
          <p key={r.review_id}><b>{r.sentiment}/{r.emotion}</b> ({r.review_date}): {r.review_text}</p>
        ))}
      </Panel>
    </>
  );
}
