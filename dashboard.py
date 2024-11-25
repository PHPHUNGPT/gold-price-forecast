import pandas as pd
import dash
from dash import dcc, html, Input, Output
import plotly.express as px

# Load the dataset
file_path = 'data/gld_price_data_cleaned.csv'  # Replace with your file path
data = pd.read_csv(file_path)

# Initialize the Dash app
app = dash.Dash(__name__)
app.title = "Interactive Dashboard - Gold Price Data"

# Define layout of the dashboard
app.layout = html.Div([
    html.H1("Interactive Dashboard - Gold Price Data", style={'text-align': 'center'}),

    html.Div([
        html.Label("Select a Variable:"),
        dcc.Dropdown(
            id='variable-selector',
            options=[{'label': col, 'value': col} for col in data.columns if col != 'Date'],
            value=data.columns[1],  # Default variable
            clearable=False,
        ),
        html.Label("Select a Chart Type:"),
        dcc.Dropdown(
            id='chart-type-selector',
            options=[
                {'label': 'Bar Chart', 'value': 'bar'},
                {'label': 'Line Chart', 'value': 'line'},
                {'label': 'Scatter Plot', 'value': 'scatter'},
                {'label': 'Pie Chart', 'value': 'pie'},
                {'label': 'Box Plot', 'value': 'box'},
                {'label': 'Correlation Matrix', 'value': 'corr_matrix'}
            ],
            value='line',  # Default chart type
            clearable=False,
        ),
    ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),

    html.Div([
        dcc.Graph(id='chart-output')
    ], style={'width': '100%', 'display': 'inline-block', 'padding': '10px'}),
])

# Callback to update the chart based on user selection
@app.callback(
    Output('chart-output', 'figure'),
    [Input('variable-selector', 'value'),
     Input('chart-type-selector', 'value')]
)
def update_chart(selected_variable, chart_type):
    if chart_type == 'bar':
        fig = px.bar(data, x='Date', y=selected_variable, title=f"Bar Chart of {selected_variable}")
    elif chart_type == 'line':
        fig = px.line(data, x='Date', y=selected_variable, title=f"Line Chart of {selected_variable}")
    elif chart_type == 'scatter':
        fig = px.scatter(data, x='Date', y=selected_variable, title=f"Scatter Plot of {selected_variable}")
    elif chart_type == 'pie':
        # Use a subset of data for the pie chart
        fig = px.pie(data.head(10), values=selected_variable, names='Date', title=f"Pie Chart of {selected_variable}")
    elif chart_type == 'box':
        fig = px.box(data, y=selected_variable, title=f"Box Plot of {selected_variable}")
    elif chart_type == 'corr_matrix':
        # Compute correlation matrix excluding non-numeric columns
        corr = data.select_dtypes(include=['number']).corr()
        fig = px.imshow(corr, text_auto=True, title="Correlation Matrix")
    else:
        fig = px.line(data, x='Date', y=selected_variable, title=f"Line Chart of {selected_variable}")

    fig.update_layout(template='plotly', title_x=0.5)
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
