// SPDX-License-Identifier: GPL-3.0
pragma solidity 0.6.12;
pragma experimental ABIEncoderV2;

interface ILens {
    function getCurrentSupplyBalanceInOf(
        address _poolTokenAddress,
        address _user
    )
        external
        view
        returns (
            uint256 balanceOnPool,
            uint256 balanceInP2P,
            uint256 totalBalance
        );
}
