import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Modal from 'react-modal';
import axios from 'axios';
import useTypewriter from './hooks/useTypewriter'; 
import ComparisonModal from './components/ComparisonModal'; 
import { XMarkIcon } from '@heroicons/react/24/solid';
import 'bootstrap-icons/font/bootstrap-icons.css';
import './App.css';

Modal.setAppElement('#root');

// --- Reusable UI Sub-Components ---
const TypingIndicator = () => (<motion.div className="message ai-message typing-indicator"><div className="dot"></div><div className="dot"></div><div className="dot"></div></motion.div>);
const UserMessage = ({ text }) => (<motion.div className="message user-message"><p>{text}</p></motion.div>);
const AiMessage = ({ text }) => (<motion.div className="message ai-message"><p>{useTypewriter(text)}</p></motion.div>);

const PatentCard = React.memo(({ patent, onCompare }) => (
    <motion.div initial={{ y: 20, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="message ai-message patent-card">
        <h4>{patent.title}</h4>
        
        {/* FIX: Abstract is restored for context */}
        <p className="patent-abstract">{patent.abstract.substring(0, 200)}...</p>

        <div className="patent-actions">
            <p className="patent-id">Relevance: <strong>{patent.score.toFixed(3)}</strong></p>
            {/* FIX: Button is fully restored and functional */}
            <button onClick={() => onCompare(patent)}>Compare My Idea</button>
        </div>
    </motion.div>
));

const AppHeader = ({ onInfoClick }) => (
    <header className="app-header">
        <div className="logo"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 2L2 7V17L12 22L22 17V7L12 2Z" stroke="var(--accent)" strokeWidth="2" strokeLinejoin="round"/><path d="M2 7L12 12" stroke="var(--accent)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/><path d="M12 22V12" stroke="var(--accent)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/><path d="M22 7L12 12" stroke="var(--accent-light-2)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/><path d="M17 4.5L7 9.5" stroke="var(--accent-light-2)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg><span>PatentAI Analyst</span></div>
        <button className="info-button" title="About this Project" onClick={onInfoClick}><i className="bi bi-info-circle-fill"></i></button>
    </header>
);

const InfoModal = ({ isOpen, onClose }) => {
    // This component logic is correct and remains unchanged.
    return (
        <Modal isOpen={isOpen} onRequestClose={onClose} className="info-modal" overlayClassName="modal-overlay" closeTimeoutMS={300}>
            <div className="info-modal-header"><h2>About PatentAI Analyst</h2><button onClick={onClose} className="modal-close-button"><XMarkIcon /></button></div>
            <div className="info-modal-content">
                <p><strong>PatentAI Analyst</strong> is a free tool using AI to help assess the novelty of an idea against existing patents.</p>
                <h4>Technology Used</h4>
                <div className="tech-stack-grid">
                    <div className="tech-item"><i className="bi bi-robot"></i><h5>Local AI Models</h5><p>Embeddings are generated locally using Sentence-Transformers for fast, free, and private semantic search.</p></div>
                    <div className="tech-item"><i className="bi bi-database-check"></i><h5>MongoDB Atlas</h5><p>Atlas is our core vector database. Vector Search finds conceptually similar patents in milliseconds.</p></div>
                    <div className="tech-item"><i className="bi bi-code-slash"></i><h5>Modern Frontend</h5><p>Built with React & Framer Motion for a fluid, intuitive conversational experience.</p></div>
                </div>
            </div>
        </Modal>
    );
};

// --- Main App Component ---
function App() {
    const [viewMode, setViewMode] = useState('initial');
    const [userInput, setUserInput] = useState('');
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [userIdea, setUserIdea] = useState('');
    const [modalData, setModalData] = useState(null);
    const [isInfoModalOpen, setIsInfoModalOpen] = useState(false);
    const chatAreaRef = useRef(null);

    useEffect(() => {
        if (chatAreaRef.current) {
            chatAreaRef.current.scrollTo({ top: chatAreaRef.current.scrollHeight, behavior: 'smooth' });
        }
    }, [messages, isLoading]);

    const handleSearch = useCallback(async (ideaText) => {
        if (ideaText.trim().split(/\s+/).length < 10 || isLoading) return;
        setUserIdea(ideaText);
        setMessages([{ type: 'user', content: ideaText }]);
        setViewMode('chat');
        setIsLoading(true);
        try {
            const res = await axios.post('http://localhost:8000/api/find-similar', { idea_text: ideaText });
            const patents = res.data.matched_patents;
            const newMessages = patents.length > 0
                ? [{ type: 'ai', content: "Based on your idea, I've found these conceptually similar patents:" }, ...patents.map(p => ({ type: 'patent', content: p }))]
                : [{ type: 'ai', content: "No highly relevant patents were found from the database. This may indicate strong novelty." }];
            setMessages(prev => [...prev, ...newMessages]);
        } catch (error) {
            setMessages(prev => [...prev, { type: 'ai', content: 'My apologies, an error occurred during the patent search.' }]);
        } finally {
            setIsLoading(false);
        }
    }, [isLoading]);

    const handleSubmit = (e) => { e.preventDefault(); handleSearch(userInput); };

    return (
        <div className="app-layout">
            <AppHeader onInfoClick={() => setIsInfoModalOpen(true)} />
            <main className={`chat-area ${viewMode === 'initial' ? 'is-initial' : ''}`} ref={chatAreaRef}>
                {viewMode === 'initial' && <div className="initial-content-wrapper"><div className="pill-header"><i className="bi bi-shield-check"></i><span>Analyze Idea Novelty</span></div><h1 className="main-heading">From Idea to Insight.<br/>Instantly.</h1></div>}
                <div className="chat-log">
                    <AnimatePresence>
                        {messages.map((msg, index) => {
                            const key = `${msg.type}-${index}-${msg.content?.publication_number || ''}`;
                            switch(msg.type) {
                                case 'user': return <UserMessage key={key} text={msg.content} />;
                                case 'ai': return <AiMessage key={key} text={msg.content} />;
                                case 'patent': return <PatentCard key={key} patent={msg.content} onCompare={(patent) => setModalData({ userIdea, patent })} />;
                                default: return null;
                            }
                        })}
                    </AnimatePresence>
                    {isLoading && <TypingIndicator />}
                </div>
            </main>
            <footer className={`input-area-wrapper ${viewMode === 'initial' ? 'is-initial-view' : ''}`}>
                <div className="main-input-container">
                    <form onSubmit={handleSubmit}>
                        <textarea value={userInput} onChange={(e) => setUserInput(e.target.value)} placeholder="Describe your invention in detail (e.g., a smart coffee mug that maintains a perfect temperature)..." />
                        <div className="input-actions"><button type="submit" className="analyze-button" disabled={isLoading || userInput.trim().split(/\s+/).length < 10}>Analyze</button></div>
                    </form>
                </div>
            </footer>
            <ComparisonModal modalData={modalData} closeModal={() => setModalData(null)} />
            <InfoModal isOpen={isInfoModalOpen} onClose={() => setIsInfoModalOpen(false)} />
        </div>
    );
}
export default App;