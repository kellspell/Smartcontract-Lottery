#from eth_account import account
from brownie import (
    accounts,
    network,
    config,
    MockV3Aggregator,
    VRFCoordinatorMock,
    LinkToken,
    interfaces,
    Contract,
)
FORK_lOCAL_ENVIRONMENTS = ["mainnet=fork", "mainnet-folk-dev"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-kellspell"]


def get_account(index=None, id=None):
    # we have three ways of setup our network here
    # accounts[0]
    # accounts.add("env")
    # accounts.load("id")
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)

    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORK_lOCAL_ENVIRONMENTS
    ):
        return account[0]

    return accounts.add(config["wallets"]["from_key"])


contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
    "vrf_coordinator": VRFCoordinatorMock,
    "link_token": LinkToken,
}


def get_contract(contract_name):

    """This function will grab the contract adddress from the brownie config
    if defined , otherwise, it deploy a mock version of that contract , and return
    that mock contract.

    Args:
        contract_name (String)

    Returns:
        brownie.network.contract.ProjectContract: The most recemtly deployed version of this contract,
        MockV3Aggregator[-1]
    """

    contract_type = contract_to_mock[contract_name]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        contract_address = config["networks"][network.show_active()][contract_name]
        # address
        # ABI
        contract = Contract.from_abi(
            contract_type._name, contract_address, contract_type.abi
        )  # MockV3Aggregator has already the abi and name with it
    return contract


DECIMALS = 8
INICIAL_VALUE = 200000000000


def deploy_mocks(decimals=DECIMALS, inicial_value=INICIAL_VALUE):
    account = get_account()
    MockV3Aggregator.deploy(decimals, inicial_value, {"from": account})
    link_token = LinkToken.deploy({"from": account})
    VRFCoordinatorMock.deploy(link_token.address, {"from": account})
    print("Deployed")


def fund_with_link(
    contract_address, account=None, link_token=None, amount=10000000000000000
):  # 0.1 Link
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    tx = link_token.transfer(contract_address, amount, {"from": account})
    #link_token_contract = interface.LinkTokenInterface(link_token.address)
    #tx = link_token_contract.transfer(contract_address, amount, {"from": account})
    
    tx.wait(1)
    print("Funded contract")
    return tx
