import React, { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

export const Jobs: React.FC = () => {
  const [pdfUrl, setPdfUrl] = useState<string>('');
  const [summary, setSummary] = useState<string>('');
  const [jobs, setJobs] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('your_route/find', { pdf_path: pdfUrl });

      // Set summary and jobs from the response data
      setSummary(response.data.summary);
      setJobs(response.data.jobs);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred while processing the PDF');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-lg mx-auto p-6 bg-white rounded-lg shadow-lg">
      <h2 className="text-2xl font-semibold mb-4">Upload PDF URL</h2>

      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label htmlFor="pdfUrl" className="block text-lg font-medium text-gray-700">PDF URL:</label>
          <input
            type="url"
            id="pdfUrl"
            value={pdfUrl}
            onChange={(e) => setPdfUrl(e.target.value)}
            className="mt-2 p-2 w-full border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-400"
            required
          />
        </div>

        <button
          type="submit"
          className={`w-full py-2 px-4 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:outline-none ${loading && 'opacity-50 cursor-not-allowed'}`}
          disabled={loading}
        >
          {loading ? 'Processing...' : 'Submit'}
        </button>
      </form>

      {error && <div className="mt-4 text-red-500">{error}</div>}

      {summary && (
        <div className="mt-6">
          <h3 className="text-xl font-semibold">Summary</h3>
          <div className="mt-2 text-gray-700">
            <ReactMarkdown>{summary}</ReactMarkdown>
          </div>
        </div>
      )}

      {jobs && (
        <div className="mt-6">
          <h3 className="text-xl font-semibold">Jobs</h3>
          <div className="mt-2 text-gray-700">
            <ReactMarkdown>{jobs}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
};
