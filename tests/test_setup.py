import brownie
from brownie import Contract, Wei
import pytest


def test_strategy_setup(
    token, reward_token, vault, strategy, trade_factory, sushiswap_address, uniswap_address
):
    uint256_max = 2**256 - 1
    assert token.allowance(strategy.address, strategy.morpho()) == uint256_max

    # assert that the default router
    assert strategy.currentV2Router() == sushiswap_address

    # COMP max allowance is uint96
    uint96_max = 2**96 - 1
    # assert allowance for comp to Sushiswap, Uniswap and ySwap
    assert reward_token.allowance(strategy.address, sushiswap_address) == uint96_max
    assert reward_token.allowance(strategy.address, uniswap_address) == uint96_max
    assert reward_token.allowance(strategy.address, trade_factory.address) == uint96_max
    assert strategy.tradeFactory() == trade_factory.address


def test_toggle_swap_router(strategy, sushiswap_address, uniswap_address):
    assert strategy.currentV2Router() == sushiswap_address
    strategy.setToggleV2Router()
    assert strategy.currentV2Router() == uniswap_address


def test_set_min_reward_token_to_claim(strategy):
    assert strategy.minRewardTokenToClaimOrSell() == Wei("0.1 ether")
    new_value = Wei("11.11 ether")
    strategy.setMinRewardTokenToClaimOrSell(new_value)
    assert strategy.minRewardTokenToClaimOrSell() == new_value


def test_set_max_gas_for_matching(strategy):
    assert strategy.maxGasForMatching() == 100000
    new_value = Wei("0.05212 ether")
    strategy.setMaxGasForMatching(new_value)
    assert strategy.maxGasForMatching() == new_value
