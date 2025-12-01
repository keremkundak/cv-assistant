# CV Assistant - Digital Twin

This project is a Streamlit-based application that serves as a "Digital Twin" for Kerem Kundak. It allows recruiters and colleagues to interact with an AI representation of Kerem to learn about his professional background, skills, and projects.

## Features

- **Digital Twin Persona:** The AI speaks in the first person ("I", "me"), acting as Kerem himself based on his CV.
- **Context Injection:** Directly injects the full CV text into the LLM's system prompt to ensure comprehensive and accurate answers without retrieval loss.
- **Multi-language Support:** Supports English and Turkish, automatically adapting to the user's language preference.
- **Interactive UI:** Features a modern, dark-themed interface with glassmorphism effects.
- **Email Notifications:** Sends transcripts of conversations to Kerem for review.
- **Privacy Focused:** Includes a KVKK (Personal Data Protection) consent flow for visitors.

## Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/keremkundak/cv-assistant.git
    cd cv-assistant
    ```

2.  Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

This application requires several API keys and secrets to function. Create a `.streamlit/secrets.toml` file in the project root with the following structure:

```toml
GOOGLE_API_KEY = "your_google_api_key"
EMAIL_ADDRESS = "your_email@gmail.com"
EMAIL_PASSWORD = "your_email_app_password"
TARGET_EMAIL = "target_email@example.com"
CV_ENCRYPTION_KEY = "your_encryption_key"
```

## Contact

- **LinkedIn:** [www.linkedin.com/in/kerem-kundak](https://www.linkedin.com/in/kerem-kundak)
- **GitHub:** [www.github.com/keremkundak](https://github.com/keremkundak)
- **Email:** keremkundak@gmail.com

## Usage

Run the Streamlit application:

```bash
streamlit run app.py
```

The application will open in your default web browser.

## Project Structure

- `app.py`: Main application logic and UI layout.
- `assets/`: Contains CSS styles and images.
- `utils/`: Helper functions for text assets, email sending, and data loading.
- `requirements.txt`: Python dependencies.
