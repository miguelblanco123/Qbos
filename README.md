# Mexican Speedcubing Competition Tools

This repository aims to develop tools for Mexican speedcubing competition organizers, enabling them to streamline their workflow and organize competitions more efficiently.

## Schedule Generator

The Schedule Generator is a Streamlit web application designed to help competition organizers create optimal schedules for WCA (World Cube Association) competitions. This tool simplifies the complex process of planning multi-day cubing competitions by automating schedule creation while adhering to WCA regulations.

### Key Features

- **Dynamic Event Selection**: Choose from 17 official WCA events including 3x3, 2x2, 4x4, and other puzzle categories
- **Competitor-based Calculations**: 
  - Automatically calculates required number of solving stations
  - Estimates participants per event based on historical registration data
  - Adjusts schedule based on total competitor count
- **Flexible Schedule Configuration**:
  - Support for 1-3 day competitions
  - Customizable daily start and end times
  - Automatic lunch break scheduling
  - Built-in registration period and prize giving ceremony
- **Advanced Round Management**:
  - Configure multiple rounds per event (up to 4, based on WCA regulations)
  - Set cutoff times for events
  - Customize advancement percentages between rounds
  - Special handling for finals with adjustable competitor counts
- **Smart Scheduling Logic**:
  - Optimizes event ordering
  - Ensures adequate time between rounds
  - Handles special events like FMC appropriately
  - Prioritizes main event placement
- **Comprehensive Output**:
  - Detailed competitor estimates per event
  - Visual schedule display with timing breakdowns
  - Scheduling recommendations and warnings
  - Raw schedule data export capability

### Event Settings

For each selected event, organizers can configure:
- Number of rounds (automatically limited based on competitor count)
- Cutoff times in MM:SS format
- Advancement percentages between rounds
- Final round sizes

### Time Management

The tool includes:
- Accurate time estimates for each round based on:
  - Number of competitors
  - Available stations
  - Event format (Ao5, Mo3, etc.)
  - Scramble times
  - Group sizes
- Built-in buffer times for registration and ceremonies
- Automatic scheduling of breaks

### Usage Requirements

The application is built with:
- Streamlit
- Pandas
- Python's datetime module
- Math utilities for various calculations

To use the tool, simply select your events, input the number of competitors, configure your competition days, and adjust settings as needed. The schedule will automatically update based on your inputs.