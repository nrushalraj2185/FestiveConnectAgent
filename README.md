# Festive Connect Agent

## 📘 Project Overview
An AgenicAI based online web app designed to keep users updated on festival-related activities and announcements. This app will provide real-time updates on event schedules, performer lineups, and exclusive festival content. With FestiveConnectAgent Users can interact naturally with AI Agent to access venue maps for easy navigation and integrated social features to connect with fellow attendees. The goal of FestiveConnectAgent is to enhance the festival experience by offering timely information and interactive features, all accessible from a single, user-friendly App.

Follow the steps below to set up and run the backend application.

## 🚀 Steps to Start the Backend App

1. **Navigate to the backend directory**  
   ```bash
   cd /workspace/festive_connect_agent/backend
   ```

2. **Install the required dependencies**  
   Before running the application, install all necessary Python packages using:  
   ```bash
   pip install -r requirements.txt
   ```

3. **Create Google AI Studio Key**
   Visit https://aistudio.google.com/ using your personal gmail id and create an API Key. If you are a first time user you might have to create a new project in https://console.cloud.google.com/ first , import it here and then create API Key.

4. **Update env with Google AI Studio Key**
   Once the key is created copy the key value and update the below variable in .env file.
   GOOGLE_API_KEY=<GET_KEY_FROM_https://aistudio.google.com/api-keys>

3. **Run the backend server**  
   Once the dependencies are installed, start the application with:  
   ```bash
   python main.py
   ```

## 🚀 Steps to Start the Frontend App

1. Find the `index.html` file inside the **frontend** directory.

2. **Configure the backend connection**  
   - Ensure that the **backend server** is up and running.  
   - Open the `apiService.js` file (usually located inside the `js` or `services` folder).
   - Get the host URL or API base URL from the Endpoints (Plug Icon) in the leftside panel and look for 8080 Port.  
   - Update the **host URL** or **API base URL** to match your backend’s running address.  
     Example:  
     ```js
     const API_CONFIG = {
         baseURL: "https://8080-kode-ws-049033f1d.hebbale.academy",
         headers: {
         "Content-Type": "application/json",
         },
      };
     ```

3. **Start the frontend app**  
   - Right-click on `index.html`.  
   - Choose **"Open with Live Server"** (available in VS Code or similar editors).  
   - The application will automatically open in your default web browser.