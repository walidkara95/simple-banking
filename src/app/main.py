from fastapi import FastAPI, status, Response, Request
from .models import Transaction
from .core import core
from .logger import log_api_error, log_api_request

app = FastAPI()

@app.post("/reset", status_code=status.HTTP_200_OK)
def reset_state():
    log_api_request(endpoint="/reset")
    core.reset_state()
    return Response(content="OK", status_code=status.HTTP_200_OK)

@app.get("/balance")
def get_balance(account_id: str, response: Response):
    log_api_request(endpoint="/balance", request_data={"account_id": account_id})
    account = core.get_account_balance(account_id)
    if account is None:
        log_api_error(
            endpoint="/balance", 
            error_type="account_not_found", 
            details={"account_id": account_id}
        )
        response.status_code = status.HTTP_404_NOT_FOUND
        return 0
    return account.balance
    
@app.post("/event", status_code=201)
def post_event(transaction: Transaction, response: Response):
        log_api_request(
            endpoint="/event", 
            request_data={
                "type": transaction.type,
                "amount": transaction.amount,
                "origin": transaction.origin,
                "destination": transaction.destination
            }
        )
        
        strategy_map = {
            "deposit": process_deposit,
            "withdraw": process_withdraw,
            "transfer": process_transfer,
        }

        process_func = strategy_map.get(transaction.type)

        if process_func is None:
            log_api_error(
                endpoint="/event",
                error_type="invalid_transaction_type",
                details={"type": transaction.type}
            )
            response.status_code = status.HTTP_400_BAD_REQUEST
            return response

        return process_func(transaction, response)

def process_deposit(transaction, response: Response):
    account = core.create_or_update_account(transaction.destination, transaction.amount)
    return {"destination": account}

def process_withdraw(transaction, response: Response):
    account = core.withdraw_from_account(transaction.origin, transaction.amount)
    if account is None: 
        log_api_error(
            endpoint="/event (withdraw)",
            error_type="insufficient_funds_or_account_not_found",
            details={
                "origin": transaction.origin,
                "amount": transaction.amount
            }
        )
        response.status_code = status.HTTP_404_NOT_FOUND
        return 0
    return {"origin": account}

def process_transfer(transaction, response: Response):
    origin, destination = core.transfer_between_accounts(transaction.origin, transaction.destination, transaction.amount)
    if origin is None:
        log_api_error(
            endpoint="/event (transfer)",
            error_type="insufficient_funds_or_account_not_found",
            details={
                "origin": transaction.origin,
                "destination": transaction.destination,
                "amount": transaction.amount
            }
        )
        response.status_code = status.HTTP_404_NOT_FOUND
        return 0
    return {"origin": origin, "destination": destination}
