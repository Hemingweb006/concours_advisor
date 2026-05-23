# Concours Advisor AI Agent

Concours Advisor is an intelligent AI agent engineered to assist Moroccan students in preparing for post-bac competitive exams, including ENSA, ENSAM, and Medecine. By leveraging historical exam data and advanced large language models, this system provides personalized study paths, targeted practice sessions, and in-depth performance analysis.

The system utilizes Groq AI to deliver high-speed inference, allowing for rapid interaction and feedback during your study sessions.

## Key Features

* Targeted Practice: Focus your preparation by selecting specific schools or institutions to work on.
* Year-Based Organization: Systematically work through past concours by academic year.
* Adaptive Learning: The agent evaluates your performance and proposes practice problems based on your specific areas of difficulty.
* Automated OCR: A dedicated OCR module processes your PDF collection, converting raw exam papers into machine-readable text for the AI.
* High-Performance Inference: Powered by Groq AI, ensuring lightning-fast responses while you study.

## Prerequisites

* Python 3.x
* Tesseract OCR (Installed and configured on your system)
* Poppler (Required for PDF to image conversion)
* Groq API Key (You can obtain one for free at the Groq Cloud console)

## Setup Instructions

### 1. Installation
First, ensure you have the requirements installed:

pip install -r requirements.txt

### 2. Project Structure
To ensure the system correctly indexes your materials, organize your concours directory as follows:

concours/
  ENSA/
    Ensa 2019.txt
    Ensa 2020.txt
  ENSAM/
    Ensam 2020.txt
    Ensam 2024.txt
  Medecine/
    Medecine 2021.txt
    Medecine 2025.txt

### 3. Configuration
Create a file named .env in the root directory of your project. Add your Groq API key to this file:

GROQ_API_KEY=your_actual_api_key_here

### 4. Data Processing
Run the included OCR script to convert your PDF library into indexable text files:

python3 ocr.py

The script will detect the files in your concours folder structure and generate corresponding text files, which the AI agent will then utilize to provide feedback, explanations, and mock exam variants.

## Why Concours Advisor?

Concours Advisor transforms static PDF archives into an active, dynamic learning partner. Instead of simply reading past papers, you engage with an agent that understands the pedagogical nuances of the professors who created them, allowing for a more efficient and targeted revision process.
