import React from 'react';

const QuickSuggestions = ({ onSelect, disabled }) => {
  const suggestions = [
    "Overall metrics summary",
    "Show bar chart",
    "Sales distribution pie",
    "Top 10 categories",
    "Trend analysis"
  ];

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
