import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Translator from './components/Home'; // Import the Translator component
import AudioTextProcessing from './components/AudioTextProcessing'; // Import the AudioTextProcessing component

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Translator />} /> {/* Home route for Translator */}
        <Route path="/audio-text-processing" element={<AudioTextProcessing />} /> {/* New route for AudioTextProcessing */}
      </Routes>
    </Router>
  );
}

export default App;
