# SocGen-IronCrypt
# Cyber Risk Visualizer


The Cyber Risk Visualizer is a comprehensive dashboard designed to provide a real-time, interactive view of your organization's cybersecurity posture. It aggregates vulnerability data, visualizes asset locations, manages patching, and offers intelligent assistance to help security teams identify, prioritize, and remediate threats effectively.

## ✨ Features

*   **Vulnerability Dashboard**: An overview of all identified vulnerabilities, sortable and filterable by severity, asset, and status.
*   **Office Floorplan Visualizer**: An interactive map of your office, showing the physical location of assets and their current risk status.
*   **Patch Management**: A centralized view for tracking and deploying patches to vulnerable systems.
*   **AI Assistant**: An integrated chatbot to help with queries and guide you through remediation steps.
*   **Data Import/Export**: Easily import asset data and export visualizations and reports.
*   **Responsive Design**: A modern, responsive UI that works on all devices.

## 🛠️ Tech Stack

*   **Frontend**:
    *   React
    *   TypeScript
    *   Vite
    *   Tailwind CSS
    *   shadcn/ui
    *   Recharts
*   **Backend**:
    *   Python
    *   Flask
    *   Pandas
*   **Deployment & Orchestration**:
    *   Docker
    *   Ansible

## 🚀 Getting Started

Follow these instructions to get the project up and running on your local machine.

### Prerequisites

Make sure you have the following installed:

*   [Node.js](https://nodejs.org/) (v18 or later)
*   [Python](https://www.python.org/) (v3.9 or later) & `pip`
*   [Docker](https://www.docker.com/get-started)
*   [Ansible](https://docs.ansible.com/ansible/latest/installation_guide/intro_installation.html)
*   [Bun](https://bun.sh/) (Optional, for frontend package management)

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd <repository-directory>
    ```

2.  **Set up the Backend:**

    *   Create a virtual environment:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    *   Install Python dependencies:
        ```bash
        pip install -r requirements.txt
        ```

3.  **Set up the Frontend:**

    *   Navigate to the frontend directory:
        ```bash
        cd cyber-risk-visualizer-main
        ```
    *   Install Node.js dependencies:
        ```bash
        npm install
        ```
        or if using Bun:
        ```bash
        bun install
        ```

### Running the Application

1.  **Start the Backend Server:**
    Open a terminal, navigate to the project root, activate the virtual environment, and run:
    ```bash
    source venv/bin/activate
    flask run
    ```
    The backend API will be running on `http://127.0.0.1:5000`.

2.  **Start the Frontend Development Server:**
    In a separate terminal, navigate to the `cyber-risk-visualizer-main` directory and run:
    ```bash
    npm run dev
    ```
    The application will be accessible at `http://localhost:5173`.

### Docker Setup (Alternative)

You can also run the entire application using Docker.

1.  **Build the Docker image:**
    ```bash
    docker build -t cyber-risk-visualizer .
    ```

2.  **Run the Docker container:**
    ```bash
    docker run -p 5173:80 cyber-risk-visualizer
    ```
    The application will be available at `http://localhost:5173`.


## 🤝 Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## 📄 License

This project is licensed under the MIT License. See the `LICENSE` file for details.

Collaborators-
Sankalp Chaudhary
Aarya Prasad Pai 
Roshan John 

