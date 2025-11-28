import os
import re
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework.decorators import api_view
from rest_framework.response import Response
import pandas as pd
from pathlib import Path

# Get the base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Path to the data files
EXCEL_FILE_PATH = os.path.join(BASE_DIR, 'data', 'real_estate_data.xlsx')
CSV_FILE_PATH = os.path.join(BASE_DIR, 'data', 'real_estate_data.csv')


def load_excel_data():
    """Load data from Excel or CSV file"""
    try:
        if os.path.exists(EXCEL_FILE_PATH):
            df = pd.read_excel(EXCEL_FILE_PATH)
            return df
        elif os.path.exists(CSV_FILE_PATH):
            # Fallback to CSV if Excel doesn't exist
            df = pd.read_csv(CSV_FILE_PATH)
            return df
        else:
            # Return empty dataframe with expected columns
            return pd.DataFrame(columns=['Year', 'Area', 'Price', 'Demand', 'Size'])
    except Exception as e:
        print(f"Error loading data file: {e}")
        return pd.DataFrame(columns=['Year', 'Area', 'Price', 'Demand', 'Size'])


def extract_areas_from_query(query, df=None):
    """Extract area names from user query"""
    query_lower = query.lower().strip()
    
    # First, try to get areas from the loaded data if available
    available_areas_dict = {}  # {lowercase: original_case}
    if df is not None and not df.empty and 'Area' in df.columns:
        for area in df['Area'].unique():
            if pd.notna(area):
                area_str = str(area).strip()
                area_lower = area_str.lower()
                if area_lower not in available_areas_dict:
                    available_areas_dict[area_lower] = area_str
    
    # Also include common real estate areas as fallback
    common_areas = ['wakad', 'ambegaon budruk', 'aundh', 'akurdi', 'hinjewadi', 
                   'baner', 'kothrud', 'viman nagar', 'hadapsar', 'kharadi']
    for area in common_areas:
        if area not in available_areas_dict:
            available_areas_dict[area] = area.title()
    
    found_areas = []
    
    # Try exact matches first
    for area_lower, area_original in available_areas_dict.items():
        # Check if area name appears in query (word boundary or exact match)
        if area_lower in query_lower:
            # Check if it's a whole word match (better match)
            words = query_lower.split()
            if area_lower in words or any(area_lower in word for word in words):
                if area_original not in found_areas:
                    found_areas.append(area_original)
    
    # If no exact matches, try partial matches (at least 3 characters)
    if len(found_areas) == 0:
        for area_lower, area_original in available_areas_dict.items():
            if len(area_lower) >= 3 and area_lower in query_lower:
                if area_original not in found_areas:
                    found_areas.append(area_original)
    
    return found_areas


def detect_query_type(query):
    """Detect the type of query: analysis, comparison, or trend"""
    query_lower = query.lower()
    
    if 'compare' in query_lower:
        return 'comparison'
    elif 'trend' in query_lower or 'growth' in query_lower:
        return 'trend'
    else:
        return 'analysis'


