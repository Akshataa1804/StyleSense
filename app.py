from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for flash messages
UPLOAD_FOLDER = 'uploads'  # Folder to save uploaded files
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Make sure the uploads folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize variable to hold the cleaned dataset
data_cleaned = None

# Function to load and clean the dataset
def load_data(file_path):
    global data_cleaned
    data_cleaned = pd.read_csv(file_path)

# Transaction Analysis

# Top 10 Products by Average Rating
def get_top_10_by_avg_rating():
    return data_cleaned.groupby('name')['avg_rating'].mean().sort_values(ascending=False).head(10)

# Top 10 Products by Number of Reviews
def get_top_10_by_num_reviews():
    return data_cleaned['name'].value_counts().head(10)

# Plotting functions
def plot_top_10_avg_rating(top_10_data):
    fig = px.bar(top_10_data, x=top_10_data.index, y=top_10_data.values,
                 title="Top 10 Products by Average Rating", labels={'x': 'Product Name', 'y': 'Average Rating'},
                 template='plotly_white')
    return fig.to_html(full_html=False)

def plot_top_10_num_reviews(top_10_data):
    fig = px.bar(top_10_data, x=top_10_data.index, y=top_10_data.values,
                 title="Top 10 Products by Number of Reviews", labels={'x': 'Product Name', 'y': 'Number of Reviews'},
                 template='plotly_white')
    return fig.to_html(full_html=False)

# Inventory Analysis

def plot_availability(data):
    availability_counts = data['availability'].value_counts()
    fig = px.bar(availability_counts, x=availability_counts.index, y=availability_counts.values,
                 title="Product Availability (In Stock vs Out Of Stock)", labels={'x': 'Availability', 'y': 'Count'},
                 template='plotly_white')
    return fig.to_html(full_html=False)

def plot_price_distribution(data):
    plt.figure(figsize=(10, 6))
    sns.histplot(data['price'], bins=20, kde=True, color='blue')
    plt.title('Price Distribution')
    plt.xlabel('Price')
    plt.ylabel('Frequency')
    img = io.BytesIO()
    plt.savefig(img, format='png')
    plt.close()
    img.seek(0)
    return base64.b64encode(img.getvalue()).decode('utf-8')

def plot_available_sizes(data):
    available_sizes_counts = data['available_sizes'].value_counts().head(10)
    fig = px.bar(available_sizes_counts, x=available_sizes_counts.index, y=available_sizes_counts.values,
                 title="Top 10 Available Sizes", labels={'x': 'Size', 'y': 'Count'},
                 template='plotly_white')
    return fig.to_html(full_html=False)

def plot_available_colors(data):
    color_counts = data['color'].value_counts().head(10)
    fig = px.pie(names=color_counts.index, values=color_counts.values, title="Top 10 Available Colors", template='plotly_white')
    return fig.to_html(full_html=False)

# Summary data
def create_summary():
    total_sales = data_cleaned['price'].count()
    total_revenue = data_cleaned['price'].sum()
    average_price = data_cleaned['price'].mean()
    top_product = data_cleaned.groupby('name')['price'].sum().idxmax()
    
    summary_points = [
        f"Total Sales: {total_sales}",
        f"Total Revenue: ${total_revenue:,.2f}",
        f"Average Price: ${average_price:,.2f}",
        f"Top Selling Product: {top_product}",
        f"Total Unique Products: {data_cleaned['name'].nunique()}",
        f"Total Available Stock: {data_cleaned['availability'].value_counts().get('In Stock', 0)}"
    ]
    return summary_points

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'dataset' not in request.files:
        flash('No file part')
        return redirect(request.url)

    file = request.files['dataset']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and file.filename.endswith('.csv'):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        load_data(file_path)  # Load the cleaned dataset
        flash('Upload successful!')  # Flash a success message
        return redirect(url_for('index'))
    else:
        flash('Please upload a valid CSV file')
        return redirect(request.url)

@app.route('/transaction_analysis')
def transaction_analysis():
    if data_cleaned is None:
        flash('Please upload a dataset first.')
        return redirect(url_for('index'))

    return render_template('transaction_analysis.html')

@app.route('/plot_avg_rating')
def plot_avg_rating():
    if data_cleaned is None:
        flash('Please upload a dataset first.')
        return redirect(url_for('index'))

    top_10_by_avg_rating = get_top_10_by_avg_rating()
    avg_rating_graph = plot_top_10_avg_rating(top_10_by_avg_rating)
    description = "This graph shows the top 10 products based on their average rating."
    return render_template('transaction_analysis.html', avg_rating_graph=avg_rating_graph, description=description)

@app.route('/plot_num_reviews')
def plot_num_reviews():
    if data_cleaned is None:
        flash('Please upload a dataset first.')
        return redirect(url_for('index'))

    top_10_by_num_reviews = get_top_10_by_num_reviews()
    num_reviews_graph = plot_top_10_num_reviews(top_10_by_num_reviews)
    description = "This graph shows the top 10 products based on the number of reviews."
    return render_template('transaction_analysis.html', num_reviews_graph=num_reviews_graph, description=description)

@app.route('/inventory_analysis')
def inventory_analysis():
    if data_cleaned is None:
        flash('Please upload a dataset first.')
        return redirect(url_for('index'))

    return render_template('inventory_analysis.html')

@app.route('/plot_availability')
def plot_availability_route():
    if data_cleaned is None:
        flash('Please upload a dataset first.')
        return redirect(url_for('index'))

    availability_graph = plot_availability(data_cleaned)
    description = "This graph shows the availability of products in stock vs. out of stock."
    return render_template('inventory_analysis.html', availability_graph=availability_graph, description=description)

@app.route('/plot_price_distribution')
def plot_price_distribution_route():
    if data_cleaned is None:
        flash('Please upload a dataset first.')
        return redirect(url_for('index'))

    price_distribution_graph = plot_price_distribution(data_cleaned)
    description = "This graph shows the distribution of product prices."
    return render_template('inventory_analysis.html', price_distribution_graph=price_distribution_graph, description=description)

@app.route('/plot_available_sizes')
def plot_available_sizes_route():
    if data_cleaned is None:
        flash('Please upload a dataset first.')
        return redirect(url_for('index'))

    available_sizes_graph = plot_available_sizes(data_cleaned)
    description = "This graph shows the top 10 available sizes."
    return render_template('inventory_analysis.html', available_sizes_graph=available_sizes_graph, description=description)

@app.route('/plot_available_colors')
def plot_available_colors_route():
    if data_cleaned is None:
        flash('Please upload a dataset first.')
        return redirect(url_for('index'))

    available_colors_graph = plot_available_colors(data_cleaned)
    description = "This graph shows the top 10 available colors."
    return render_template('inventory_analysis.html', available_colors_graph=available_colors_graph, description=description)

@app.route('/summary')
def summary():
    if data_cleaned is None:
        flash('Please upload a dataset first.')
        return redirect(url_for('index'))

    summary_points = create_summary()
    return render_template('summary.html', summary_points=summary_points)

if __name__ == '__main__':
    app.run(debug=True)
