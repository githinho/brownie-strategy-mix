import brownie
from brownie import Contract
import pytest


def aave_test_operation(
    chain, accounts, token, vault, strategy, user, strategist, amount, RELATIVE_APPROX
):
    # Deposit to the vault
    user_balance_before = token.balanceOf(user)
    token.approve(vault.address, amount, {"from": user})
    vault.deposit(amount, {"from": user})
    assert token.balanceOf(vault.address) == amount

    # harvest
    chain.sleep(1)
    strategy.harvest()
    assert pytest.approx(strategy.estimatedTotalAssets(), rel=RELATIVE_APPROX) == amount

    # tend()
    strategy.tend()

    # withdrawal
    vault.withdraw({"from": user})
    assert (
        pytest.approx(token.balanceOf(user), rel=RELATIVE_APPROX) == user_balance_before
    )


def aave_test_emergency_exit(
    chain, accounts, token, vault, strategy, user, strategist, amount, RELATIVE_APPROX
):
    # Deposit to the vault
    token.approve(vault.address, amount, {"from": user})
    vault.deposit(amount, {"from": user})
    chain.sleep(1)
    strategy.harvest()
    assert pytest.approx(strategy.estimatedTotalAssets(), rel=RELATIVE_APPROX) == amount

    # set emergency and exit
    strategy.setEmergencyExit()
    chain.sleep(1)
    strategy.harvest()
    assert strategy.estimatedTotalAssets() < amount


def aave_test_profitable_harvest(
    chain,
    accounts,
    token,
    vault,
    strategy,
    user,
    strategist,
    gov,
    amount,
    RELATIVE_APPROX,
    token_whale,
):
    # Deposit to the vault
    token.approve(vault.address, amount, {"from": user})
    vault.deposit(amount, {"from": user})
    assert token.balanceOf(vault.address) == amount

    # Harvest 1: Send funds through the strategy
    chain.sleep(1)
    strategy.harvest()
    assert pytest.approx(strategy.estimatedTotalAssets(), rel=RELATIVE_APPROX) == amount
    before_pps = vault.pricePerShare()

    # increase lending interest
    chain.sleep(100 * 24 * 3600)
    chain.mine(1)

    # Harvest 2: Realize profit
    chain.sleep(1)
    strategy.harvest()
    chain.sleep(3600 * 6)  # 6 hrs needed for profits to unlock
    chain.mine(1)
    profit = token.balanceOf(vault.address)  # Profits go to vault

    assert strategy.estimatedTotalAssets() + profit > amount
    assert vault.pricePerShare() > before_pps


def aave_test_change_debt(
    chain, gov, token, vault, strategy, user, strategist, amount, RELATIVE_APPROX
):
    # Deposit to the vault and harvest
    token.approve(vault.address, amount, {"from": user})
    vault.deposit(amount, {"from": user})
    vault.updateStrategyDebtRatio(strategy.address, 5_000, {"from": gov})
    chain.sleep(1)
    strategy.harvest()
    half = int(amount / 2)

    assert pytest.approx(strategy.estimatedTotalAssets(), rel=RELATIVE_APPROX) == half

    vault.updateStrategyDebtRatio(strategy.address, 10_000, {"from": gov})
    chain.sleep(1)
    strategy.harvest()
    assert pytest.approx(strategy.estimatedTotalAssets(), rel=RELATIVE_APPROX) == amount

    # In order to pass this tests, you will need to implement prepareReturn.
    # TODO: uncomment the following lines.
    vault.updateStrategyDebtRatio(strategy.address, 5_000, {"from": gov})
    chain.sleep(1)
    strategy.harvest()
    assert pytest.approx(strategy.estimatedTotalAssets(), rel=RELATIVE_APPROX) == half


def test_sweep(gov, vault, strategy, token, user, amount, weth, weth_amount):
    # Strategy want token doesn't work
    token.transfer(strategy, amount, {"from": user})
    assert token.address == strategy.want()
    assert token.balanceOf(strategy) > 0
    with brownie.reverts("!want"):
        strategy.sweep(token, {"from": gov})

    # Vault share token doesn't work
    with brownie.reverts("!shares"):
        strategy.sweep(vault.address, {"from": gov})

    # TODO: If you add protected tokens to the strategy.
    # Protected token doesn't work
    # with brownie.reverts("!protected"):
    #     strategy.sweep(strategy.protectedToken(), {"from": gov})

    before_balance = weth.balanceOf(gov)
    weth.transfer(strategy, weth_amount, {"from": user})
    assert weth.address != strategy.want()
    assert weth.balanceOf(user) == 0
    strategy.sweep(weth, {"from": gov})
    assert weth.balanceOf(gov) == weth_amount + before_balance


def test_triggers(
    chain, gov, vault, strategy, token, amount, user, weth, weth_amount, strategist
):
    # Deposit to the vault and harvest
    token.approve(vault.address, amount, {"from": user})
    vault.deposit(amount, {"from": user})
    vault.updateStrategyDebtRatio(strategy.address, 5_000, {"from": gov})
    chain.sleep(1)
    strategy.harvest()

    strategy.harvestTrigger(0)
    strategy.tendTrigger(0)
