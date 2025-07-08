import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  DocumentArrowUpIcon, 
  MagnifyingGlassIcon, 
  DocumentTextIcon,
  ChatBubbleLeftRightIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ChartBarIcon,
  ClockIcon,
  DocumentMagnifyingGlassIcon,
  CogIcon
} from '@heroicons/react/24/outline';

const API_BASE_URL = 'http://localhost:8000/api/v1';

interface Document {
  id: number;
  title: string;
  document_type: string;
  created_at: string;
  file_size?: number;
  word_count?: number;
  processed_chunks?: number;
}

interface QueryResponse {
  answer: string;
  relevant_documents: Array<{
    title: string;
    document_type?: string;
    relevance: number;
    excerpt: string;
  }>;
  processing_time?: number;
}

interface Analytics {
  documents: {
    total: number;
    by_type: Record<string, number>;
    recent: Array<{
      id: number;
      title: string;
      type: string;
      created_at: string;
    }>;
  };
  queries: {
    total: number;
    average_processing_time: number;
    recent: Array<{
      query: string;
      processing_time: number;
      created_at: string;
    }>;
  };
}

interface QueryHistoryItem {
  id: number;
  query_text: string;
  answer: string;
  processing_time: number;
  created_at: string;
  relevant_documents: Array<any>;
}

