from flask import Flask, request, jsonify
from flask_restful import Resource, Api, abort
from datetime import datetime

app = Flask(__name__)
api = Api(app)

service_memory = {}


def handle_no_user(user):
    """Helper method to handle case when user not in service memory."""
    abort(404, message=f'User {user} does not exist')

def handle_point_limit(user):
    """Helper method to handle case when trying to deduct too many points /
     adding too many negative points to company"""
    abort(422, message=f'User {user} cannot deduct these points')


class Add(Resource):
    """Manages route which adds points to specific user"""

    def put(self, user):
        """Add points request handler"""
        data = request.get_json()
        # Add user if not in memory
        if user not in service_memory:
            service_memory[user] = {
                'totals': {},
                'transactions': []
            }

        # Add points to total company points
        if data['company'] not in service_memory[user]['totals']:
            if data['points'] < 0:
                handle_point_limit(user)
            service_memory[user]['totals'][data['company']] = data['points']
        else:
            total_points = sum(v for k, v in service_memory[user]['totals']
                               .items())
            if total_points + data['points'] < 0:
                handle_point_limit(user)
            service_memory[user]['totals'][data['company']] += data['points']

        data['transactionDate'] = datetime.strptime(data['transactionDate'],
                                                    '%m/%d/%y %I:%M%p')
        # Check if positive points. If negative, not adding to transactions
        if data['points'] >= 0:
            service_memory[user]['transactions'].append(data)
        else:
            self.handle_negative_points(user, data['points'], data['company'],
                                        data['transactionDate'])
        return '', 201


    def handle_negative_points(self, user, points, company, date):
        """Helper method for handling case of negative points being added"""
        service_memory[user]['transactions'].sort(
            key=lambda i: i['transactionDate'])
        tran_list = service_memory[user]['transactions']

        # Loop through transactions and deduct most recent points
        for i in reversed(range(len(tran_list))):
            curr_company = tran_list[i]['company']
            curr_points = tran_list[i]['points']
            curr_date = tran_list[i]['transactionDate']

            # If companies match and transaction is older, subtract from
            # transaction
            if curr_company == company and curr_date < date:
                if curr_points < -points:
                    points += curr_points
                    del tran_list[i]
                elif curr_points == points:
                    del tran_list
                    break
                else:
                    tran_list[i]['points'] += points
                    break


class Deduct(Resource):
    """Manages route which deducts points from specific user"""

    def put(self, user, amount):
        """Deduct points request handler"""
        if user not in service_memory:
            handle_no_user(user)

        service_memory[user]['transactions'].sort(
            key=lambda i: i['transactionDate'])
        tran_list = service_memory[user]['transactions']
        company_totals = service_memory[user]['totals']

        # Return error if trying to deduct too many points
        total_points = sum(v for k, v in company_totals.items())
        if amount > total_points:
            handle_point_limit(user)

        # Calculate deductions
        deductions = self.determine_deductions(tran_list, company_totals, amount)

        curr_datetime = datetime.strftime(datetime.now(), '%m/%d/%y %I:%M%p')
        deductions_list = [{'company': k, 'points': -v,
                            'deductionDate': curr_datetime} for k, v in
                           deductions.items()]
        response = jsonify(deductions_list)

        return response

    def determine_deductions(self, tran_list, company_totals, amount):
        """Helper method for determining appropriate point deductions to be
        made based on business logic"""
        deductions = {}

        # Loop through list of transactions
        for i in range(len(tran_list)):
            curr_company = tran_list[i]['company']
            curr_points = tran_list[i]['points']
            # Check if transaction company total points > 0
            if company_totals[curr_company] > 0:
                # If transaction amount less than deduction amount, subtract
                # all of transaction amount and delete from list
                if curr_points < amount:
                    company_totals[curr_company] -= curr_points
                    amount -= curr_points
                    tran_list[i]['points'] = 0
                    # Add transaction amount to response
                    if curr_company not in deductions:
                        deductions[curr_company] = curr_points
                    else:
                        deductions[curr_company] += curr_points
                # Otherwise transaction amount >= deduction amount. Subtract
                # remaining deduction amount from transaction (or delete) and
                # end loop
                else:
                    company_totals[curr_company] -= amount
                    if curr_points == amount:
                        tran_list[i]['points'] = 0
                    else:
                        tran_list[i]['points'] -= amount
                    # Add transaction amount to response
                    if curr_company not in deductions:
                        deductions[curr_company] = amount
                    else:
                        deductions[curr_company] += amount
                    break
        # Remove transaction points from memory if at 0
        for tran in tran_list:
            if tran['points'] == 0:
                tran_list.remove(tran)

        return deductions


class Balance(Resource):
    """Manages route for returning point balance for specific user"""

    def get(self, user):
        """Handles get balance request"""
        if user not in service_memory:
            handle_no_user(user)
        return service_memory[user]['totals']


api.add_resource(Add, '/<string:user>/add')
api.add_resource(Deduct, '/<string:user>/deduct/<int:amount>')
api.add_resource(Balance, '/<string:user>/balance')

if __name__ == '__main__':
    app.run(host="localhost", port=5001)