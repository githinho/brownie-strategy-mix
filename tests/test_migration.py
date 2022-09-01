# TODO: Add tests that show proper migration of the strategy to a newer one
#       Use another copy of the strategy to simulate the migration
#       Show that nothing is lost!

import pytest


def test_migration(
    chain,
    token,
    vault,
    strategy,
    amount,
    Strategy,
    strategist,
    gov,
    user,
    RELATIVE_APPROX,
    poolToken,
    reward_token,
):
    # Deposit to the vault and harvest
    token.approve(vault.address, amount, {"from": user})
    vault.deposit(amount, {"from": user})
    chain.sleep(1)
    strategy.harvest()
    assert pytest.approx(strategy.estimatedTotalAssets(), rel=RELATIVE_APPROX) == amount

    # migrate to a new strategy
    new_strategy = strategist.deploy(Strategy, vault, "0x777777c9898D384F785Ee44Acfe945efDFf5f3E0", "0x507fA343d0A90786d86C7cd885f5C49263A91FF4", poolToken, reward_token, "StrategyMorphoUSDT2")
    # new_strategy = strategist.deploy(Strategy, vault, "0x8888882f8f843896699869179fB6E4f7e3B58888", "0x930f1b46e1D081Ec1524efD95752bE3eCe51EF67", poolToken, reward_token, "StrategyMorphoUSDT2")
    vault.migrateStrategy(strategy, new_strategy, {"from": gov})
    assert (
        pytest.approx(new_strategy.estimatedTotalAssets(), rel=RELATIVE_APPROX)
        == amount
    )
