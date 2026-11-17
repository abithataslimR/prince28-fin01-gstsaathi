# GSTSaathi - Requirements

## 1. Functional Requirements

1. The system must answer at least 10 common GST-related questions using official government sources.

2. The system must identify the GST rate for a given HSN code and date.

3. The system must display the relevant GST notification number and effective date for every rate-related answer.

4. The system must allow users to retrieve GST documents using their document ID.

5. The system must identify missing or mismatched purchase invoices during reconciliation.

## 2. Non-Functional Requirements

1. The system must achieve at least 95% correctness on 50 HSN-date test cases.

2. The API must respond to 95% of normal requests within 2 seconds.

3. The system must support at least 20 simultaneous users.

4. The system must return structured error responses for invalid requests.

5. Every API request must have a unique request ID for tracking and debugging.
