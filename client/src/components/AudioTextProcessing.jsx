import React, { useState } from 'react';
import axios from 'axios';
import { Pie } from 'react-chartjs-2';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';

// Registering required Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend);

function UnifiedProcessing() {
  const [file, setFile] = useState(null);
  const [response, setResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false); // State to track loading status
  const [translatedResponse, setTranslatedResponse] = useState(null); // Store translated response
  const [isEnglishToTelugu, setIsEnglishToTelugu] = useState(true); // Toggle state for translation direction

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleFileSubmit = async () => {
    const formData = new FormData();
    formData.append('file', file);

    setIsLoading(true); // Start loading animation

    try {
      const res = await axios.post('http://localhost:5000/api1/process_audio', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setResponse(res.data);
    } catch (error) {
      console.error('Error processing audio:', error);
    } finally {
      setIsLoading(false); // End loading animation
    }
  };

  // Function to format data for the pie chart
  const formatSentimentData = (sentiments) => {
    const sentimentLabels = [
      'Joy',
      'Anger',
      'Sadness',
      'Fear',
      'Neutral',
      'Surprise',
      'Disgust',
      'Love',
    ];
    const sentimentScores = sentimentLabels.map((label) => sentiments[label.toLowerCase()] || 0);

    return {
      labels: sentimentLabels,
      datasets: [
        {
          data: sentimentScores,
          backgroundColor: [
            '#ffcc00',
            '#ff6666',
            '#6699ff',
            '#ff9966',
            '#cccccc',
            '#99cc33',
            '#ff3333',
            '#ff66cc',
          ],
        },
      ],
    };
  };

  // Function to translate transcript and summary
  const translateText = async () => {
    if (response && response.transcript && response.summary) {
      const data = {
        text1: response.transcript,
        text2: response.summary,
        direction: isEnglishToTelugu ? 'en-to-te' : 'te-to-en', // Toggle translation direction
      };

      setIsLoading(true); // Start loading animation

      try {
        const res = await axios.post('http://localhost:5000/api2/translate_multiple', data);
        setTranslatedResponse(res.data); // Set translated response
      } catch (error) {
        console.error('Error translating text:', error);
      } finally {
        setIsLoading(false); // End loading animation
      }
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-semibold text-center">Audio Processing</h1>

      <div className="mt-4 flex justify-center items-center">
        <input
          type="file"
          onChange={handleFileChange}
          className="mt-4"
        />
        <button
          onClick={handleFileSubmit}
          className="bg-blue-500 text-white py-2 px-4 rounded mt-4 ml-4"
        >
          Process Audio
        </button>
      </div>

      {/* Loading animation (centered) */}
      {isLoading ? (
        <div className="flex justify-center items-center mt-4">
          <div className="relative w-16 h-16 border-4 border-t-4 border-blue-500 rounded-full animate-spin"></div>
          <div className="absolute w-8 h-8 bg-blue-500 rounded-full animate-bounce top-0 left-1/2 transform -translate-x-1/2"></div>
        </div>
      ) : (
        response && (
          <div className="mt-4 grid grid-cols-3 gap-4">
            {/* Left: Mood Chart */}
            <div className="col-span-1">
              {response.sentiments && (
                <div>
                  <h3 className="font-semibold">Mood Analysis (Pie Chart):</h3>
                  <Pie className="w-full h-64" data={formatSentimentData(response.sentiments)} />
                  <p><strong>Overall Sentiment:</strong> {response.overall_sentiment}</p>
                </div>
              )}
            </div>

            {/* Center: Text response */}
            
            <div className="col-span-2">
              <h2 className="font-semibold">Response:</h2>
              {translatedResponse ? (
                <div>
                  <p><strong>{isEnglishToTelugu ? 'Translated Transcript' : 'Translated Transcript (English)'}:</strong> {translatedResponse.translated_text1}</p>
                  <p><strong>{isEnglishToTelugu ? 'Translated Summary' : 'Translated Summary (English)'}:</strong> {translatedResponse.translated_text2}</p>
                </div>
              ) : (
                <>
                  {response.transcript && (
                    <div>
                      <p><strong>Transcript:</strong> {response.transcript}</p>
                    </div>
                  )}
                  {response.summary && (
                    <div>
                      <p><strong>Summary:</strong> {response.summary}</p>
                    </div>
                  )}
                  {/* Translate button */}
                  <button
                    onClick={translateText}
                    className="bg-green-500 text-white py-2 px-4 rounded mt-4"
                  >
                    Translate to {isEnglishToTelugu ? 'Telugu' : 'English'}
                  </button>
                </>
              )}
            </div>
          </div>
        )
      )}
    </div>
  );
}

export default UnifiedProcessing;
