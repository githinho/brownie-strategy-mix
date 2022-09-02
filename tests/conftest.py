import pytest
from brownie import config
from brownie import Contract


@pytest.fixture
def gov(accounts):
    yield accounts.at("0xFEB4acf3df3cDEA7399794D0869ef76A6EfAff52", force=True)


@pytest.fixture
def user(accounts):
    yield accounts[0]


@pytest.fixture
def rewards(accounts):
    yield accounts[1]


@pytest.fixture
def guardian(accounts):
    yield accounts[2]


@pytest.fixture
def management(accounts):
    yield accounts[3]


@pytest.fixture
def strategist(accounts):
    yield accounts[4]


@pytest.fixture
def keeper(accounts):
    yield accounts[5]


@pytest.fixture
def token():
    # token_address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"  # USDT
    # token_address = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"  # USDC
    token_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"  # WETH
    yield Contract(token_address)


@pytest.fixture
def token_whale(accounts):
    # yield accounts.at( "0x5754284f345afc66a98fbb0a0afe71e0f007b949", force=True)  # Tether Treasury
    # yield accounts.at("0x55fe002aeff02f77364de339a1292923a15844b8", force=True) #Reserve = Circle
    yield accounts.at("0x2f0b23f53734252bda2277357e97e1517d6b042a", force=True)  # Maker


@pytest.fixture
def usdt():
    token_address = "0xdAC17F958D2ee523a2206206994597C13D831ec7"  # USDT
    yield Contract(token_address)


@pytest.fixture
def usdt_amount(accounts, usdt, user):
    amount = 10_000 * 10 ** usdt.decimals()
    # In order to get some funds for the token you are about to use,
    # it impersonate an exchange address to use it's funds.
    reserve = accounts.at("0x5754284f345afc66a98fbb0a0afe71e0f007b949", force=True)
    usdt.transfer(user, amount, {"from": reserve})
    yield amount


@pytest.fixture
def amount(accounts, token, user, token_whale):
    amount = 10_000 * 10 ** token.decimals()
    # In order to get some funds for the token you are about to use,
    # it impersonate an exchange address to use it's funds.
    reserve = token_whale
    token.transfer(user, amount, {"from": reserve})
    yield amount


@pytest.fixture
def poolToken():
    # token_address = "0x3Ed3B47Dd13EC9a98b44e6204A523E766B225811"  # aUSDT
    # token_address = "0xBcca60bB61934080951369a648Fb03DF4F96263C" #aUSDC
    token_address = "0x030bA81f1c18d280636F32af80b9AAd02Cf0854e"  # aWETH
    yield Contract(token_address)


@pytest.fixture
def weth():
    token_address = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    yield Contract(token_address)


@pytest.fixture
def weth_amount(user, weth):
    weth_amount = 10 ** weth.decimals()
    user.transfer(weth, weth_amount)
    yield weth_amount


@pytest.fixture
def vault(pm, gov, rewards, guardian, management, token):
    Vault = pm(config["dependencies"][0]).Vault
    vault = guardian.deploy(Vault)
    vault.initialize(token, gov, rewards, "", "", guardian, management)
    vault.setDepositLimit(2**256 - 1, {"from": gov})
    vault.setManagement(management, {"from": gov})
    yield vault


@pytest.fixture
def strategy(strategist, keeper, vault, poolToken, Strategy, gov):
    strategy = strategist.deploy(Strategy, vault, poolToken, "StrategyMorphoAaveUSDT")
    strategy.setKeeper(keeper)
    vault.addStrategy(strategy, 10_000, 0, 2**256 - 1, 1_000, {"from": gov})
    yield strategy


@pytest.fixture(scope="session")
def RELATIVE_APPROX():
    yield 1e-5


# Function scoped isolation fixture to enable xdist.
# Snapshots the chain before each test and reverts after test completion.
@pytest.fixture(scope="function", autouse=True)
def shared_setup(fn_isolation):
    pass
