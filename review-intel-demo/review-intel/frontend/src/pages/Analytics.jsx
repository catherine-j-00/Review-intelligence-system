import FilterBar from '../components/FilterBar';
import Panel from '../components/Panel';
import { SentimentDonut, EmotionBars } from '../components/Charts';
import { useFilters } from '../context/FilterContext';
import { useData } from '../hooks/useData';
import { getSentiments, getEmotions } from '../services/api';

export default function Analytics() {
  const { params } = useFilters();
  const key = JSON.stringify(params);
  const s = useData(() => getSentiments(params), [key]);
  const e = useData(() => getEmotions(params), [key]);
  return (
    <>
      <h1>Analytics</h1>
      <FilterBar />
      <p className='note'>Sentiment is derived from emotion by a mapping table. They are related but not the same thing.</p>
      <div className='grid'>
        <Panel title='Sentiment'><SentimentDonut data={s.data} /></Panel>
        <Panel title='Emotion'><EmotionBars data={e.data} /></Panel>
      </div>
      <Panel title='Emotion table'>
        <table><tbody>{(e.data || []).map((x) => (
          <tr key={x.label}><td>{x.label}</td><td>{x.count}</td><td>{x.pct}%</td></tr>))}</tbody></table>
      </Panel>
    </>
  );
}
