import { useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";

function App() {
  const [inputValue, setInputValue] = useState("");
  const [story, setStory] = useState("");
  const [scene, setScene] = useState("");
  const [image, setImage] = useState("");
  const [loading, setLoading] = useState(false);
  const [imageLoading, setImageLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Handle input change
  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInputValue(event.target.value);
  };

  // Generate Horror Story & Scene
  const handleGenerateStory = async () => {
    setLoading(true);
    setError(null);
    setScene("");
    setStory("");

    try {
      const response = await axios.post("http://localhost:8000/generate-horror-story", {
        scene_prompt: `Describe a terrifying moment about ${inputValue} in 50 words.`,
        story_prompt: `Tell a 250-word horror story about ${inputValue}.`
      });

      if (response.data.scene && response.data.story) {
        setScene(response.data.scene);
        setStory(response.data.story);
      } else {
        throw new Error("Invalid response from server");
      }
    } catch (err) {
      setError("Error generating story");
    } finally {
      setLoading(false);
    }
  };

  
  
  
  
  

  // Generate Image from Story
  const handleGenerateImage = async () => {
    if (!story) return;
    setImageLoading(true);
    setError(null);

    try {
      const response = await axios.post("https://url/generate", { prompt: scene });
      if (response.data.image_base64) {
        console.log("Generated Image URL:", response.data.image_url);
        const imageSrc = `data:image/png;base64,${response.data.image_base64}`;
        setImage(imageSrc);
      } else {
        throw new Error("Invalid response from server");
      }
    } catch (err) {
      console.error("Error generating image:", err);
      setError("Image generation failed.");
    } finally {
      setImageLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <h1 className="text-3xl font-extrabold text-center text-gray-900">AI-Generated Horror Story</h1>

        <div className="mt-8 space-y-6">
          <div className="rounded-md shadow-sm space-y-4">
            <label htmlFor="input" className="block text-lg font-medium text-gray-700">
              Enter a horror story topic
            </label>
            <input
              id="input"
              name="input"
              type="text"
              value={inputValue}
              onChange={handleInputChange}
              placeholder="e.g., Haunted House, Ghost, Creepy Forest"
              className="w-full px-4 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
            />
          </div>

          <div>
          <button
            type="button"
            onClick={handleGenerateStory}
            className="mt-4 py-2 px-4 border border-transparent rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
            disabled={loading}>
              {loading ? "Generating..." : "Generate Horror Story"}
            </button>
          </div>
        </div>

        {error && <p className="text-red-500 text-center">{error}</p>}

        {scene && (
          <div className="mt-8 bg-white shadow-lg rounded-lg p-6">
            <h3 className="text-xl font-semibold text-gray-900">Terrifying Scene:</h3>
            <ReactMarkdown className="mt-2 text-gray-700">{scene}</ReactMarkdown>
          </div>
        )}

        {story && (
          <div className="mt-8 bg-white shadow-lg rounded-lg p-6">
            <h3 className="text-2xl font-semibold text-gray-900">Story:</h3>
            <ReactMarkdown className="mt-4 text-gray-700">{story}</ReactMarkdown>
            <button
              onClick={handleGenerateImage}
              className="mt-4 py-2 px-4 border border-transparent rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              disabled={imageLoading}
            >
              {imageLoading ? "Creating Image..." : "Create Image"}
            </button>
            {image && <img src={image} alt="Generated Scene" className="mt-4 rounded-lg shadow-lg" />}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
