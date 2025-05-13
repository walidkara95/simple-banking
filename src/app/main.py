from fastapi import FastAPI, status, Response
from .models import Transaction
from .core import core
from .logging_config import logger, log_api_error

app = FastAPI()

@app.post("/reset", status_code=status.HTTP_200_OK)
def reset_state():
    core.reset_state()
    return Response(content="OK", status_code=status.HTTP_200_OK)

@app.get("/balance")
def get_balance(account_id: str, response: Response):
    account = core.get_account_balance(account_id)
    if account is None:
        log_api_error("/balance", "NOT_FOUND", f"Account {account_id} not found", {"account_id": account_id})
        response.status_code = status.HTTP_404_NOT_FOUND
        return 0
    return account.balance
    
@app.post("/event", status_code=201)
def post_event(transaction: Transaction, response: Response):
        strategy_map = {
            "deposit": process_deposit,
            "withdraw": process_withdraw,
            "transfer": process_transfer,
        }

        process_func = strategy_map.get(transaction.type)

        if process_func is None:
            log_api_error(
                "/event", 
                "BAD_REQUEST", 
                f"Invalid transaction type: {transaction.type}",
                transaction.dict()
            )
            response.status_code = status.HTTP_400_BAD_REQUEST
            return response

        return process_func(transaction, response)

def process_deposit(transaction, response: Response):
    account = core.create_or_update_account(transaction.destination, transaction.amount)
    logger.info(f"Deposit successful - Account: {transaction.destination}, Amount: {transaction.amount}")
    return {"destination": account}

def process_withdraw(transaction, response: Response):
    account = core.withdraw_from_account(transaction.origin, transaction.amount)
    if account is None: 
        error_detail = f"Account {transaction.origin} not found or has insufficient funds"
        log_api_error("/event (withdraw)", "NOT_FOUND", error_detail, transaction.dict())
        response.status_code = status.HTTP_404_NOT_FOUND
        return 0
    return {"origin": account}

def process_transfer(transaction, response: Response):
    origin, destination = core.transfer_between_accounts(transaction.origin, transaction.destination, transaction.amount)
    if origin is None:
        error_detail = f"Account {transaction.origin} not found or has insufficient funds"
        log_api_error("/event (transfer)", "NOT_FOUND", error_detail, transaction.dict())
        response.status_code = status.HTTP_404_NOT_FOUND
        return 0
    return {"origin": origin, "destination": destination}
