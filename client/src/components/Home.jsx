import { useState, useRef } from 'react';
import axios from 'axios';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import { useNavigate } from 'react-router-dom'; // Import useNavigate for navigation

const Home = () => {
  const [translatedText, setTranslatedText] = useState("");
  const [loadingTranslation, setLoadingTranslation] = useState(false);
  const [loadingKeywords, setLoadingKeywords] = useState(false);
  const [posTags, setPosTags] = useState([]);
  const [keywords, setKeywords] = useState([]);
  const Textref = useRef(null);
  const navigate = useNavigate(); // Hook for navigation

  // Translation handler
  const translateText = async () => {
    const inputText = Textref.current.value;

    if (!inputText.trim()) {
      toast.error('Please enter text to translate.', { position: 'top-center', autoClose: 3000 });
      return;
    }

    setLoadingTranslation(true);

    try {
      const response = await axios.post('http://127.0.0.1:5000/api2/translate', { text: inputText });
      const translated = response.data.translated_text;

      setTranslatedText(translated);

      toast.success('Translation done!', { position: 'top-center', autoClose: 3000 });
    } catch (error) {
      console.error('Error during translation:', error);
      toast.error('Failed to translate. Please try again later.');
    } finally {
      setLoadingTranslation(false);
    }
  };

  // Handler for POS tagging
  const fetchPartsOfSpeech = async () => {
    const inputText = Textref.current.value;

    if (!inputText.trim()) {
      toast.error('Please enter text to perform POS tagging.', { position: 'top-center', autoClose: 3000 });
      return;
    }

    setLoadingTranslation(true);

    try {
      const response = await axios.post('http://127.0.0.1:5000/api2/pos', { text: inputText });
      setPosTags(response.data);

      toast.success('POS tagging completed!', { position: 'top-center', autoClose: 3000 });
    } catch (error) {
      console.error('Error during POS tagging:', error);
      toast.error('Failed to perform POS tagging. Please try again later.');
    } finally {
      setLoadingTranslation(false);
    }
  };

  // Handler for translating keywords
  const translateKeywords = async () => {
    const inputText = Textref.current.value;

    if (!inputText.trim()) {
      toast.error('Please enter text to extract and translate keywords.', {
        position: 'top-center',
        autoClose: 3000,
      });
      return;
    }

    setLoadingKeywords(true);

    try {
      const response = await axios.post('http://127.0.0.1:5000/api2/translate_keywords', { text: inputText });
      setKeywords(response.data.keywords);

      toast.success('Keywords translated successfully!', { position: 'top-center', autoClose: 3000 });
    } catch (error) {
      console.error('Error during keyword translation:', error);
      toast.error('Failed to translate keywords. Please try again later.');
    } finally {
      setLoadingKeywords(false);
    }
  };

  // Handler to navigate to the audio processing page using useNavigate
  const goToAudioPage = () => {
    navigate('/audio-text-processing'); // Navigates to the '/audio' route
  };

  return (
    <div className="w-full border-black border-2 rounded-lg p-6">
      <ToastContainer />
      <h1 className="text-xl font-bold text-center mb-4">Text Processing</h1>

      <div className="flex justify-between mb-4 p-4">
        <div>English</div>
        <div>Telugu</div>
      </div>

      <div className="flex w-full gap-4">
        <div className="flex-1">
          <label className="block mb-2 font-medium">Input Text</label>
          <textarea
            ref={Textref}
            spellCheck
            className="w-full h-[60vh] border rounded-lg p-4"
            placeholder="Enter text here (up to 400 characters)"
          />
        </div>

        <div className="flex-1">
          <label className="block mb-2 font-medium">Translated Text</label>
          <textarea
            value={translatedText}
            className="w-full h-[60vh] border rounded-lg p-4"
            placeholder="Translation will appear here"
            readOnly
          />
        </div>
      </div>
      <div  className=' flex gap-10'>
      <div className="w-full flex justify-center mt-4">
        <button
          className={`border-2 px-8 py-2 rounded-full mt-2 transition-colors ${
            loadingTranslation ? 'bg-gray-300 cursor-not-allowed' : 'bg-blue-300 hover:bg-blue-400 cursor-pointer'
          }`}
          onClick={translateText}
          disabled={loadingTranslation || loadingKeywords}
        >
          {loadingTranslation ? 'Translating...' : 'Translate'}
        </button>
      </div>

      <div className="w-full flex justify-center mt-4">
        <button
          className={`border-2 px-8 py-2 rounded-full mt-2 transition-colors ${
            loadingTranslation ? 'bg-gray-300 cursor-not-allowed' : 'bg-green-300 hover:bg-green-400 cursor-pointer'
          }`}
          onClick={fetchPartsOfSpeech}
          disabled={loadingTranslation || loadingKeywords}
        >
          POS Tagging
        </button>
      </div>

      <div className="w-full flex justify-center mt-4">
        <button
          className={`border-2 px-8 py-2 rounded-full mt-2 transition-colors ${
            loadingKeywords ? 'bg-gray-300 cursor-not-allowed' : 'bg-purple-300 hover:bg-purple-400 cursor-pointer'
          }`}
          onClick={translateKeywords}
          disabled={loadingKeywords || loadingTranslation}
        >
          {loadingKeywords ? 'Translating Keywords...' : 'Translate Keywords'}
        </button>
      </div>
      {/* Button to go to the audio processing page */}
      <div className="w-full flex justify-center mt-4">
        <button
          className="border-2 px-8 py-2 rounded-full mt-2 transition-colors bg-yellow-300 hover:bg-yellow-400 cursor-pointer"
          onClick={goToAudioPage}
        >
          Go to Audio Processing
        </button>
      </div>
      </div>
      {/* Display POS Tags and Translated Keywords (Similar to Original Code) */}
      <div className="mt-4">
        <h2 className="text-lg font-bold">Parts of Speech:</h2>
        {posTags.length > 0 ? (
          <table className="w-full border-collapse border border-gray-300">
            <thead>
              <tr className="bg-blue-200">
                <th className="border border-black p-2">Token</th>
                <th className="border border-black p-2">POS</th>
              </tr>
            </thead>
            <tbody>
              {posTags.map((item, index) => (
                <tr key={index}>
                  <td className="border border-black p-2">{item.token}</td>
                  <td className="border border-black p-2">{item.pos}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>No POS tags available. Translate to see the results.</p>
        )}
      </div>

      <div className="mt-4">
        <h2 className="text-lg font-bold">Translated Keywords with Scores:</h2>
        {keywords.length > 0 ? (
          <table className="w-full border-collapse border border-gray-300">
            <thead>
              <tr className="bg-blue-200">
                <th className="border border-black p-2">Translated Keyword (Telugu)</th>
                <th className="border border-black p-2">TF-IDF Score</th>
              </tr>
            </thead>
            <tbody>
              {keywords.map((item, index) => (
                <tr key={index}>
                  <td className="border border-black p-2">{item.translated_keyword}</td>
                  <td className="border border-black p-2">{item.score.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p>Extract and translate keywords to see results here.</p>
        )}
      </div>
    </div>
  );
};

export default Home;
