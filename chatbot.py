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

@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '').lower()
    response = ""

    # Parse user input using GPT for intent recognition
    try:
        gpt_response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a natural language processor. Extract intents from user input related to flooring products, installation costs, or general questions."},
                {"role": "user", "content": f"Extract intent: {user_input}"}
            ],
            max_tokens=100,
            temperature=0.3
        )
        intent = gpt_response['choices'][0]['message']['content'].strip().lower()

    except Exception as e:
        response = "Sorry, I couldn't understand your request. Please try again."
        return jsonify({"response": response})

    # Handling intents based on extracted input
    if "flooring types" in intent or "products" in intent:
        # Return list of flooring types
        flooring_types = flooring_data['Type'].unique()
        response = f"We offer the following flooring types: {', '.join(flooring_types)}."

    elif "price" in intent or "cost" in intent:
        # Extract flooring type and area size for cost calculation
        flooring_type = None
        area_size = None

        # Use GPT to extract flooring type and area size from user input
        try:
            extraction_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extract flooring type and area size from the user's message."},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=50,
                temperature=0.3
            )
            extracted_data = extraction_response['choices'][0]['message']['content'].strip()
            # Example output: "Flooring type: Hardwood, Area size: 600 sq ft"
            flooring_type = extracted_data.split(",")[0].split(":")[-1].strip().lower()
            area_size = int(extracted_data.split(",")[1].split(":")[-1].strip().split()[0])
        except:
            response = "Please specify the flooring type and the size of the area in square feet."
            return jsonify({"response": response})

        # Find the flooring type in the CSV
        product = flooring_data[flooring_data['Type'].str.lower() == flooring_type]
        if product.empty:
            response = f"Sorry, we don't have flooring type '{flooring_type}'. Please choose from {', '.join(flooring_data['Type'].unique())}."
        else:
            # Calculate cost
            price_per_sqft = product.iloc[0]['Price per Sq Ft']
            install_cost_per_sqft = product.iloc[0]['Installation Cost per Sq Ft']
            total_cost = (price_per_sqft + install_cost_per_sqft) * area_size
            if area_size < 1000:
                total_cost = max(total_cost, 250)
            response = f"The estimated cost for {area_size} sq ft of {flooring_type} flooring is ${total_cost:.2f}."

    elif "tips" in intent or "installation" in intent:
        # Return installation tips
        response = (
            "Here are some tips for flooring installation:\n"
            "1. Make sure the subfloor is clean, level, and dry.\n"
            "2. Acclimate flooring materials to the room's temperature and humidity for 48 hours.\n"
            "3. Leave expansion gaps around the edges.\n"
            "4. Follow the manufacturer's installation instructions."
        )

    else:
        # Default response for unclear intents
        response = "I'm here to help with flooring products, installation costs, or general tips. Please clarify your request."

    return jsonify({"response": response})


if __name__ == '__main__':
    # Get the port from the environment variable (default to 5000 if not set)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)