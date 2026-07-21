# Expected Output

The application prints a series of messages demonstrating the task manager functionality. The exact output is:

```
=== Personal Task Manager ===
Adding tasks...
All tasks:
ID: 1 Title: Complete project report
  Priority: High
  Category: Work
  Due: 2024-12-31
  Notes: Write the Q4 report
  Status: Pending
---
ID: 2 Title: Buy groceries
  Priority: Medium
  Category: Personal
  Due: 2024-12-25
  Notes: Milk, eggs, bread
  Status: Pending
---
ID: 3 Title: Schedule dentist appointment
  Priority: Low
  Category: Health
  Due: 2025-01-15
  Notes: Annual checkup
  Status: Pending
---
ID: 4 Title: Review code
  Priority: High
  Category: Work
  Due: 2024-12-20
  Notes: Review PR #123
  Status: Pending
---
ID: 5 Title: Call mom
  Priority: Medium
  Category: Personal
  Due: 2024-12-22
  Notes: Weekly call
  Status: Pending
---
Editing task 2...
Completing task 2...
Setting task 1 back to pending...
Searching for Work...
Found 2 tasks
=== Task Statistics ===
Total tasks: 5
Completed tasks: 1
Pending tasks: 4
High priority: 3
Medium priority: 1
Low priority: 1
Saving to JSON...
Saved to tasks.json
Loading from JSON...
Loaded 5 tasks
Exporting to CSV...
CSV content preview:
1,Complete project report,High,Work,2024-12-31,Write the Q4 report,False
2,Buy groceries and cook dinner,High,Personal,2024-12-25,"Milk, eggs, bread",True
3,Schedule dentist appointment,Low,Health,2025-01-15,Annual checkup,False
4,Review code,High,Work,2024-12-20,Review PR #123,False
5,Call mom,Medium,Personal,2024-12-22,Weekly call,False

Deleting task 3...
Final task count: 4
```
