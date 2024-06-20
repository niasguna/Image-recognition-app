from flask import Flask, request, render_template, url_for
from PIL import Image
import openai
import io
import base64
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'uploads')

# Read the OpenAI API key from the environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_description(image):
    # Generate description using OpenAI GPT-4 Turbo
    description = "The image description could not be generated."
    try:
        # Convert image to bytes
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

        # Create a prompt for the GPT model
        prompt = f"Describe the following image encoded in base64: {img_str}"

        # Use OpenAI API to generate description
        response = openai.Completion.create(
            model="gpt-4-turbo",
            prompt=prompt,
            max_tokens=100
        )

        # Extract description from response
        description = response.choices[0].text.strip()

    except Exception as e:
        print(f"Error generating description: {str(e)}")

    return description

@app.route('/', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            # Save the uploaded file to a temporary location
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            
            # Open the saved image
            image = Image.open(file_path)
            
            # Generate description using OpenAI
            description = generate_description(image)
            
            # Remove the temporary file
            os.remove(file_path)
            
            # Render the result page with the image URL and description
            return render_template('result.html', image_url=url_for('static', filename=f'uploads/{file.filename}'), description=description)
    
    # Render the upload page by default (GET request)
    return render_template('upload.html')

if __name__ == '__main__':
    # Ensure the uploads directory exists
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    
    # Check if API key is set
    if not openai.api_key:
        raise ValueError("No OpenAI API key found. Set the OPENAI_API_KEY environment variable.")
    
    app.run(debug=True)
