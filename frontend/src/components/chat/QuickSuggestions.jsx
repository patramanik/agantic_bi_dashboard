import React from 'react';

const QuickSuggestions = ({ onSelect, disabled, suggestions }) => {
  if (!suggestions || !Array.isArray(suggestions) || suggestions.length === 0) {
    return null;
  }

  return (
    <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-none no-scrollbar">
      {suggestions.map((s, i) => (
        <button 
          key={i} 
          onClick={() => onSelect(s)}
          disabled={disabled}
          className="suggestion-pill"
        >
          {s}
        </button>
      ))}
    </div>
  );
};

export default QuickSuggestions;
