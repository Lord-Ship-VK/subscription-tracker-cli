# SmartSub: Problem Statement

## Background & Context
In the modern digital economy, individuals rely heavily on recurring subscription services for entertainment, education, productivity, cloud storage, and software. As the number of subscriptions grows, it becomes increasingly difficult for consumers to track billing cycles, monitor total monthly and yearly expenditure, and identify unused services. The lack of a centralized tracking mechanism often leads to "subscription fatigue" and unintended financial drain from auto-renewing services.

## Objectives
The primary objective of this project is to develop a lightweight, secure, and user-friendly command-line tool that allows users to manage their recurring expenses efficiently. The tool must operate entirely locally without requiring external databases or internet connectivity, ensuring data privacy.

## Scope
The scope of the project includes:
- A command-line interface (CLI) for managing subscriptions (CRUD operations).
- Persistent local storage using human-readable JSON.
- Automated categorization and analytics of spending.
- Automated handling of renewal dates (including month-end and leap-year edge cases).
- A safe "savings analyzer" to evaluate hypothetical cancellations.
- Search and filtering capabilities.
- Export functionality for generating CSV reports.
- Comprehensive unit testing ensuring robust edge-case handling.

The scope explicitly **excludes**:
- Cloud synchronization or remote databases.
- Multi-user authentication.
- Graphical User Interfaces (GUI) or web frontends.
- Direct integration with bank APIs or payment gateways.

## Target Users
- Students managing limited budgets and student discounts.
- Professionals managing software and productivity subscriptions.
- Individuals seeking to gain clarity on their recurring personal expenses without uploading their financial data to a third-party cloud service.

## Proposed SmartSub Solution
SmartSub is a terminal-based Subscription Expense Tracker & Analyzer built purely with the Python Standard Library. It acts as a local repository for all subscription data. 

## High-Level Features
- **Subscription Management**: Add, update, view, and delete subscription records.
- **Categorization**: Enforces strict categorization (e.g., Entertainment, Software, Cloud Storage) to help group expenses.
- **Expense Analytics**: Converts mixed billing cycles (monthly/yearly) into normalized monthly and yearly equivalent costs, providing an immediate overview of financial commitment.
- **Renewal Alerts**: Detects and highlights subscriptions renewing within a 7-day window.
- **Automated Date Advancement**: Automatically rolls over past renewal dates to the next valid billing cycle, handling calendar anomalies like February 29th and 31-day months.
- **Hypothetical Savings**: Calculates potential savings interactively before the user commits to deleting any records.
- **Data Export**: Generates clean CSV reports for external use in spreadsheets.