def generate_summary(df, areas, query_type):
    """Generate a natural language summary (mocked LLM output)"""
    if df.empty or len(areas) == 0:
        return "No data available for the requested areas."
    
    summary_parts = []
    
    if query_type == 'comparison' and len(areas) >= 2:
        area1_clean = str(areas[0]).strip()
        area2_clean = str(areas[1]).strip()
        area1_data = df[df['Area'].astype(str).str.strip().str.lower() == area1_clean.lower()]
        area2_data = df[df['Area'].astype(str).str.strip().str.lower() == area2_clean.lower()]
        
        if not area1_data.empty and not area2_data.empty:
            avg_price1 = area1_data['Price'].mean()
            avg_price2 = area2_data['Price'].mean()
            avg_demand1 = area1_data['Demand'].mean()
            avg_demand2 = area2_data['Demand'].mean()
            
            summary_parts.append(f"Comparison between {areas[0]} and {areas[1]}:")
            summary_parts.append(f"{areas[0]} has an average price of ₹{avg_price1:,.0f} and average demand of {avg_demand1:.1f}.")
            summary_parts.append(f"{areas[1]} has an average price of ₹{avg_price2:,.0f} and average demand of {avg_demand2:.1f}.")
            
            if avg_price1 > avg_price2:
                summary_parts.append(f"{areas[0]} is {((avg_price1/avg_price2 - 1) * 100):.1f}% more expensive than {areas[1]}.")
            else:
                summary_parts.append(f"{areas[1]} is {((avg_price2/avg_price1 - 1) * 100):.1f}% more expensive than {areas[0]}.")
    
    elif query_type == 'trend':
        for area in areas:
            area_clean = str(area).strip()
            area_data = df[df['Area'].astype(str).str.strip().str.lower() == area_clean.lower()].sort_values('Year')
            if not area_data.empty:
                if len(area_data) > 1:
                    first_price = area_data.iloc[0]['Price']
                    last_price = area_data.iloc[-1]['Price']
                    growth = ((last_price - first_price) / first_price) * 100
                    
                    summary_parts.append(f"Price trend for {area}:")
                    summary_parts.append(f"Price grew from ₹{first_price:,.0f} to ₹{last_price:,.0f}, representing a {growth:.1f}% increase over the period.")
                else:
                    summary_parts.append(f"{area} has a current price of ₹{area_data.iloc[0]['Price']:,.0f}.")
    
    else:  # analysis
        for area in areas:
            # More robust area matching - handle whitespace and case
            area_clean = str(area).strip()
            area_data = df[df['Area'].astype(str).str.strip().str.lower() == area_clean.lower()]
            
            if not area_data.empty:
                avg_price = area_data['Price'].mean()
                avg_demand = area_data['Demand'].mean()
                avg_size = area_data['Size'].mean()
                latest_year = area_data['Year'].max()
                latest_data = area_data[area_data['Year'] == latest_year]
                
                summary_parts.append(f"Analysis for {area}:")
                summary_parts.append(f"Average price: ₹{avg_price:,.0f}")
                summary_parts.append(f"Average demand: {avg_demand:.1f}")
                summary_parts.append(f"Average property size: {avg_size:.1f} sqft")
                if not latest_data.empty:
                    summary_parts.append(f"Latest data (Year {latest_year}): Price ₹{latest_data.iloc[0]['Price']:,.0f}, Demand {latest_data.iloc[0]['Demand']:.1f}")
            else:
                # Debug: show what areas are actually in the data
                available_areas = df['Area'].astype(str).str.strip().unique() if 'Area' in df.columns else []
                summary_parts.append(f"Warning: No data found for '{area}'. Available areas: {', '.join(available_areas[:5])}")
    
    return " ".join(summary_parts) if summary_parts else "No data found for the requested analysis."


def get_chart_data(df, areas, query_type):
    """Generate chart data in JSON format"""
    chart_data = {
        'labels': [],
        'datasets': []
    }
    
    if df.empty or len(areas) == 0:
        return chart_data
    
    if query_type == 'comparison' and len(areas) >= 2:
        # Compare demand trends
        years = sorted(df['Year'].unique())
        chart_data['labels'] = [str(int(year)) for year in years]
        
        for area in areas[:2]:  # Limit to 2 areas for comparison
            area_clean = str(area).strip()
            area_data = df[df['Area'].astype(str).str.strip().str.lower() == area_clean.lower()].sort_values('Year')
            demand_values = []
            for year in years:
                year_data = area_data[area_data['Year'] == year]
                if not year_data.empty:
                    demand_values.append(float(year_data['Demand'].mean()))
                else:
                    demand_values.append(0)
            
            chart_data['datasets'].append({
                'label': f'{area} Demand',
                'data': demand_values,
                'borderColor': f'rgb({75 + len(chart_data["datasets"]) * 50}, 192, 192)',
                'backgroundColor': f'rgba({75 + len(chart_data["datasets"]) * 50}, 192, 192, 0.2)',
            })
    
    elif query_type == 'trend':
        # Price trend over years
        for area in areas:
            area_clean = str(area).strip()
            area_data = df[df['Area'].astype(str).str.strip().str.lower() == area_clean.lower()].sort_values('Year')
            if not area_data.empty:
                years = [str(int(year)) for year in area_data['Year'].tolist()]
                prices = [float(price) for price in area_data['Price'].tolist()]
                
                chart_data['labels'] = years
                chart_data['datasets'].append({
                    'label': f'{area} Price',
                    'data': prices,
                    'borderColor': f'rgb({75 + len(chart_data["datasets"]) * 50}, 192, 192)',
                    'backgroundColor': f'rgba({75 + len(chart_data["datasets"]) * 50}, 192, 192, 0.2)',
                })
                break  # For trend, show only first area
    
    else:  # analysis
        # Show price and demand trends
        for area in areas:
            area_clean = str(area).strip()
            area_data = df[df['Area'].astype(str).str.strip().str.lower() == area_clean.lower()].sort_values('Year')
            if not area_data.empty:
                years = [str(int(year)) for year in area_data['Year'].tolist()]
                prices = [float(price) for price in area_data['Price'].tolist()]
                demands = [float(demand) for demand in area_data['Demand'].tolist()]
                
                chart_data['labels'] = years
                chart_data['datasets'].append({
                    'label': f'{area} Price',
                    'data': prices,
                    'yAxisID': 'y',
                    'borderColor': 'rgb(75, 192, 192)',
                    'backgroundColor': 'rgba(75, 192, 192, 0.2)',
                })
                chart_data['datasets'].append({
                    'label': f'{area} Demand',
                    'data': demands,
                    'yAxisID': 'y1',
                    'borderColor': 'rgb(255, 99, 132)',
                    'backgroundColor': 'rgba(255, 99, 132, 0.2)',
                })
                break  # For analysis, show only first area
    
    return chart_data


