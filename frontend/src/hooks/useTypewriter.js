import { useState, useEffect } from 'react';

const useTypewriter = (text, speed = 20) => {
    const [displayText, setDisplayText] = useState('');

    useEffect(() => {
        setDisplayText('');
        if (text) {
            let i = 0;
            const timer = setInterval(() => {
                if (i < text.length) {
                    setDisplayText(prev => prev + text.charAt(i));
                    i++;
                } else {
                    clearInterval(timer);
                }
            }, speed);
            return () => clearInterval(timer);
        }
    }, [text, speed]);

    return displayText;
};

export default useTypewriter;