function App() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
  const [activeTab, setActiveTab] = useState<'upload' | 'query' | 'analytics' | 'history'>('upload');
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [queryHistory, setQueryHistory] = useState<QueryHistoryItem[]>([]);
  const [selectedDocumentType, setSelectedDocumentType] = useState<string>('');

  useEffect(() => {
    fetchDocuments();
    fetchAnalytics();
    fetchQueryHistory();
  }, []);

  const fetchDocuments = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/documents/list/`);
      setDocuments(response.data);
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  const fetchAnalytics = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/analysis/analytics/`);
      setAnalytics(response.data);
    } catch (error) {
      console.error('Error fetching analytics:', error);
    }
  };

  const fetchQueryHistory = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/analysis/query-history/?limit=10`);
      setQueryHistory(response.data);
    } catch (error) {
      console.error('Error fetching query history:', error);
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFile) {
      setMessage({ type: 'error', text: 'Please select a file first' });
      return;
    }

    setUploading(true);
    setMessage(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      await axios.post(`${API_BASE_URL}/documents/upload/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      setMessage({ type: 'success', text: 'Document uploaded successfully!' });
      setSelectedFile(null);
      fetchDocuments();
      fetchAnalytics();
    } catch (error: any) {
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Error uploading document' 
      });
    } finally {
      setUploading(false);
    }
  };

  const handleQuery = async () => {
    if (!query.trim()) {
      setMessage({ type: 'error', text: 'Please enter a query' });
      return;
    }

    setLoading(true);
    setMessage(null);

    try {
      const requestBody: any = { query_text: query };
      if (selectedDocumentType) {
        requestBody.document_type = selectedDocumentType;
      }

      const response = await axios.post(`${API_BASE_URL}/analysis/query/`, requestBody);
      setResponse(response.data);
      fetchQueryHistory();
      fetchAnalytics();
    } catch (error: any) {
      setMessage({ 
        type: 'error', 
        text: error.response?.data?.detail || 'Error processing query' 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteDocument = async (docId: number) => {
    if (!window.confirm('Are you sure you want to delete this document?')) return;
    try {
      await axios.delete(`${API_BASE_URL}/documents/delete/${docId}/`);
      setMessage({ type: 'success', text: 'Document deleted successfully!' });
      fetchDocuments();
      fetchAnalytics && fetchAnalytics();
    } catch (error: any) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Error deleting document',
      });
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Personal Finance Management
          </h1>
          <p className="text-lg text-gray-600">
            Upload your financial documents and ask questions using AI-powered RAG
          </p>
        </div>

        {/* Message Display */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg flex items-center ${
            message.type === 'success' 
              ? 'bg-green-50 border border-green-200 text-green-800' 
              : 'bg-red-50 border border-red-200 text-red-800'
          }`}>
            {message.type === 'success' ? (
              <CheckCircleIcon className="h-5 w-5 mr-2" />
            ) : (
              <ExclamationTriangleIcon className="h-5 w-5 mr-2" />
            )}
            {message.text}
          </div>
        )}

        {/* Navigation Tabs */}
        <div className="mb-6">
          <div className="flex space-x-1 bg-white p-1 rounded-lg shadow-sm">
            <button
              onClick={() => setActiveTab('upload')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'upload'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <DocumentArrowUpIcon className="h-4 w-4 inline mr-2" />
              Upload
            </button>
            <button
              onClick={() => setActiveTab('query')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'query'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <ChatBubbleLeftRightIcon className="h-4 w-4 inline mr-2" />
              Query
            </button>
            <button
              onClick={() => setActiveTab('analytics')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'analytics'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <ChartBarIcon className="h-4 w-4 inline mr-2" />
              Analytics
            </button>
            <button
              onClick={() => setActiveTab('history')}
              className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                activeTab === 'history'
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <ClockIcon className="h-4 w-4 inline mr-2" />
              History
            </button>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'upload' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Document Upload Section */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-center mb-4">
                <DocumentArrowUpIcon className="h-6 w-6 text-blue-600 mr-2" />
                <h2 className="text-xl font-semibold text-gray-900">Upload Document</h2>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select File
                  </label>
                  <input
                    type="file"
                    accept=".txt,.pdf,.doc,.docx"
                    onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                  />
                </div>
                
                {selectedFile && (
                  <div className="text-sm text-gray-600">
                    Selected: {selectedFile.name} ({formatFileSize(selectedFile.size)})
                  </div>
                )}
                
                <button
                  onClick={handleFileUpload}
                  disabled={uploading || !selectedFile}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  {uploading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Uploading...
                    </>
                  ) : (
                    <>
                      <DocumentArrowUpIcon className="h-4 w-4 mr-2" />
                      Upload Document
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Document List */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-center mb-4">
                <DocumentTextIcon className="h-6 w-6 text-green-600 mr-2" />
                <h2 className="text-xl font-semibold text-gray-900">Uploaded Documents</h2>
              </div>
              
              <div className="space-y-3 max-h-96 overflow-y-auto">
                {documents.length === 0 ? (
                  <p className="text-gray-500 text-center py-4">No documents uploaded yet</p>
                ) : (
                  documents.map((doc) => (
                    <div key={doc.id} className="border border-gray-200 rounded-lg p-3 flex justify-between items-center">
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-900">{doc.title}</h3>
                        <p className="text-sm text-gray-600">Type: {doc.document_type}</p>
                        <p className="text-sm text-gray-600">Uploaded: {formatDate(doc.created_at)}</p>
                        {doc.file_size && (
                          <p className="text-sm text-gray-600">Size: {formatFileSize(doc.file_size)}</p>
                        )}
                        {doc.word_count && (
                          <p className="text-sm text-gray-600">Words: {doc.word_count.toLocaleString()}</p>
                        )}
                      </div>
                      <button
                        onClick={() => handleDeleteDocument(doc.id)}
                        className="ml-4 bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded text-xs font-semibold shadow-sm"
                        title="Delete document"
                      >
                        Delete
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}

        {activeTab === 'query' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Query Section */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-center mb-4">
                <ChatBubbleLeftRightIcon className="h-6 w-6 text-green-600 mr-2" />
                <h2 className="text-xl font-semibold text-gray-900">Ask Questions</h2>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Document Type (Optional)
                  </label>
                  <select
                    value={selectedDocumentType}
                    onChange={(e) => setSelectedDocumentType(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">All document types</option>
                    <option value="bank_statement">Bank Statement</option>
                    <option value="credit_card">Credit Card</option>
                    <option value="investment">Investment</option>
                    <option value="tax">Tax Document</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Your Question
                  </label>
                  <textarea
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="e.g., What is my closing balance? How many deposits over $1000?"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={4}
                  />
                </div>
                
                <button
                  onClick={handleQuery}
                  disabled={loading || !query.trim()}
                  className="w-full bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                >
                  {loading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Processing...
                    </>
                  ) : (
                    <>
                      <MagnifyingGlassIcon className="h-4 w-4 mr-2" />
                      Ask Question
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Response Section */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex items-center mb-4">
                <DocumentMagnifyingGlassIcon className="h-6 w-6 text-purple-600 mr-2" />
                <h2 className="text-xl font-semibold text-gray-900">AI Response</h2>
              </div>
              
              {response ? (
                <div className="space-y-4">
                  {response.processing_time && (
                    <div className="text-sm text-gray-600">
                      Processing time: {response.processing_time.toFixed(2)}s
                    </div>
                  )}
                  
                  <div className="bg-gray-50 rounded-lg p-4">
                    <h3 className="font-medium text-gray-900 mb-2">Answer:</h3>
                    <p className="text-gray-700 whitespace-pre-wrap">{response.answer}</p>
                  </div>
                  
                  {response.relevant_documents.length > 0 && (
                    <div>
                      <h3 className="font-medium text-gray-900 mb-2">Relevant Documents:</h3>
                      <div className="space-y-2">
                        {response.relevant_documents.map((doc, index) => (
                          <div key={index} className="border border-gray-200 rounded-lg p-3">
                            <div className="flex justify-between items-start mb-1">
                              <span className="font-medium text-sm">{doc.title}</span>
                              <span className="text-xs text-gray-500">
                                {(doc.relevance * 100).toFixed(1)}% relevant
                              </span>
                            </div>
                            <p className="text-sm text-gray-600">{doc.excerpt}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center text-gray-500 py-8">
                  <ChatBubbleLeftRightIcon className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>Ask a question to get started</p>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'analytics' && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center mb-6">
              <ChartBarIcon className="h-6 w-6 text-purple-600 mr-2" />
              <h2 className="text-xl font-semibold text-gray-900">System Analytics</h2>
            </div>
            
            {analytics ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Document Statistics */}
                <div className="bg-blue-50 rounded-lg p-4">
                  <h3 className="font-medium text-blue-900 mb-3">Documents</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-blue-700">Total Documents:</span>
                      <span className="font-medium">{analytics.documents.total}</span>
                    </div>
                    {Object.entries(analytics.documents.by_type).map(([type, count]) => (
                      <div key={type} className="flex justify-between">
                        <span className="text-blue-700">{type}:</span>
                        <span className="font-medium">{count}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Query Statistics */}
                <div className="bg-green-50 rounded-lg p-4">
                  <h3 className="font-medium text-green-900 mb-3">Queries</h3>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-green-700">Total Queries:</span>
                      <span className="font-medium">{analytics.queries.total}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-green-700">Avg Processing Time:</span>
                      <span className="font-medium">{analytics.queries.average_processing_time}s</span>
                    </div>
                  </div>
                </div>

                {/* Recent Documents */}
                <div className="md:col-span-2">
                  <h3 className="font-medium text-gray-900 mb-3">Recent Documents</h3>
                  <div className="space-y-2">
                    {analytics.documents.recent.map((doc) => (
                      <div key={doc.id} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                        <span className="text-sm">{doc.title}</span>
                        <span className="text-xs text-gray-500">{formatDate(doc.created_at)}</span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Recent Queries */}
                <div className="md:col-span-2">
                  <h3 className="font-medium text-gray-900 mb-3">Recent Queries</h3>
                  <div className="space-y-2">
                    {analytics.queries.recent.map((query, index) => (
                      <div key={index} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                        <span className="text-sm truncate flex-1">{query.query}</span>
                        <span className="text-xs text-gray-500 ml-2">
                          {query.processing_time.toFixed(2)}s
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center text-gray-500 py-8">
                <ChartBarIcon className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <p>Loading analytics...</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'history' && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <div className="flex items-center mb-6">
              <ClockIcon className="h-6 w-6 text-orange-600 mr-2" />
              <h2 className="text-xl font-semibold text-gray-900">Query History</h2>
            </div>
            
            <div className="space-y-4">
              {queryHistory.length === 0 ? (
                <div className="text-center text-gray-500 py-8">
                  <ClockIcon className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                  <p>No query history yet</p>
                </div>
              ) : (
                queryHistory.map((item) => (
                  <div key={item.id} className="border border-gray-200 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="font-medium text-gray-900">{item.query_text}</h3>
                      <div className="text-xs text-gray-500 text-right">
                        <div>{formatDate(item.created_at)}</div>
                        <div>{item.processing_time.toFixed(2)}s</div>
                      </div>
                    </div>
                    <p className="text-gray-700 text-sm mb-2">{item.answer}</p>
                    {item.relevant_documents.length > 0 && (
                      <div className="text-xs text-gray-500">
                        Sources: {item.relevant_documents.length} document(s)
                      </div>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
