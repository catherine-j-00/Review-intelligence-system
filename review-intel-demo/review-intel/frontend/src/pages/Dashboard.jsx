import FilterBar from '../components/FilterBar';
import StatCard from '../components/StatCard';
import Panel from '../components/Panel';
import RankTable from '../components/RankTable';
import { SentimentDonut, EmotionBars, MonthlyReviews } from '../components/Charts';
import { useFilters } from '../context/FilterContext';
import { useData } from '../hooks/useData';
import { getOverview, getSentiments, getEmotions, getMonthly, getProductRankings } from '../services/api';

export default function Dashboard() {
  const { params } = useFilters();
  const key = JSON.stringify(params); // re-fetch whenever filters change
  const overview = useData(() => getOverview(params), [key]);
  const sentiments = useData(() => getSentiments(params), [key]);
  const emotions = useData(() => getEmotions(params), [key]);
  const monthly = useData(() => getMonthly(params), [key]);
  const ranks = useData(() => getProductRankings(params), [key]);
  const o = overview.data;
  const r = ranks.data;

  return (
    <>
      <h1>Dashboard</h1>
      <FilterBar />
      {overview.error && <p className='note'>{overview.error}</p>}
      {o && (
        <div className='cards'>
          <StatCard label='Total reviews' value={o.total_reviews} />
          <StatCard label='Positive' value={o.positive} sub={o.positive_pct + '%'} />
          <StatCard label='Negative' value={o.negative} sub={o.negative_pct + '%'} />
          <StatCard label='Neutral' value={o.neutral} sub={o.neutral_pct + '%'} />
          <StatCard label='Products' value={o.products} />
          <StatCard label='Brands' value={o.brands} />
        </div>
      )}
      <p className='note'>All figures are review counts, not sales.</p>
      <div className='grid'>
        <Panel title='Sentiment split'><SentimentDonut data={sentiments.data} /></Panel>
        <Panel title='Emotion distribution'><EmotionBars data={emotions.data} /></Panel>
        <Panel title='Reviews per month'><MonthlyReviews data={monthly.data} /></Panel>
      </div>
      {r && (
        <div className='grid'>
          <Panel title='Most reviewed products'><RankTable rows={r.most_reviewed} /></Panel>
          <Panel title={'Highest positive % (at least ' + r.min_reviews_for_ranking + ' reviews)'}>
            <RankTable rows={r.highest_positive_pct} /></Panel>
          <Panel title={'Highest negative % (at least ' + r.min_reviews_for_ranking + ' reviews)'}>
            <RankTable rows={r.highest_negative_pct} /></Panel>
        </div>
      )}
    </>
  );
}