def get_filtered_table(df, areas):
    """Get filtered table data based on areas"""
    if df.empty or len(areas) == 0:
        return []
    
    # More robust area matching - handle whitespace and case
    area_lower_list = [str(area).strip().lower() for area in areas]
    filtered_df = df[df['Area'].astype(str).str.strip().str.lower().isin(area_lower_list)]
    
    # Convert to list of dictionaries
    table_data = filtered_df.to_dict('records')
    
    # Convert numpy types to native Python types
    for record in table_data:
        for key, value in record.items():
            if pd.isna(value):
                record[key] = None
            elif isinstance(value, (pd.Timestamp,)):
                record[key] = str(value)
            else:
                record[key] = float(value) if isinstance(value, (int, float)) else str(value)
    
    return table_data


@api_view(['POST'])
@csrf_exempt
def analyze_query(request):
    """Main API endpoint for processing real estate queries"""
    try:
        query = request.data.get('query', '')
        
        if not query:
            return Response({'error': 'Query is required'}, status=400)
        
        # Load data
        df = load_excel_data()
        
        # Extract areas and detect query type (pass df to extract_areas_from_query)
        areas = extract_areas_from_query(query, df)
        query_type = detect_query_type(query)
        
        # If no areas found, provide helpful message with available areas
        if len(areas) == 0:
            available_areas = []
            if not df.empty and 'Area' in df.columns:
                available_areas = sorted([str(area) for area in df['Area'].unique() if pd.notna(area)])[:10]  # Show first 10
            
            error_msg = 'No recognized areas found in your query.'
            if available_areas:
                error_msg += f' Available areas in your data: {", ".join(available_areas)}. Please mention one of these areas in your query.'
            else:
                error_msg += ' Please mention specific area names from your uploaded data.'
            
            return Response({
                'summary': error_msg,
                'chart_data': {'labels': [], 'datasets': []},
                'table_data': [],
                'available_areas': available_areas
            })
        
        # Debug: Log extracted areas
        print(f"Query: {query}")
        print(f"Extracted areas: {areas}")
        print(f"DataFrame shape: {df.shape}")
        if not df.empty and 'Area' in df.columns:
            print(f"Available areas in data: {df['Area'].unique()}")
        
        # Generate response
        summary = generate_summary(df, areas, query_type)
        chart_data = get_chart_data(df, areas, query_type)
        table_data = get_filtered_table(df, areas)
        
        return Response({
            'summary': summary,
            'chart_data': chart_data,
            'table_data': table_data,
            'query_type': query_type,
            'areas': areas,
            'debug': {
                'extracted_areas': areas,
                'data_shape': df.shape if not df.empty else None,
                'available_areas': list(df['Area'].unique()) if not df.empty and 'Area' in df.columns else []
            }
        })
    
    except Exception as e:
        return Response({'error': str(e)}, status=500)


@api_view(['GET'])
def health_check(request):
    """Health check endpoint"""
    return Response({'status': 'ok', 'message': 'Real Estate Analysis API is running'})


@api_view(['GET'])
def list_areas(request):
    """List all available areas in the dataset"""
    try:
        df = load_excel_data()
        
        if df.empty or 'Area' not in df.columns:
            return Response({
                'areas': [],
                'message': 'No data available. Please upload an Excel file first.'
            })
        
        areas = sorted([str(area) for area in df['Area'].unique() if pd.notna(area)])
        
        return Response({
            'areas': areas,
            'count': len(areas),
            'message': f'Found {len(areas)} unique areas in the dataset.'
        })
    except Exception as e:
        return Response({'error': str(e)}, status=500)


