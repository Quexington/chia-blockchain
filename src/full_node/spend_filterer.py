from src.types.spend_bundle import SpendBundle
from src.types.blockchain_format.program import Program
from src.types.blockchain_format.sized_bytes import bytes32
from src.full_node.mempool_check_conditions import get_name_puzzle_conditions
from src.types.condition_opcodes import ConditionOpcode
from typing import Tuple

def filter_spend(transaction: SpendBundle, spend_name: bytes32) -> Tuple[SpendBundle, bytes32]:
    new_coin_solutions = []
    for coin_solution in transaction.coin_solutions:
        save_amount = coin_solution.coin.amount
        spend_puzzle = coin_solution.puzzle_reveal
        spend_solution = coin_solution.solution
        result = spend_puzzle.run(spend_solution)
        sum_additions = 0
        exclude_it = True
        for sexp in result.as_iter():
            items = sexp.as_python()
            opcode = ConditionOpcode(items[0])
            if opcode in [ConditionOpcode.AGG_SIG_ME, ConditionOpcode.AGG_SIG, ConditionOpcode.CREATE_ANNOUNCEMENT]:
                exclude_it = False
            if opcode == ConditionOpcode.CREATE_COIN:
                sum_additions += int.from_bytes(items[2],"big")
        if (not exclude_it) | (sum_additions <= save_amount):
            new_coin_solutions.append({
                "coin": {
                    "parent_coin_info": str(coin_solution.coin.parent_coin_info),
                    "puzzle_hash": str(coin_solution.coin.puzzle_hash),
                    "amount": str(coin_solution.coin.amount)
                },
                "puzzle_reveal": str(coin_solution.puzzle_reveal),
                "solution": str(coin_solution.solution)
            })
    new_spend = SpendBundle.from_json_dict({
        "aggregated_signature": str(transaction.aggregated_signature),
        "coin_solutions": new_coin_solutions
    })
    return new_spend, new_spend.name()
