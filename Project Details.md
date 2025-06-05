# OVERVIEW
This file contains the general information about each of the projects included in this repository
Projects:
    2nd Year Project:
    - Project 3: Team Project (Resturant website build using Django, python, and SQL)
    3rd Year Project:
    - Project 4: Nearest Neighbours Classifier (Machine Learning)
    Final Year Projects:
    - Project 1: Spark Project in python (end-to-end analytics pipeline)
    - Project 2: Elixir Project (Building a paxos implementation for consensus in distributed systems)
    - Final Year MSci Project: https://github.com/J-SMX/ML-algorithm-comparison-fyp
    
    NOTE: Obviously these were not the only courseworks I have done in my 4 years at Royal Holloway, however other courseworks were purely Theory based (Essay writing), or are from 1st or 2nd year and are not worth showing
# Project 1: Team Project CS2810 Backend web dev

Grade Achieved: 71% 

## Overview

The objective of this project was to develop a fully functional website for a restaurant, designed to support all types of users: customers, wait staff, kitchen staff, and management. Key functionality included:

- **Customers**: Browsing the menu, placing orders, and making payments.
- **Wait Staff**: Confirming orders and printing receipts.
- **Kitchen Staff**: Viewing incoming orders and updating order statuses.
- **Management**: Accessing financial reports and tracking order times.

This system was built as a collaborative team effort, with responsibilities divided by file and feature. The code included in this repository represents only the components I personally developed. While my main focus was on backend development, I also contributed minor assistance to the frontend team when needed.

## Implementation

The project stack included **Python**, **SQL**, **Django**, **CSS**, **HTML**, **JavaScript**, and **PostgreSQL**. My primary contributions were in **Python** and **SQL**, specifically:

- Designing and implementing the **database models**.
- Writing **unit tests** to validate the models and their integration with the rest of the system.

In addition to standard models, I developed two **advanced modules**:

- `financial.py`: A custom analytics engine for generating financial reports, averages, trends, and customer metrics using raw SQL and time-based logic.
- `search.py`: A modular, SQL-powered search system capable of filtering users, orders, and menu items, with support for logging and extensibility.

These modules played a central role in supporting data-driven management features and internal staff workflows.


# Project 2: Machine Learning CS3920/CS5920 Nearest Neighbours Classifier Coursework

**Focus**: Implementation of Nearest Neighbour and Conformal Prediction algorithms  
**Language**: Python (Jupyter Notebook)  
**Tools**: NumPy, Matplotlib (no external ML libraries)

## Overview

This project involved implementing the **1-Nearest Neighbour (1-NN)** classification algorithm entirely from scratch, without relying on pre-built machine learning libraries. The coursework emphasized understanding the mechanics of distance-based classification and how such models can be extended with **conformal prediction techniques** to estimate uncertainty in predictions.

Two datasets were used:
- **Iris dataset** – A classic dataset for multi-class classification (3 flower types).
- **Ionosphere dataset** – A binary classification task based on radar signals.

## Tasks

Key tasks included:
- Writing a custom implementation of the **1-NN algorithm**.
- Running and evaluating the model on both datasets.
- Optionally implementing:
  - The **3-NN algorithm** for comparison.
  - A **conformal predictor** using distance-based conformity measures to estimate prediction confidence.


# Project 3: Large-Scale Data Storage and Processing CS4234/5234 Project Overview

Grade Achieved:
  - 90% for main code
  - 92% for report and report code

This project involves building an **end-to-end analytics pipeline** using big data tools to process and analyze the **Enron email dataset**, a real-world corpus containing communications among Enron employees prior to the company's collapse.

## Objectives

- **Data Extraction & Cleaning**: Extract sender-recipient-timestamp triples from raw email data using Spark RDDs. Filter only valid `@enron.com` addresses, remove self-loops, and convert timestamps to UTC `datetime` objects.
  
- **Weighted Network Construction**: Convert the email data into a **directed, weighted graph**, where each edge `(a, b)` represents emails sent from user `a` to `b`. The weight is the number of such emails, optionally filtered by a date range.

- **Degree Analysis**:
  - Calculate **weighted out-degrees** (emails sent) and **in-degrees** (emails received) for each user.
  - Compute **degree distributions**: how many users have each possible in/out-degree.

- **Temporal Analysis**: For each sender, identify the **month (MM/YYYY)** when they contacted the **most distinct recipients**.

## Report Tasks

- **Function Analysis**: Choose one function you implemented; include its code, describe key design decisions, draw its Spark DAG (lineage graph), and identify **narrow vs. wide dependencies**.

- **Network Slice Analysis**: For a 12-month period between Jan 2000–Mar 2002:
  - Test the **80/20 rule** (Pareto principle): Do ~20% of users account for ~80% of communication?
  - Investigate if **max node degree scales** linearly with number of nodes.
  - Evaluate **scale-freeness** by plotting in/out degree distributions on a log-log scale and estimating the **power-law exponent α**.

## Dataset

- Enron email dataset (~0.5M messages) stored in HDFS as Hadoop Sequence Files.
- Use smaller sample datasets for development; run final analysis on the full dataset.


# Project 4: Advanced Distributed Systems CS4860/5860 Paxos Implementation Project Overview

Grade Achieved: 60%

This project centers on implementing the **Paxos distributed consensus algorithm** in **Elixir**, as part of a fault-tolerant, replicated database system for an online flight booking service (FlyWithMe.com). The goal is to ensure that even in the presence of concurrent requests and process failures, consensus is reached on which user successfully reserves a seat.

## Project Context

FlyWithMe.com needs a system where:
- Reservation data is replicated across nodes for availability.
- Seat reservations must be conflict-free even with concurrent proposals.
- The system continues to operate as long as a **majority of nodes** are functional.

To meet these requirements, you must implement a **Paxos protocol layer**.

## Implementation Requirements

You are required to complete the `paxos.ex` Elixir file to support the following operations:

- `start(name, participants, upper)`: Starts a Paxos process and registers it.
- `propose(pid, value)`: Submits a value for consensus (does nothing until `start_ballot` is called).
- `start_ballot(pid)`: Triggers the 2-phase Paxos protocol as leader.

This involves handling:
- Proposal registration and ballot initiation.
- Majority quorum detection.
- Leader election and value agreement.

## Evaluation Goals

Your implementation will be tested against a suite of unit and integration tests. Marks are awarded based on the following capabilities:

- **Basic Protocol**: Correct handling of Paxos phases with concurrent ballots.
- **Crash Fault Tolerance**: Proper behavior in the event of leader or follower failure.
- **Distributed Operation**: Working correctly across multiple physical nodes.

