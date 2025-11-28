Real Estate Analysis Chatbot

A Mini Real Estate Analysis Chatbot built with React (Frontend) and Django (Backend) that accepts user queries related to real estate localities, processes Excel datasets, and returns natural-language summaries, charts, and filtered data tables.

Features:

- Natural Language Queries: Ask questions about real estate localities in plain English
- Excel Data Processing: Upload and process Excel files with real estate data
- Interactive Charts: Visualize price trends, demand trends, and comparisons
- Filtered Data Tables: View filtered data based on your queries
- Chat Interface: Modern chat-style UI for easy interaction

## Sample Queries

- "Give me analysis of Wakad"
- "Compare Ambegaon Budruk and Aundh demand trends"
- "Show price growth for Akurdi over the last 3 years"


## Technologies Used

### Backend
- Django 4.2.7
- Django REST Framework
- Pandas (Excel processing)
- openpyxl (Excel file handling)

### Frontend
- React 18.2.0
- Bootstrap 5.3.2
- Chart.js & react-chartjs-2 (Data visualization)
- Axios (HTTP client)

## Usage Examples

1. Area Analysis: 
   - Query: "Give me analysis of Wakad"
   - Returns: Summary, price & demand trends chart, filtered table

2. Comparison:
   - Query: "Compare Ambegaon Budruk and Aundh demand trends"
   - Returns: Comparison summary, demand trend comparison chart, filtered table

3. Trend Analysis:
   - Query: "Show price growth for Akurdi over the last 3 years"
   - Returns: Price growth summary, price trend chart, filtered table

Development Notes

- The backend uses mocked LLM output for summaries 
- Area extraction uses keyword matching 
- Chart visualization supports multiple chart types based on query type
- CORS is enabled for development 

License

This project is open source and available for educational purposes.

