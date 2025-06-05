# Project 1: Large-Scale Data Storage and Processing CS4234/5234 Project Overview

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

## Skills Demonstrated

- Real-world data cleaning and parsing.
- Distributed computation with Spark RDDs (no DataFrames/SparkSQL).
- Graph-based analysis of communication patterns.
- Statistical and visual analysis of large-scale network structure.

## Dataset

- Enron email dataset (~0.5M messages) stored in HDFS as Hadoop Sequence Files.
- Use smaller sample datasets for development; run final analysis on the full dataset.

## Tools & Constraints

- Language: Python (RDD API only)
- Environment: Spark on the `bigdata` cluster
- No generative AI usage permitted


# Project 2: Advanced Distributed Systems CS4860/5860 Paxos Implementation Project Overview

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

## Objective

Demonstrate your understanding of **distributed agreement under failure**, and your ability to translate a foundational distributed algorithm into working, testable code using real-world tools.

