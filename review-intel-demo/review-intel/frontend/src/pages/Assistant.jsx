import { useState } from 'react';
import { askAssistant } from '../services/api';

export default function Assistant() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);

  const send = async () => {
    const question = input.trim();
    if (!question || busy) return;
    const history = messages.slice(-6);
    setMessages([...messages, { role: 'user', content: question }]);
    setInput(''); setBusy(true);
    try {
      const { answer } = await askAssistant(question, history);
      setMessages((m) => [...m, { role: 'assistant', content: answer }]);
    } catch (e) {
      const err = (e.response && e.response.data && e.response.data.error) || 'Assistant failed';
      setMessages((m) => [...m, { role: 'assistant', content: err }]);
    }
    setBusy(false);
  };

  return (
    <>
      <h1>AI Assistant</h1>
      <p className='note'>Answers come only from your review data. These are review statistics, not sales.</p>
      <div className='panel'>
        <div className='chat-log'>
          {messages.map((m, i) => <div key={i} className={'bubble ' + m.role}>{m.content}</div>)}
          {busy && <p className='note'>Thinking...</p>}
        </div>
        <input style={{ width: '75%' }} value={input} placeholder='Which lipstick has the most positive reviews?'
          onChange={(e) => setInput(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && send()} />{' '}
        <button onClick={send}>Ask</button>
      </div>
    </>
  );
}
