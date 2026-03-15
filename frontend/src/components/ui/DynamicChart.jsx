import React, { useRef, useEffect } from 'react';
import Plotly from 'plotly.js-dist-min';

const DynamicChart = ({ data, type, title }) => {
  const chartRef = useRef(null);

  useEffect(() => {
    if (!data || data.length === 0 || !chartRef.current) return;

    let plotData = [];
    let layout = {
      title: { 
        text: title, 
        font: { size: 13, color: 'rgba(255,255,255,0.7)', family: 'Inter' },
        x: 0,
        y: 0.95
      },
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      font: { color: '#f8fafc', family: 'Inter' },
      margin: { t: 60, b: 40, l: 40, r: 20 },
      xaxis: { 
        gridcolor: 'rgba(255,255,255,0.03)',
        tickfont: { size: 10, color: 'rgba(255,255,255,0.4)' },
        linecolor: 'rgba(255,255,255,0.1)'
      },
      yaxis: { 
        gridcolor: 'rgba(255,255,255,0.03)',
        tickfont: { size: 10, color: 'rgba(255,255,255,0.4)' },
        linecolor: 'rgba(255,255,255,0.1)'
      },
      showlegend: type === 'pie',
      legend: { font: { size: 10, color: '#f8fafc' }, bgcolor: 'transparent' }
    };

    const labels = data.map(d => Object.values(d)[0]);
    const values = data.map(d => Object.values(d)[1]);

    if (type === 'bar') {
      plotData = [{
        x: labels,
        y: values,
        type: 'bar',
        marker: { 
          color: '#6366f1',
          line: { color: '#818cf8', width: 1 }
        }
      }];
    } else if (type === 'pie') {
      plotData = [{
        labels: labels,
        values: values,
        type: 'pie',
        marker: { colors: ['#6366f1', '#10b981', '#f59e0b', '#3b82f6', '#ec4899', '#8b5cf6'] },
        hole: 0.5,
        textinfo: 'percent',
        insidetextorientation: 'radial'
      }];
    } else if (type === 'line' || type === 'area') {
      plotData = [{
        x: labels,
        y: values,
        type: 'scatter',
        mode: 'lines',
        fill: type === 'area' ? 'tozeroy' : 'none',
        line: { color: '#818cf8', width: 3, shape: 'spline' },
        fillcolor: 'rgba(129, 140, 248, 0.1)'
      }];
    } else if (type === 'scatter') {
      plotData = [{
        x: labels,
        y: values,
        mode: 'markers',
        type: 'scatter',
        marker: { 
          color: '#f59e0b', 
          size: 10,
          line: { color: '#ffffff', width: 1 },
          opacity: 0.8
        }
      }];
    }

    Plotly.newPlot(chartRef.current, plotData, layout, { 
      responsive: true, 
      displayModeBar: false,
      staticPlot: false
    });
  }, [data, type, title]);

  return <div ref={chartRef} className="w-full h-full min-h-[300px]" />;
};

export default DynamicChart;
