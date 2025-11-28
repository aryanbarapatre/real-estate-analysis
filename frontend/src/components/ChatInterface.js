import React, { useState, useRef, useEffect } from 'react';
import { Form, Button, Card, Table, Alert, Spinner, Badge } from 'react-bootstrap';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const API_BASE_URL = 'http://localhost:8000/api';

const ChatInterface = () => {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentResponse, setCurrentResponse] = useState(null);
  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, currentResponse]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userMessage = query.trim();
    setQuery('');
    setLoading(true);
    setCurrentResponse(null);

    // Add user message to chat
    setMessages(prev => [...prev, { type: 'user', content: userMessage }]);

    try {
      const response = await axios.post(`${API_BASE_URL}/analyze/`, {
        query: userMessage
      }, {
        timeout: 30000, // 30 second timeout
      });

      setCurrentResponse(response.data);
      setMessages(prev => [...prev, { 
        type: 'bot', 
        content: response.data.summary,
        data: response.data
      }]);
    } catch (error) {
      console.error('Error:', error);
      let errorMessage = 'Failed to process query. Please try again.';
      
      if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
        errorMessage = 'Cannot connect to backend server. Please make sure the Django server is running on http://localhost:8000';
      } else if (error.response?.data?.error) {
        errorMessage = error.response.data.error;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      setMessages(prev => [...prev, { 
        type: 'error', 
        content: errorMessage 
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      setLoading(true);
      const response = await axios.post(`${API_BASE_URL}/upload/`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 30000, // 30 second timeout
      });

      const mappingInfo = response.data.mapped_columns 
        ? `\nColumn mapping:\n${Object.entries(response.data.mapped_columns).map(([k, v]) => `  ${k} ← ${v}`).join('\n')}`
        : '';
      
      alert(`File uploaded successfully! ${response.data.rows} rows loaded.${mappingInfo}`);
      setMessages(prev => [...prev, { 
        type: 'system', 
        content: `File "${file.name}" uploaded successfully. ${response.data.rows} rows of data loaded.${mappingInfo}` 
      }]);
    } catch (error) {
      console.error('Upload error:', error);
      let errorMessage = 'Failed to upload file.';
      
      if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
        errorMessage = 'Cannot connect to backend server. Please make sure the Django server is running on http://localhost:8000';
      } else if (error.response?.data?.error) {
        errorMessage = error.response.data.error;
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      alert(errorMessage);
      setMessages(prev => [...prev, { 
        type: 'error', 
        content: errorMessage 
      }]);
    } finally {
      setLoading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const getChartOptions = (queryType) => {
    const baseOptions = {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top',
        },
        title: {
          display: true,
          text: queryType === 'comparison' 
            ? 'Demand Trend Comparison' 
            : queryType === 'trend' 
            ? 'Price Growth Trend' 
            : 'Price & Demand Trends',
        },
      },
    };

    if (queryType === 'analysis') {
      baseOptions.scales = {
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          title: {
            display: true,
            text: 'Price (₹)'
          }
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          title: {
            display: true,
            text: 'Demand'
          },
          grid: {
            drawOnChartArea: false,
          },
        },
      };
    } else {
      baseOptions.scales = {
        y: {
          beginAtZero: false,
          title: {
            display: true,
            text: queryType === 'comparison' ? 'Demand' : 'Price (₹)'
          }
        }
      };
    }

    return baseOptions;
  };

  const sampleQueries = [
    "Give me analysis of Wakad",
    "Compare Ambegaon Budruk and Aundh demand trends",
    "Show price growth for Akurdi over the last 3 years"
  ];

  return (
    <div>
      {/* File Upload Section */}
      <Card className="mb-3">
        <Card.Body>
          <Form.Group>
            <Form.Label>Upload Excel File (Optional)</Form.Label>
            <Form.Control
              ref={fileInputRef}
              type="file"
              accept=".xlsx,.xls"
              onChange={handleFileUpload}
              disabled={loading}
            />
            <Form.Text className="text-muted">
              Upload a new Excel file to replace the default dataset
            </Form.Text>
          </Form.Group>
        </Card.Body>
      </Card>

      {/* Sample Queries */}
      <Card className="mb-3">
        <Card.Body>
          <h6>Sample Queries:</h6>
          <div className="d-flex flex-wrap gap-2">
            {sampleQueries.map((sample, idx) => (
              <Button
                key={idx}
                variant="outline-primary"
                size="sm"
                onClick={() => setQuery(sample)}
                disabled={loading}
              >
                {sample}
              </Button>
            ))}
          </div>
        </Card.Body>
      </Card>

      {/* Chat Messages */}
      <Card className="mb-3" style={{ maxHeight: '400px', overflowY: 'auto' }}>
        <Card.Body>
          {messages.length === 0 && (
            <div className="text-center text-muted py-4">
              <p>👋 Welcome! Ask me about real estate localities.</p>
              <p className="small">Try: "Give me analysis of Wakad"</p>
            </div>
          )}
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`mb-3 chat-message ${
                msg.type === 'user' ? 'text-end' : 'text-start'
              }`}
            >
              <Badge
                bg={msg.type === 'user' ? 'primary' : msg.type === 'error' ? 'danger' : 'success'}
                className="p-2"
              >
                {msg.type === 'user' ? 'You' : msg.type === 'error' ? 'Error' : 'Bot'}
              </Badge>
              <div className="mt-2">
                {msg.type === 'user' ? (
                  <strong>{msg.content}</strong>
                ) : (
                  <div>{msg.content}</div>
                )}
              </div>
            </div>
          ))}
          {loading && (
            <div className="text-center">
              <Spinner animation="border" variant="primary" />
              <p className="mt-2 text-muted">Analyzing your query...</p>
            </div>
          )}
          <div ref={messagesEndRef} />
        </Card.Body>
      </Card>

      {/* Query Input */}
      <Form onSubmit={handleSubmit} className="mb-3">
        <Form.Group className="d-flex gap-2">
          <Form.Control
            type="text"
            placeholder="Ask about real estate localities (e.g., 'Analyze Wakad')"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={loading}
          />
          <Button type="submit" variant="primary" disabled={loading}>
            Send
          </Button>
        </Form.Group>
      </Form>

      {/* Results Section */}
      {currentResponse && (
        <div>
          {/* Chart */}
          {currentResponse.chart_data && 
           currentResponse.chart_data.labels && 
           currentResponse.chart_data.labels.length > 0 && (
            <Card className="mb-3">
              <Card.Body>
                <div style={{ height: '400px' }}>
                  <Line
                    data={currentResponse.chart_data}
                    options={getChartOptions(currentResponse.query_type)}
                  />
                </div>
              </Card.Body>
            </Card>
          )}

          {/* Data Table */}
          {currentResponse.table_data && currentResponse.table_data.length > 0 && (
            <Card>
              <Card.Header>
                <h5 className="mb-0">Filtered Data</h5>
              </Card.Header>
              <Card.Body>
                <div className="table-responsive">
                  <Table striped bordered hover size="sm">
                    <thead>
                      <tr>
                        {Object.keys(currentResponse.table_data[0]).map((key) => (
                          <th key={key}>{key}</th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {currentResponse.table_data.map((row, idx) => (
                        <tr key={idx}>
                          {Object.values(row).map((value, valIdx) => (
                            <td key={valIdx}>
                              {typeof value === 'number' 
                                ? value.toLocaleString('en-IN', { maximumFractionDigits: 2 })
                                : value}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </Table>
                </div>
              </Card.Body>
            </Card>
          )}
        </div>
      )}
    </div>
  );
};

export default ChatInterface;

