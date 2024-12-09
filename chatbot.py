from flask import Flask, request, jsonify
import pandas as pd
import openai
import os
from flask_cors import CORS

app = Flask(__name__)

# Load your flooring data
flooring_data = pd.read_csv('sample_flooring_products.csv')

# Set up OpenAI API key (I provided mine in case you don't have one)
openai.api_key = "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"

## Helper function for cost calculation
def calculate_cost(flooring_type, area):
    product = flooring_data[flooring_data['Type'].str.lower() == flooring_type.lower()]
    if product.empty:
        return "Sorry, we couldn't find that flooring type. Please try again."

    # Extract costs
    price_per_sqft = product.iloc[0]['Price per Sq Ft']
    install_cost_per_sqft = product.iloc[0]['Installation Cost per Sq Ft']

    # Calculate total cost
    total_cost = (price_per_sqft + install_cost_per_sqft) * area

    # Apply minimum charge if area < 1000 sq ft
    if area < 1000:
        total_cost = max(total_cost, 250)
    
    return f"The estimated cost for {area} sq ft of {flooring_type} flooring is ${total_cost:.2f}."

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '')  # Extract user input from request

    # Messages format for ChatCompletion
    messages = [
        {"role": "system", "content": "You are a helpful flooring assistant chatbot. Provide product information and cost estimates."},
        {"role": "user", "content": f"The flooring data is:\n{flooring_data.to_string(index=False)}\n\nUser query: {user_input}"}
    ]

    try:
        # Call the OpenAI Chat API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Replace deprecated model with gpt-3.5-turbo
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What are some tips for home flooring installation?"}
            ],
            max_tokens=200,
            temperature=0.7
        )
        # Extract response content
        assistant_reply = response['choices'][0]['message']['content'].strip()
        return jsonify({"response": assistant_reply})

    except Exception as e:
        return jsonify({"response": f"Error processing your request: {e}"})

if __name__ == '__main__':
    # Get the port from the environment variable (default to 5000 if not set)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)