def map_columns(df):
    """Map various column names to standard format"""
    column_mapping = {}
    
    # Map Year - prioritize exact matches
    year_candidates = ['year', 'yr']
    for col in df.columns:
        col_lower = str(col).lower().strip()
        if col_lower in year_candidates:
            column_mapping['Year'] = col
            break
    
    # Map Area - prioritize final location (more specific), then locality, then city
    # This ensures we get specific areas like "Wakad" instead of just "Pune"
    area_priority = ['final location', 'locality', 'location', 'area', 'place', 'region', 'city']
    for priority in area_priority:
        for col in df.columns:
            col_lower = str(col).lower().strip()
            if col_lower == priority or priority in col_lower:
                if col not in column_mapping.values():
                    column_mapping['Area'] = col
                    break
        if 'Area' in column_mapping:
            break
    
    # Map Price - look for price/rate columns, prioritize weighted average rate
    price_priority = [
        'flat - weighted average rate',
        'office - weighted average rate',
        'shop - weighted average rate',
        'others - weighted average rate',
        'weighted average rate',
        'average rate',
        'prevailing rate',
        'most prevailing rate',
        'rate',
        'price'
    ]
    for priority in price_priority:
        for col in df.columns:
            col_lower = str(col).lower().strip()
            if priority in col_lower or col_lower == priority:
                column_mapping['Price'] = col
                break
        if 'Price' in column_mapping:
            break
    
    # Map Demand - look for sales/demand columns, prioritize total_sales or total sold
    demand_priority = [
        'total_sales',
        'total sold',
        'total units',
        'residential_sold',
        'flat_sold',
        'demand',
        'sales',
        'sold',
        'units'
    ]
    for priority in demand_priority:
        for col in df.columns:
            col_lower = str(col).lower().strip()
            # Handle columns with spaces, dashes, or underscores
            col_normalized = col_lower.replace(' ', '_').replace('-', '_')
            if priority in col_lower or priority in col_normalized or col_lower == priority:
                column_mapping['Demand'] = col
                break
        if 'Demand' in column_mapping:
            break
    
    # Map Size - look for area/size columns, prioritize carpet area
    size_priority = [
        'total carpet area supplied',
        'carpet area supplied',
        'total carpet area',
        'carpet area',
        'sqft',
        'size',
        'area'
    ]
    for priority in size_priority:
        for col in df.columns:
            col_lower = str(col).lower().strip()
            if priority in col_lower:
                if col not in column_mapping.values():  # Don't use if already mapped to Area
                    column_mapping['Size'] = col
                    break
        if 'Size' in column_mapping:
            break
    
    return column_mapping


