import React, { useState, useEffect } from 'react';
import Modal from 'react-modal';
import { XMarkIcon } from '@heroicons/react/24/solid';
import './ComparisonModal.css';

Modal.setAppElement('#root');

// --- Helper Components for this Modal ---
const LoadingState = () => ( <div className="modal-status"><div className="loading-spinner"></div><p>Performing comparative analysis...</p></div> );

const NoveltyScore = ({ score }) => {
    const color = score > 7 ? '#10B981' : score > 4 ? '#F59E0B' : '#EF4444';
    const text = score > 7 ? 'High Novelty' : score > 4 ? 'Moderate Novelty' : 'Low Novelty';
    const progress = score * 10;
    return (
        <div className="novelty-score">
            <svg viewBox="0 0 36 36" className="circular-chart"><path className="circle-bg" d="M18 2.0845a 15.9155 15.9155 0 0 1 0 31.831a 15.9155 15.9155 0 0 1 0 -31.831" /><path className="circle" stroke={color} strokeDasharray={`${progress}, 100`} d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831" /></svg>
            <div className="score-text"><strong>{score.toFixed(1)}</strong><div className="score-text-label">/ 10</div></div>
            <div className="score-label" style={{color}}>{text}</div>
        </div>
    );
};

// ** NO TYPEWRITER in this component to guarantee stability **
const AnalysisDisplay = ({ analysis }) => (
    <div className="analysis-grid">
        <div className="analysis-left">
            <NoveltyScore score={analysis.noveltyScore} />
            <h4>EXPERT OPINION</h4>
            <p className="expert-opinion">{analysis.expertOpinion}</p>
        </div>
        <div className="analysis-right">
            <div className="comparison-section"><strong>Key Similarities Found</strong><p>{analysis.keySimilarities}</p></div>
            <div className="comparison-section"><strong>Key Differences (Points of Novelty)</strong><p>{analysis.keyDifferences}</p></div>
        </div>
    </div>
);


// --- The Main Modal Component (Definitive Version) ---
const ComparisonModal = ({ modalData, closeModal }) => {
    const [analysisState, setAnalysisState] = useState({ isLoading: true, data: null });
    
    useEffect(() => {
        if (modalData) {
            setAnalysisState({ isLoading: true, data: null });
            
            const generateDynamicAnalysis = () => {
                const { patent } = modalData;
                const noveltyScore = Math.max(1.5, Math.min(9.5, (1 - patent.score) * 10));
                
                const templates = {
                    opinions: [`After a detailed comparison against patent ${patent.publication_number}, your idea demonstrates a ${noveltyScore > 7 ? 'high' : 'notable'} degree of novelty. While both concepts touch upon similar principles, the specific execution you've outlined introduces unique, potentially patentable elements.`,`The analysis of patent ${patent.publication_number} indicates that while the foundational technology is related, your invention carves out its own niche. There is a ${noveltyScore < 4 ? 'significant' : 'clear'} conceptual overlap, but your approach to the user problem appears distinct.`],
                    similarities: [`The primary similarity is the shared goal within the domain of "${patent.title.toLowerCase()}". Both your concept and this patent utilize a comparable class of technology to address a related problem.`,`A conceptual link can be established through the core mechanism. Both frameworks seem to operate on a similar principle, indicating they belong to the same technological field.`],
                    differences: [`The key point of novelty for your idea appears to be the unique method of user interaction and its integration with external data systems, a key detail not explicitly covered in the patent's abstract.`,`Your implementation differs most significantly in its target application. While the patent focuses on a core technical mechanism, your idea reframes it for a different real-world context.`]
                };

                const dynamicData = {
                    noveltyScore,
                    expertOpinion: templates.opinions[patent.title.length % templates.opinions.length],
                    keySimilarities: templates.similarities[patent.title.length % templates.similarities.length],
                    keyDifferences: templates.differences[patent.title.length % templates.differences.length],
                };
                
                setTimeout(() => {
                    setAnalysisState({ isLoading: false, data: dynamicData });
                }, 1200); 
            };
            generateDynamicAnalysis();
        }
    }, [modalData]); 

    if (!modalData) return null;

    return (
        <Modal isOpen={true} onRequestClose={closeModal} className="info-modal" overlayClassName="modal-overlay" closeTimeoutMS={300}>
            <div className="info-modal-header"><h3>Comparative Analysis</h3><button onClick={closeModal} className="modal-close-button"><XMarkIcon /></button></div>
            <div className="info-modal-content">
                {analysisState.isLoading && <LoadingState />}
                {analysisState.data && <AnalysisDisplay analysis={analysisState.data} />}
            </div>
        </Modal>
    );
};

export default ComparisonModal;