# WAF-SMASHER v2.0

WAF-SMASHER is a web-based Capture The Flag (CTF) challenge focused on exploiting Server-Side Template Injection (SSTI) vulnerabilities in a Flask application. The challenge features four distinct stages, each with an increasingly sophisticated Web Application Firewall (WAF) that players must bypass to extract the final flag.

This project is designed for educational purposes to help developers and security enthusiasts understand, identify, and mitigate SSTI vulnerabilities.

![Screenshot](screenshot.png) 
*(You should add your own screenshot.png file to the project!)*

## Features

-   **4 Themed Stages:** Progress through systems with escalating difficulty.
-   **Interactive Terminal UI:** A retro "hacker terminal" aesthetic provides an engaging user experience.
-   **Realistic WAF Bypasses:** The challenges are based on real-world SSTI exploit chains and WAF evasion techniques.
-   **Flask & Jinja2:** Built with a popular and easy-to-understand Python web framework.

## Setup and Installation

This project is built with Python and Flask.

### Prerequisites

-   Python 3.6+
-   `pip` for installing packages

### Local Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/waf-smasher.git
    cd waf-smasher
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required packages:**
    ```bash
    pip install Flask
    ```

4.  **Run the application:**
    ```bash
    python app.py
    ```

    The application will now be running at `http://127.0.0.1:5000`.

### Docker Setup

For an isolated and consistent environment, you can use the provided `Dockerfile`.

1.  **Build the Docker image:**
    ```bash
    docker build -t waf-smasher .
    ```

2.  **Run the Docker container:**
    ```bash
    docker run -p 5000:5000 --rm --name waf-smasher-container waf-smasher
    ```
    The application will be accessible at `http://127.0.0.1:5000`.

## Challenge Solutions

**(SPOILER ALERT: The solutions are available in the repository if you get stuck.)**
The definitive solutions are provided in the `solutions.md` file. It's recommended to try solving the challenges on your own first!

## Security Notes

This application is **intentionally vulnerable** to SSTI for educational purposes. **DO NOT** deploy this application in a production environment or on a publicly accessible server without proper sandboxing and security measures. The debug mode is enabled by default for ease of use but should be disabled in any non-local setting.