def transform_dataframe(df, column_mapping):
    """Transform dataframe to standard format"""
    # Create a new dataframe with standard columns
    transformed_df = pd.DataFrame()
    
    # Map Year - try to extract year from various formats
    if 'Year' in column_mapping:
        year_col = column_mapping['Year']
        if df[year_col].dtype == 'object':
            # Try to extract year from strings
            transformed_df['Year'] = pd.to_numeric(
                df[year_col].astype(str).str.extract(r'(\d{4})')[0], 
                errors='coerce'
            )
        else:
            transformed_df['Year'] = pd.to_numeric(df[year_col], errors='coerce')
    else:
        # Default to current year if not found
        transformed_df['Year'] = 2024
    
    # Map Area - use the mapped column, or try to combine city + final location if both exist
    if 'Area' in column_mapping:
        area_col = column_mapping['Area']
        transformed_df['Area'] = df[area_col].astype(str).str.strip()
        
        # If we mapped to "city" but "final location" also exists, use final location for more specificity
        # Check if there's a "final location" column that wasn't used
        final_location_cols = [col for col in df.columns if 'final location' in str(col).lower()]
        if final_location_cols and area_col.lower() != 'final location':
            final_loc_col = final_location_cols[0]
            # Use final location if it has more unique values (more specific)
            if df[final_loc_col].nunique() > df[area_col].nunique():
                transformed_df['Area'] = df[final_loc_col].astype(str).str.strip()
                print(f"Using '{final_loc_col}' instead of '{area_col}' for Area (more specific)")
    else:
        transformed_df['Area'] = 'Unknown'
    
    # Map Price - use first available price column or calculate average
    if 'Price' in column_mapping:
        price_col = column_mapping['Price']
        transformed_df['Price'] = pd.to_numeric(df[price_col], errors='coerce')
    else:
        # Try to find any rate column
        rate_cols = [col for col in df.columns if 'rate' in str(col).lower()]
        if rate_cols:
            # Use first rate column or average if multiple
            if len(rate_cols) == 1:
                transformed_df['Price'] = pd.to_numeric(df[rate_cols[0]], errors='coerce')
            else:
                # Average multiple rate columns
                transformed_df['Price'] = df[rate_cols].apply(
                    lambda x: pd.to_numeric(x, errors='coerce')
                ).mean(axis=1)
        else:
            transformed_df['Price'] = 0
    
    # Map Demand
    if 'Demand' in column_mapping:
        demand_col = column_mapping['Demand']
        transformed_df['Demand'] = pd.to_numeric(df[demand_col], errors='coerce')
    else:
        # Try to sum all sold columns
        sold_cols = [col for col in df.columns if 'sold' in str(col).lower()]
        if sold_cols:
            transformed_df['Demand'] = df[sold_cols].apply(
                lambda x: pd.to_numeric(x, errors='coerce')
            ).sum(axis=1)
        else:
            transformed_df['Demand'] = 0
    
    # Map Size
    if 'Size' in column_mapping:
        size_col = column_mapping['Size']
        transformed_df['Size'] = pd.to_numeric(df[size_col], errors='coerce')
    else:
        # Try to find area columns
        area_cols = [col for col in df.columns if 'sqft' in str(col).lower() or 'area' in str(col).lower()]
        if area_cols:
            transformed_df['Size'] = pd.to_numeric(df[area_cols[0]], errors='coerce')
        else:
            transformed_df['Size'] = 0
    
    # Fill NaN values
    transformed_df['Year'] = transformed_df['Year'].fillna(2024)
    transformed_df['Price'] = transformed_df['Price'].fillna(0)
    transformed_df['Demand'] = transformed_df['Demand'].fillna(0)
    transformed_df['Size'] = transformed_df['Size'].fillna(0)
    transformed_df['Area'] = transformed_df['Area'].fillna('Unknown')
    
    # Convert Year to int
    transformed_df['Year'] = transformed_df['Year'].astype(int)
    
    return transformed_df


@api_view(['POST'])
@csrf_exempt
def upload_file(request):
    """Endpoint for uploading Excel file"""
    try:
        # Check if file is in request
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided. Please select a file to upload.'}, status=400)
        
        file = request.FILES['file']
        
        # Check if file is empty
        if file.size == 0:
            return Response({'error': 'File is empty. Please upload a valid file.'}, status=400)
        
        # Validate file extension
        if not file.name.endswith(('.xlsx', '.xls')):
            return Response({'error': 'Invalid file format. Please upload an Excel file (.xlsx or .xls).'}, status=400)
        
        # Save file
        data_dir = os.path.join(BASE_DIR, 'data')
        os.makedirs(data_dir, exist_ok=True)
        file_path = os.path.join(data_dir, 'real_estate_data.xlsx')
        
        # Write file
        with open(file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        # Validate file can be read
        try:
            df = pd.read_excel(file_path)
            
            if df.empty:
                return Response({
                    'error': 'The uploaded file is empty. Please upload a file with data.'
                }, status=400)
            
            # Map columns to standard format
            column_mapping = map_columns(df)
            
            # Transform dataframe to standard format
            transformed_df = transform_dataframe(df, column_mapping)
            
            # Save transformed dataframe
            transformed_file_path = os.path.join(data_dir, 'real_estate_data.xlsx')
            transformed_df.to_excel(transformed_file_path, index=False)
            
            # Return success with mapping info
            mapping_info = {k: v for k, v in column_mapping.items()}
            
            return Response({
                'message': 'File uploaded and processed successfully',
                'rows': len(transformed_df),
                'original_columns': list(df.columns),
                'mapped_columns': mapping_info,
                'transformed_columns': list(transformed_df.columns),
                'sample_data': transformed_df.head(5).to_dict('records') if len(transformed_df) > 0 else []
            })
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"Upload error: {error_details}")
            return Response({
                'error': f'Failed to process Excel file: {str(e)}. Please ensure the file is a valid Excel file with data.',
                'details': str(e)
            }, status=400)
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Upload error: {error_details}")
        return Response({'error': f'Server error: {str(e)}'}, status=500)

