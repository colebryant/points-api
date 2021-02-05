User points system web service built with python flask framework and
flask_restful extension.

To Run Service:

1) Install pip3 / python3 if not already installed: 
   https://www.python.org/downloads/
2) Install dependencies:
    1) flask: run cmd ```pip3 install Flask```
    2) flask_restful: run cmd ```pip3 install flask_restful```
    
3) cd into web service directory and run cmd ```python3 api.py```
    * Web service will begin running on localhost port 5001: 
      http://localhost:5001/

To Interact with Service:
Utilizing tool such as Postman (https://www.postman.com/) or curl, the user 
   can perform add, deduct, and get balance actions as follows:
   
1) Add points to user account for specific payer and date. To perform,
    send PUT request to specific user route http://localhost:5001/[user]/add.
      * Example endpoint: http://localhost:5001/bill/add.
      * Body of message should be in the following exact JSON format:
      
        ```json
        {
            "company": "DANNON",
            "points": 300,
            "transactionDate": "10/31/20 10:00AM"
        }
        ```
        * Note that company is a string, points is an integer, and transactionDate
    is a string of the form "MM/DD/YY HH:MM<AM/PM>"
          
2) Deduct points from a user account. To perform, send PUT request to 
    specific user route with specific amount to deduct:
        http://localhost:5001/[user]/deduct/[amount].
        * Example endpoint: http://localhost:5001/bill/deduct/5000
        * Note that a user must first have points in memory to deduct points
   
3) Return point balance for a specific user per company. To perform,
    send GET request to specific user route
   http://localhost:5001/[user]/balance. 
   * Example endpoint: http://localhost:5001/bill/balance
   * Note that a user must first have points in memory for a list of point
          balances to return

* Notes/ Assumptions:

1) Limiting ability for front end to cause user's total points for a company
   to go negative or to deduct more points than user has in total. Sending an
   error message if this is the case. I am assuming a company's points cannot
   go negative.
   
2) Data being sent to and from the service is in JSON format.
   
3) Utilizing standard hashtable data structure with in service to house service
   memory. No durable data store such as SQL database.
     


