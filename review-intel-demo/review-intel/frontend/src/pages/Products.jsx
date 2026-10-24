import FilterBar from '../components/FilterBar';
import Panel from '../components/Panel';
import RankTable from '../components/RankTable';
import { useFilters } from '../context/FilterContext';
import { useData } from '../hooks/useData';
import { getProductRankings } from '../services/api';

export default function Products() {
  const { params } = useFilters();
  const key = JSON.stringify(params);
  const ranks = useData(() => getProductRankings({ ...params, limit: 50 }), [key]);
  return (
    <>
      <h1>Products</h1>
      <FilterBar />
      <Panel title='Products by number of reviews (not sales)'>
        <RankTable rows={ranks.data && ranks.data.most_reviewed} />
      </Panel>
    </>
  );
}
