import React, { useState } from 'react';
import { Container, Row, Col, Card, Button } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import ChatInterface from './components/ChatInterface';
import './App.css';

function App() {
  return (
    <div className="App">
      <Container fluid className="py-4">
        <Row>
          <Col>
            <Card className="shadow-sm">
              <Card.Header className="bg-primary text-white">
                <h2 className="mb-0">🏠 Real Estate Analysis Chatbot</h2>
                <small>Ask questions about real estate localities and get insights</small>
              </Card.Header>
              <Card.Body>
                <ChatInterface />
              </Card.Body>
            </Card>
          </Col>
        </Row>
      </Container>
    </div>
  );
}

export default App;

