from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from flask import Blueprint, request
from flask.json import jsonify
from werkzeug.security import check_password_hash
from src.models import User, Accounts, Transactions, db
from src.constants.handle_authentication import authentication
import requests

account = Blueprint("accounts", __name__, url_prefix="/api/accounts")


@account.route("/", methods=['GET', 'POST', 'PUT', 'DELETE'])
def handle_accounts():
    if request.method == 'GET':
        email = request.headers.get('email')
        password = request.headers.get('password')
        if not email or not password:
            return jsonify({"error": "email and password are required"}), HTTP_400_BAD_REQUEST
        else:
            user = User.query.filter_by(email=email).first()

            if user is None:
                return jsonify({"error": "user does not exist"}), HTTP_404_NOT_FOUND
            else:
                # check if password is correct
                if check_password_hash(user.password, password):
                    
                    accounts = Accounts.query.all()
                

                    data = []

                    for account in accounts:
                        data.append({
                            'id': account.id,
                            'account_number': account.account_number,
                            'account_balance': account.account_balance,
                            'user_id': account.user_id,
                        })


                    return jsonify({'data': data}), HTTP_200_OK
                else:
                    return jsonify({"error": "password is incorrect"}), HTTP_400_BAD_REQUEST
    elif request.method == 'POST':
        # check if email and password are available in the header and validate if they are available
        email = request.headers.get('email')
        password = request.headers.get('password')

        if not email or not password:
            return jsonify({"error": "email and password are required"}), HTTP_400_BAD_REQUEST
        else:
            # validate credentials
            # get user credential
            user = User.query.filter_by(email=email).first()
            if user is None:
                return jsonify({"error": "user does not exist"}), HTTP_404_NOT_FOUND
            else:
                # check if password is correct
                if check_password_hash(user.password, password):
                    # check if account already created
                    if Accounts.query.filter_by(user_id=user.id).first() is not None:
                        return jsonify({"error": "account already exists"}), HTTP_409_CONFLICT
                    else:
                        # create account
                        account = Accounts(user_id=user.id)
                        db.session.add(account)
                        db.session.commit()
                        return jsonify({
                            "message": "account successfully created",
                            "account_number":account.account_number,
                            "account_balance": account.account_balance,
                            "account_name": user.first_name+" "+user.last_name 
                            }), HTTP_201_CREATED
                else:
                    return jsonify({"error": "password is incorrect"}), HTTP_400_BAD_REQUEST
                
    elif request.method == 'PUT':
        # check if email and password are available in the header and validate if they are available
        email = request.headers.get('email')
        password = request.headers.get('password')
        
        if not email or not password:
            return jsonify({"error": "email and password are required"}), HTTP_400_BAD_REQUEST
        else:
            # validate credentials
            # get user credential
            user = User.query.filter_by(email=email).first()
            if user is None:
                return jsonify({"error": "user does not exist"}), HTTP_404_NOT_FOUND
            else:
                # check if password is correct
                if check_password_hash(user.password, password):
                    # check if account already created
                    if Accounts.query.filter_by(user_id=user.id).first() is not None:
                        account = Accounts.query.filter_by(user_id=user.id).first()
                        account.account_number = request.json.get('account_number')
                        account.account_balance = request.json.get('account_balance')
                        db.session.commit()

                        return jsonify({
                            "message": "account successfully updated",
                            "account_number":account.account_number,
                            "account_balance": account.account_balance,
                        })
                    
        

@account.post("/<int:id>/transactions")
def handle_credit(id):

      if(authentication.handle_auth(request)["is_authenticated"] and authentication.handle_auth(request)["message"] == "validated"):
          id = request.args.get('id')
        #   id = request.args.get('id', default = 1, type = int)
          account = Accounts.query.filter_by(id=id).first()
          if account is None:
              return jsonify({"error": "account does not exist"}), HTTP_404_NOT_FOUND
          else:
              user_id = account.user_id
              amount = request.json.get('amount')
              transaction_type = request.json.get('transaction_type')
              transaction_description = request.json.get('transaction_description')
              ipify = requests.get("https://geo.ipify.org/api/v2/country?apiKey=at_s0RUkyuKK3h8wCKA0pTjjIPDBm7Ns")
              ipify_response = ipify.json
              #account.account_balance = account.account_balance + request.json.get('amount')

              if(transaction_type == "credit"):
                  account.account_balance = account.account_balance + amount
                  db.session.commit()

                  #save transaction
                  transaction = Transactions(
                      user_id=user_id, 
                      transaction_amount=amount, 
                      transaction_type=transaction_type, 
                      transaction_description=transaction_description, 
                      transaction_location=ipify_response.ip
                    )
                  db.session.add(transaction)
                  db.session.commit()
                  return jsonify({
                      "message": "credit successfully added"
                  })
              elif(transaction_type == "debit"):
                  # check if amount is correct
                  if(amount > account.account_balance):
                      return jsonify({"error": "amount exceeds balance"}), HTTP_400_BAD_REQUEST
                  else:
                      account.account_balance = account.account_balance - amount
                      db.session.commit()
                      
                      #save transaction
                      transaction = Transactions(
                          user_id=user_id, 
                          transaction_amount=amount, 
                          transaction_type=transaction_type, 
                          transaction_description=transaction_description, 
                          transaction_location=ipify_response.ip
                        )
                      db.session.add(transaction)
                      db.session.commit()

                      return jsonify({
                          "message": "debit successfully added"
                      })
              else:
                  return jsonify({"error": "invalid transaction type"}), HTTP_400_BAD_REQUEST
              
      else:
          return jsonify({"error": authentication.handle_auth(request)["message"]}), 403
      

@account.post("/<int:id>/list-transactions")
def list_transactions():
    if(authentication.handle_auth(request)["is_authenticated"] and authentication.handle_auth(request)["message"] == "validated"):
        id = request.args.get('id')
        #   id = request.args.get('id', default = 1, type = int)
        account = Accounts.query.filter_by(id=id).first()
        if account is None:
            return jsonify({"error": "account does not exist"}), HTTP_404_NOT_FOUND
        else:
            user_id = account.user_id
            transactions = Transactions.query.filter_by(user_id=user_id).all()
            data = []
            for transaction in transactions:
                data.append({
                    'id': transaction.id,
                    'transaction_amount': transaction.transaction_amount,
                    'transaction_type': transaction.transaction_type,
                    'transaction_description': transaction.transaction_description,
                    'transaction_location': transaction.transaction_location
                })
            return jsonify({'data': data}), HTTP_200_OK